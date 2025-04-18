use std::sync::Arc;

use crate::{middleware::auth, service::users};
use axum::{extract::rejection::JsonRejection, http::StatusCode, response::IntoResponse, Json};
use derive_more::From;
use serde::Serialize;
use serde_with::{serde_as, DisplayFromStr};
use tracing::debug;

pub type Result<T> = core::result::Result<T, Error>;
pub type PayloadJson<T> = core::result::Result<Json<T>, JsonRejection>;

#[serde_as]
#[derive(Debug, Serialize, From, strum_macros::AsRefStr)]
#[serde(tag = "type", content = "data")]
pub enum Error {
    // Internals
    ConfigMissingEnv(&'static str),

    // Modules
    #[from]
    Auth(auth::Error),

    #[from]
    User(users::Error),

    #[from]
    SerdeJson(#[serde_as(as = "DisplayFromStr")] serde_json::Error),

    #[from]
    JsonRejection(#[serde_as(as = "DisplayFromStr")] JsonRejection),
}

#[derive(Debug, Serialize, strum_macros::AsRefStr)]
#[serde(tag = "code", content = "details")]
#[allow(non_camel_case_types)]
pub enum ClientError {
    // Auth
    MISSING_AUTH_HEADER,
    NO_BEARER_PREFIX,
    INVALID_CREDENTIALS,
    SERVICE_ERROR,

    // User
    USER_ALREADY_EXISTS,
    USER_NOT_FOUND { user_id: String },

    // Invalid Request Body
    INVALID_REQUEST_BODY(String),
}

impl IntoResponse for Error {
    fn into_response(self) -> axum::response::Response {
        debug!("{self:?}");

        let mut response = StatusCode::INTERNAL_SERVER_ERROR.into_response();

        response.extensions_mut().insert(Arc::new(self));
        response
    }
}

impl Error {
    pub fn client_status_error(&self) -> (StatusCode, ClientError) {
        match self {
            Error::Auth(auth::Error::MissingAuthHeader) => {
                (StatusCode::UNAUTHORIZED, ClientError::MISSING_AUTH_HEADER)
            }
            Error::Auth(auth::Error::NoBearerPrefix) => {
                (StatusCode::UNAUTHORIZED, ClientError::NO_BEARER_PREFIX)
            }
            Error::Auth(auth::Error::InvalidToken) => {
                (StatusCode::UNAUTHORIZED, ClientError::INVALID_CREDENTIALS)
            }
            Error::Auth(auth::Error::UserNotFound { user_id }) => (
                StatusCode::NOT_FOUND,
                ClientError::USER_NOT_FOUND {
                    user_id: user_id.to_string(),
                },
            ),
            Error::User(users::Error::UserAlreadyExists) => {
                (StatusCode::CONFLICT, ClientError::USER_ALREADY_EXISTS)
            }
            Error::JsonRejection(req_body) => (
                StatusCode::BAD_REQUEST,
                ClientError::INVALID_REQUEST_BODY(req_body.to_string()),
            ),
            _ => (
                StatusCode::INTERNAL_SERVER_ERROR,
                ClientError::SERVICE_ERROR,
            ),
        }
    }
}

// Boilerplate for Errors
impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> core::result::Result<(), core::fmt::Error> {
        write!(f, "{self:?}")
    }
}

impl std::error::Error for Error {}
