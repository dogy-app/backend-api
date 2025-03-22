use axum::{
    extract::{Path, State},
    Extension, Json,
};
use futures::future::join_all;
use reqwest::Client;
use serde_json::{json, Value};
use sqlx::{query, query_as};
use tokio::task;
use uuid::Uuid;

use crate::{
    middleware::auth::layer::CurrentUser, service::assistant::models::MessageType, AppState,
};

use super::models::{AllThreadResponse, DbThread, Message, Thread, ThreadResponse};

pub async fn link_user_to_thread(
    Extension(current_user): Extension<CurrentUser>,
    State(state): State<AppState>,
    Path(thread_id): Path<Uuid>,
    Json(thread): Json<Thread>,
) -> Json<Value> {
    let conn = &*state.db;
    query(
        "INSERT INTO user_assistant_threads (user_id, thread_id, thread_title)
        VALUES ($1, $2, $3);",
    )
    .bind(current_user.internal_id.unwrap())
    .bind(thread_id)
    .bind(thread.title)
    .execute(conn)
    .await
    .unwrap();

    Json(json!({
        "message": format!("Thread {} successfully linked to user {}", thread_id, current_user.user_id)
    }))
}

pub async fn update_thread_title(
    State(state): State<AppState>,
    Path(thread_id): Path<Uuid>,
    Json(thread): Json<Thread>,
) -> Json<Value> {
    let conn = &*state.db;
    query(
        r#"UPDATE user_assistant_threads
        SET thread_title = $2
        WHERE thread_id = $1;
        "#,
    )
    .bind(thread_id)
    .bind(&thread.title)
    .execute(conn)
    .await
    .unwrap();

    Json(json!({
        "message": format!("Thread {} successfully updated title to {}", thread_id, thread.title)
    }))
}

pub async fn unlink_thread_from_user(
    Extension(current_user): Extension<CurrentUser>,
    State(state): State<AppState>,
    Path(thread_id): Path<Uuid>,
) -> Json<Value> {
    let conn = &*state.db;
    query("DELETE FROM user_assistant_threads WHERE thread_id = $1;")
        .bind(thread_id)
        .execute(conn)
        .await
        .unwrap();

    Json(json!({
        "message": format!("Thread {} has been successfully unlinked from user {}.", thread_id, current_user.user_id)
    }))
}

async fn retrieve_thread_history(client: &Client, thread_id: Uuid) -> Vec<Message> {
    let res: serde_json::Value = client
        .get(format!(
            "https://dogy-assistant.azurewebsites.net/threads/{}",
            thread_id
        ))
        .send()
        .await
        .unwrap()
        .json()
        .await
        .unwrap();

    let mut parsed_messages: Vec<Message> = vec![];

    if let Some(messages) = res
        .get("values")
        .and_then(|v| v.get("messages"))
        .and_then(|m| m.as_array())
    {
        for message in messages {
            match message.get("type").unwrap().as_str().unwrap() {
                "human" => parsed_messages.push(Message {
                    id: message
                        .get("id")
                        .unwrap()
                        .as_str()
                        .unwrap()
                        .parse()
                        .unwrap(),
                    is_bot_message: false,
                    text: message.get("content").unwrap().as_array().unwrap()[0]
                        .get("text")
                        .unwrap()
                        .as_str()
                        .unwrap()
                        .to_string(),
                    title: MessageType::User,
                }),
                "ai" => parsed_messages.push(Message {
                    id: message
                        .get("id")
                        .unwrap()
                        .as_str()
                        .unwrap()
                        .strip_prefix("run-")
                        .unwrap()
                        .parse()
                        .unwrap(),
                    is_bot_message: true,
                    text: message.get("content").unwrap().to_string(),
                    title: MessageType::Bot,
                }),
                _ => (),
            }
        }
    }

    parsed_messages
}

pub async fn get_all_threads_from_user(
    Extension(current_user): Extension<CurrentUser>,
    State(state): State<AppState>,
) -> Json<AllThreadResponse> {
    let conn = &*state.db;
    let db_threads = query_as::<_, DbThread>(
        r#"
        SELECT thread_id, thread_title
        FROM user_assistant_threads
        WHERE user_id = $1;
    "#,
    )
    .bind(current_user.internal_id.unwrap())
    .fetch_all(conn)
    .await
    .unwrap();

    let client = Client::new();
    let threads: Vec<_> = db_threads
        .into_iter()
        .map(|thread| {
            let client = client.clone();
            let user_id = current_user.user_id.clone();
            task::spawn(async move {
                let messages = retrieve_thread_history(&client, thread.thread_id).await;
                ThreadResponse {
                    thread_id: thread.thread_id,
                    user_id,
                    title: thread.thread_title,
                    messages,
                }
            })
        })
        .collect();

    let results = join_all(threads).await;
    let thread_responses = results.into_iter().map(|r| r.unwrap()).collect::<Vec<_>>();

    Json(AllThreadResponse {
        threads: thread_responses,
    })
}
