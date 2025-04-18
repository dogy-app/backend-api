use std::sync::Arc;

use crate::{
    middleware::{auth::layer::CurrentUser, log::core::ClientErrorResponse},
    Error,
};
use axum::{
    http::{Method, Uri},
    response::{IntoResponse, Response},
    Json,
};
use serde_json::to_value;

use super::core::log_request;

// Logging and Response Mapper Middleware
pub async fn log_middleware(uri: Uri, req_method: Method, res: Response) -> Response {
    let current_user = res.extensions().get::<CurrentUser>();
    let web_error = res.extensions().get::<Arc<Error>>().map(Arc::as_ref);
    let client_status_error = web_error.map(|se| se.client_status_error());

    let error_response = client_status_error
        .as_ref()
        .map(|(status_code, client_error)| {
            let client_error = to_value(client_error).ok();
            let code = client_error.as_ref().and_then(|v| v.get("code"));
            let detail = client_error.as_ref().and_then(|v| v.get("details"));

            let client_error_body = ClientErrorResponse {
                status: "error".to_string(),
                code: code.cloned(),
                details: detail.cloned(),
            };

            //error!(code = ?client_error_body.code, status = "error", detail = ?client_error_body.detail, "Client error response");

            (*status_code, Json(client_error_body)).into_response()
        });

    let client_error = client_status_error.unzip().1;
    let _ = log_request(current_user, uri, req_method, web_error, client_error);

    error_response.unwrap_or(res)
}
