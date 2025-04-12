use crate::error::{ClientError, Error, Result};
use axum::http::Uri;
use reqwest::Method;
use serde::Serialize;
use serde_json::Value;
use tracing::{error, info};
use uuid::Uuid;

#[derive(Debug, Serialize)]
pub struct ClientErrorResponse {
    pub status: String,
    pub code: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub detail: Option<Value>,
}

pub fn log_request(
    user_id: Option<String>,
    req_path: Uri,
    req_method: Method,
    web_error: Option<&Error>,
    client_error: Option<ClientError>,
) -> Result<()> {
    let req_id = Uuid::now_v7();
    let req_path_str = req_path.to_string();

    let error_details = serde_json::to_value(web_error)
        .ok()
        .and_then(|mut v| v.get_mut("details").map(|v| v.take()));

    match web_error {
        Some(_) => {
            error!(
            id = %req_id,
            user_id = "None",
            path = %req_path_str,
            method = %req_method.as_str(),
            client_error_code = %client_error.map(|e| e.as_ref().to_string()).unwrap(),
            error_code = %web_error.map(|e| e.to_string()).unwrap(),
            "{error_details:?}"
            );
        }
        None => {
            info!(
                id = %req_id,
                user_id = "None",
                path = %req_path_str,
                method = %req_method.as_str()
            );
        }
    }

    Ok(())
}
