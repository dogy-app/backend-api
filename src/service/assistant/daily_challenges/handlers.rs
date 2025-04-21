use axum::{
    extract::{Path, State},
    Extension, Json,
};
use chrono::{DateTime, Datelike, Duration, NaiveDate, Utc, Weekday};
use chrono_tz::Tz;
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
    retrieve_daily_challenge_streaks, retrieve_past_challenges, retrieve_timezone_from_user,
    save_daily_challenge, verify_daily_challenge_existence, DAILY_CHALLENGE_PROMPT,
};

#[derive(Serialize)]
pub struct DailyChallengeResponse {
    pub id: Uuid,
    pub challenge: String,
}

#[derive(Serialize)]
pub struct DailyActivity {
    pub day: String,
    pub completed: bool,
}

#[derive(Serialize)]
pub struct DailyChallengeStreaks {
    pub current_streak: u16, // Maximum of 65535 days. Dont think anyone will live for more than 179 years.
    pub longest_streak: u16,
    pub total_streak_days: u16,
    pub weekly_activity: Vec<DailyActivity>,
}

async fn create_challenge_from_ai(pet: FullPet, past_challenges: Option<&Vec<String>>) -> String {
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

pub async fn get_daily_challenge_streak(
    Extension(current_user): Extension<CurrentUser>,
    State(state): State<AppState>,
) -> Result<Json<DailyChallengeStreaks>> {
    let conn = &*state.db;
    let internal_user_id = current_user.internal_id.unwrap();
    let mut txn = conn.begin().await.unwrap();

    let timezone = retrieve_timezone_from_user(&mut *txn, internal_user_id).await?;

    let daily_streak_dates =
        retrieve_daily_challenge_streaks(&mut txn, internal_user_id, &timezone).await?;

    txn.commit().await.unwrap();

    let total_streak_days = daily_streak_dates.len() as u16;
    let tz: Tz = timezone.parse().unwrap();
    let today = Utc::now().with_timezone(&tz);
    let (current_streak, longest_streak) =
        retrieve_current_longest_streak(&daily_streak_dates, today);
    let weekly_activity = retrieve_weekly_activity(&daily_streak_dates, today);

    Ok(Json(DailyChallengeStreaks {
        weekly_activity,
        current_streak,
        longest_streak,
        total_streak_days,
    }))
}

fn retrieve_current_longest_streak(dates: &Vec<NaiveDate>, today: DateTime<Tz>) -> (u16, u16) {
    let (mut current_streak, mut longest_streak) = (0_u16, 0_u16);
    let mut streak = 0;
    let mut prev_day: Option<NaiveDate> = None;

    for date in dates {
        if let Some(prev) = prev_day {
            if *date == prev + Duration::days(1) {
                streak += 1;
            } else {
                streak = 1;
            }
        } else {
            streak = 1;
        }

        if *date == today.date_naive() {
            current_streak = streak;
        }

        if streak > longest_streak {
            longest_streak = streak;
        }

        prev_day = Some(*date);
    }

    (current_streak, longest_streak)
}

fn retrieve_weekly_activity(dates: &[NaiveDate], today: DateTime<Tz>) -> Vec<DailyActivity> {
    let mut weekly_activity: Vec<DailyActivity> = Vec::new();
    for i in 0..7 {
        let date = today - Duration::days(6 - i);
        let weekday = date.weekday();
        let short_day = match weekday {
            Weekday::Mon => "M",
            Weekday::Tue => "T",
            Weekday::Wed => "W",
            Weekday::Thu => "Th",
            Weekday::Fri => "F",
            Weekday::Sat => "Sat",
            Weekday::Sun => "Sun",
        };

        let completed = dates.contains(&date.date_naive());
        weekly_activity.push(DailyActivity {
            day: short_day.to_string(),
            completed,
        });
    }

    weekly_activity
}
