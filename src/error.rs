use std::sync::Arc;

use crate::middleware::auth;
use axum::{http::StatusCode, response::IntoResponse};
use derive_more::From;
use serde::Serialize;
use serde_with::serde_as;
use tracing::debug;

pub type Result<T> = core::result::Result<T, Error>;

#[serde_as]
#[derive(Debug, Serialize, From, strum_macros::AsRefStr)]
#[serde(tag = "type", content = "data")]
pub enum Error {
    // Internals
    ConfigMissingEnv(&'static str),

    // Modules
    #[from]
    Auth(auth::Error),
}

#[derive(Debug, Serialize, strum_macros::AsRefStr)]
#[serde(tag = "code", content = "detail")]
#[allow(non_camel_case_types)]
pub enum ClientError {
    // Auth
    MISSING_AUTH_HEADER,
    NO_BEARER_PREFIX,
    INVALID_CREDENTIALS,
    SERVICE_ERROR,
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
