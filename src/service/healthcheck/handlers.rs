use axum::Json;
use serde_json::{json, Value};

pub async fn healthcheck_v1() -> Json<Value> {
    Json(json!({ "message": "Welcome to Dogy API v1" }))
}
