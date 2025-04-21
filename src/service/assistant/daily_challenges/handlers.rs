use axum::{
    extract::{Path, State},
    Extension, Json,
};
use reqwest::Client;
use serde::Serialize;
use uuid::Uuid;

use crate::{
    config::load_config,
    middleware::auth::layer::CurrentUser,
    service::{
        assistant::daily_challenges::store::{EXCLUDE_PAST_CHALLENGES_PROMPT, PET_INFO_PROMPT},
        pets::{models::FullPet, store::retrieve_full_pet},
    },
    AppState,
};

use crate::Result;

use super::store::{
    retrieve_past_challenges, retrieve_timezone_from_user, save_daily_challenge,
    verify_daily_challenge_existence, DAILY_CHALLENGE_PROMPT,
};

#[derive(Serialize)]
pub struct DailyChallengeResponse {
    pub id: Uuid,
    pub challenge: String,
}

pub async fn create_challenge_from_ai(
    pet: FullPet,
    past_challenges: Option<&Vec<String>>,
) -> String {
    let pet_as_str = serde_json::to_string(&pet).unwrap();
    let prompt = match past_challenges {
        Some(_) => {
            format!(
                "{}\n\n{}\n{}\n\n{}",
                DAILY_CHALLENGE_PROMPT, PET_INFO_PROMPT, pet_as_str, EXCLUDE_PAST_CHALLENGES_PROMPT,
            )
        }
        None => {
            format!(
                "{}\n\n{}\n{}",
                DAILY_CHALLENGE_PROMPT, PET_INFO_PROMPT, pet_as_str
            )
        }
    };

    let past_challenges_as_str = past_challenges
        .map(|challenges| challenges.join("\n"))
        .unwrap_or_else(|| "I have no past daily challenges.".to_string());

    let config = load_config();

    // TODO: Turn this into a shared client instead of creating a new client every time.
    let client = Client::new();
    let response = client
        .post(&config.AZURE_OPENAI_ENDPOINT)
        .header("api-key", &config.AZURE_OPENAI_KEY)
        .header("Content-Type", "application/json")
        .body(
            serde_json::json!({
                "messages": [
                    {
                        "role": "system",
                        "content": [{
                            "type": "text",
                            "text": prompt
                        }]
                    },
                    {
                        "role": "user",
                        "content": [{
                            "type": "text",
                            "text": past_challenges_as_str
                        }]
                    }
                ],
                "temperature": 0.7,
            })
            .to_string(),
        )
        .send()
        .await
        .unwrap();

    response
        .json::<serde_json::Value>()
        .await
        .unwrap()
        .get("choices")
        .and_then(|choices| choices.get(0))
        .and_then(|choice| choice.get("message"))
        .and_then(|message| message.get("content"))
        .and_then(|content| content.as_str())
        .map(|content| content.to_string())
        .unwrap_or_else(|| "No challenge generated".to_string())
}

pub async fn create_daily_challenge(
    Extension(current_user): Extension<CurrentUser>,
    State(state): State<AppState>,
    Path(pet_id): Path<Uuid>,
) -> Result<Json<DailyChallengeResponse>> {
    let internal_user_id = current_user.internal_id.unwrap();
    let conn = &*state.db;
    let timezone = retrieve_timezone_from_user(conn, internal_user_id).await?;

    let mut txn1 = conn.begin().await.unwrap();
    verify_daily_challenge_existence(&mut txn1, internal_user_id, &timezone).await?;
    txn1.commit().await.unwrap();

    let pet = retrieve_full_pet(conn, pet_id).await;
    let past_challenges = retrieve_past_challenges(conn, internal_user_id).await?;
    let past_challenges_as_opt = (!past_challenges.is_empty()).then_some(&past_challenges);

    let generated_challenge = create_challenge_from_ai(pet, past_challenges_as_opt).await;

    let mut txn = conn.begin().await.unwrap();
    let challenge_id = save_daily_challenge(
        &mut txn,
        internal_user_id,
        timezone,
        generated_challenge.as_ref(),
    )
    .await?;
    txn.commit().await.unwrap();

    Ok(Json(DailyChallengeResponse {
        id: challenge_id,
        challenge: generated_challenge,
    }))
}
