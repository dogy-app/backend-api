use chrono::{NaiveDate, NaiveDateTime};
use serde::{Deserialize, Deserializer, Serialize};
use sqlx::{FromRow, Type};
use uuid::Uuid;

#[derive(Serialize, Type, Deserialize)]
#[serde(rename_all = "lowercase")]
#[sqlx(type_name = "user_gender", rename_all = "lowercase")]
pub enum Gender {
    Male,
    Female,
    Other,
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
#[derive(Serialize, Deserialize, Type)]
#[serde(rename_all = "camelCase")]
pub struct User {
    #[serde(rename = "externalID", skip_deserializing)]
    pub external_id: String,
    pub name: String,
    pub timezone: String,
    pub gender: Gender,
    pub has_onboarded: bool,
}

#[derive(Serialize, Deserialize, Type, FromRow)]
#[serde(rename_all = "camelCase")]
pub struct UserUpdate {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub timezone: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gender: Option<Gender>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub has_onboarded: Option<bool>,
}

#[allow(dead_code)]
#[derive(Serialize, Deserialize, Type)]
#[serde(rename_all = "camelCase")]
pub struct UserNotification {
    pub enabled: bool,
    pub is_registered: bool,
    pub daily_enabled: bool,
    pub playtime_enabled: bool,
}

#[derive(Serialize, Deserialize, Type, FromRow)]
#[serde(rename_all = "camelCase")]
pub struct UserNotificationUpdate {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub enabled: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub is_registered: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub daily_enabled: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub playtime_enabled: Option<bool>,
}

#[allow(dead_code)]
#[derive(Serialize, Deserialize, Type)]
#[serde(rename_all = "camelCase")]
pub struct UserSubscription {
    pub trial_start_date: Option<NaiveDate>,
    pub subscription_type: SubscriptionType,
    pub is_trial_mode: bool,
}

#[derive(Serialize, Deserialize, Type, FromRow)]
#[serde(rename_all = "camelCase")]
pub struct UserSubscriptionUpdate {
    #[serde(
        skip_serializing_if = "Option::is_none",
        default,
        deserialize_with = "deserialize_some"
    )]
    pub trial_start_date: Option<Option<NaiveDate>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub subscription_type: Option<SubscriptionType>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub is_trial_mode: Option<bool>,
}

fn deserialize_some<'de, T, D>(deserializer: D) -> std::result::Result<Option<T>, D::Error>
where
    T: Deserialize<'de>,
    D: Deserializer<'de>,
{
    Deserialize::deserialize(deserializer).map(Some)
}

#[derive(Serialize, Deserialize)]
pub struct FullUser {
    #[serde(flatten)]
    pub base: User,
    pub subscription: UserSubscription,
    pub notifications: UserNotification,
}

// This struct should only be used when retrieving from the database and not for
// serializing/deserializing.
#[derive(Type, FromRow)]
pub struct JoinedFullUser {
    pub id: Uuid,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
    pub name: String,
    pub external_id: String,
    pub timezone: String,
    pub gender: Gender,
    pub has_onboarded: bool,
    pub trial_start_date: Option<NaiveDate>,
    pub subscription_type: SubscriptionType,
    pub is_trial_mode: bool,
    pub enabled: bool,
    pub is_registered: bool,
    pub daily_enabled: bool,
    pub playtime_enabled: bool,
}
