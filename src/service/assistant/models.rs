use serde::{Deserialize, Serialize};
use sqlx::prelude::{FromRow, Type};
use uuid::Uuid;

#[derive(Deserialize)]
pub struct Thread {
    pub title: String,
}

#[derive(Debug, Serialize, FromRow, Type)]
pub struct DbThread {
    pub thread_id: Uuid,
    pub thread_title: String,
}

#[allow(dead_code)]
#[derive(Debug, Serialize)]
pub enum MessageType {
    User,
    Bot,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Message {
    pub id: Uuid,
    pub is_bot_message: bool,
    pub text: String,
    pub title: MessageType, // Indicator above a chat whether its a user or bot (AI).
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ThreadResponse {
    pub thread_id: Uuid,
    pub user_id: String,
    pub title: String,
    pub messages: Vec<Message>,
}

#[derive(Serialize)]
pub struct AllThreadResponse {
    pub threads: Vec<ThreadResponse>,
}
