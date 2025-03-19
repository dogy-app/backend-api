use chrono::{DateTime, NaiveDate, Utc};
use serde::{Deserialize, Serialize};
use sqlx::{FromRow, Type};
use uuid::Uuid;

#[derive(Serialize, Type, Deserialize)]
#[serde(rename_all = "lowercase")]
#[sqlx(type_name = "gender", rename_all = "lowercase")]
pub enum Gender {
    Male,
    Female,
}

#[derive(Serialize, Type, Deserialize)]
#[serde(rename_all = "lowercase")]
#[sqlx(type_name = "subscription_type", rename_all = "lowercase")]
pub enum SubscriptionType {
    Active,
    Inactive,
    Unknown,
}

#[allow(dead_code)]
#[derive(Serialize, Deserialize, FromRow, Type)]
#[serde(rename_all = "camelCase")]
pub struct User {
    #[serde(skip)]
    pub id: Uuid,
    #[serde(skip)]
    pub created_at: DateTime<Utc>,
    #[serde(skip)]
    pub updated_at: DateTime<Utc>,
    #[serde(rename = "externalID", skip_deserializing)]
    pub external_id: String,
    pub name: String,
    pub timezone: String,
    pub gender: Gender,
    pub has_onboarded: bool,
}

#[allow(dead_code)]
#[derive(Serialize, Deserialize, FromRow, Type)]
#[serde(rename_all = "camelCase")]
pub struct UserNotification {
    pub enabled: bool,
    pub is_registered: bool,
    pub daily_enabled: bool,
    pub playtime_enabled: bool,
}

#[allow(dead_code)]
#[derive(Serialize, Deserialize, FromRow, Type)]
#[serde(rename_all = "camelCase")]
pub struct UserSubscription {
    pub trial_start_date: Option<NaiveDate>,
    pub subscription_type: SubscriptionType,
    pub is_trial_mode: bool,
}

#[derive(Serialize, Deserialize)]
pub struct FullUser {
    #[serde(flatten)]
    pub base: User,
    pub subscription: UserSubscription,
    pub notifications: UserNotification,
}
