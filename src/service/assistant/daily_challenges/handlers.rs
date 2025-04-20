use axum::{
    extract::{Path, State},
    Extension, Json,
};
use serde::Serialize;
use uuid::Uuid;

use crate::{
    middleware::auth::layer::CurrentUser,
    service::pets::{models::FullPet, store::retrieve_full_pet},
    AppState,
};

use crate::Result;

use super::store::{retrieve_timezone_from_user, DAILY_CHALLENGE_PROMPT};

#[derive(Serialize)]
pub struct DailyChallengeResponse {
    pub id: Uuid,
    pub challenge: String,
}

//pub async fn create_challenge_from_ai(pet: FullPet, past_challenges: Option<Vec<String>>) {
//    let pet_as_str = serde_json::to_string(&pet).unwrap();
//    let prompt = format!("{}\n\n{}\n\n{}", DAILY_CHALLENGE_PROMPT,);
//}

pub async fn create_daily_challenge(
    Extension(current_user): Extension<CurrentUser>,
    State(state): State<AppState>,
    Path(pet_id): Path<Uuid>,
) -> Result<Json<DailyChallengeResponse>> {
    let internal_user_id = current_user.internal_id.unwrap();
    let conn = &*state.db;
    let mut txn = conn.begin().await.map_err(super::Error::from)?;
    let timezone = retrieve_timezone_from_user(&mut *txn, internal_user_id).await?;

    let pet = retrieve_full_pet(&mut *txn, pet_id).await;

    txn.commit().await.map_err(super::Error::from)?;

    Ok(Json(DailyChallengeResponse {
        id: Uuid::now_v7(),
        challenge: "nice".to_string(),
    }))
}
