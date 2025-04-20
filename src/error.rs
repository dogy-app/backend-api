//! This module contains the main error handling for all routes and axum handlers.
//!
//! This follows the rust-10x production code convention for handling errors.
//! See [this video](https://www.youtube.com/watch?v=j-VQCYP7wyw) to know more about it.
//!
//! Moreover, this module contains error handling for both server errors and client errors.

use std::sync::Arc;

use crate::{
    middleware::auth,
    service::{assistant::daily_challenges, users},
};
use axum::{extract::rejection::JsonRejection, http::StatusCode, response::IntoResponse, Json};
use derive_more::From;
use serde::Serialize;
use serde_with::{serde_as, DisplayFromStr};
use tracing::debug;

/// Boilerplate Result Type from rust-10x style convention. This result type is used by all axum
/// handlers.
pub type Result<T> = core::result::Result<T, Error>;

/// This type is used when you have a JSON request body as it can potentially throw
/// [`JsonRejection`], which is not handled by [`serde_json`].
///
/// See this example when using in a handler:
/// ```rust
/// async fn update_user_base(payload: PayloadJson<UserUpdate>) -> Result<Json<UserUpdate>> {
///     Json(user) = payload?;
///     println!("User ID: {user.id}");
/// }
/// ```
pub type PayloadJson<T> = core::result::Result<Json<T>, JsonRejection>;

/// Main Error Types for all axum handlers.
///
/// This contains all of the error types from all other modules.
/// In particular, the [`From`] trait is used to cast the error types from other modules to this.
/// Moreover, This handles the following:
/// - Error types from [serde_json][`serde_json::Error`], if an axum handler fails to serialize to
/// JSON as a response.
/// - JSON Rejection errors from [axum][`axum::extract::rejection::JsonRejection`], if an axum handler
/// fails to deserialize the request body to JSON. This occurs if the consumer of the API sends a
/// malformed/incorrect format for the request body.
/// - Error types from [auth][`auth::Error`].
/// - Error types from [users][`users::Error`].
///
#[serde_as]
#[derive(Debug, Serialize, From, strum_macros::AsRefStr)]
#[serde(tag = "type", content = "data")]
pub enum Error {
    // Internals
    /// This error will occur if an environment variable imported using
    /// `get_env()` is missing when the server starts up.
    /// If you want to import env variables with default value such as `PORT`, you can use
    /// `get_env_opt()` instead.
    ConfigMissingEnv(&'static str),

    // Modules
    /// Errors from [`auth::Error`]
    #[from]
    Auth(auth::Error),

    /// Errors from [`auth::Error`]
    #[from]
    User(users::Error),

    #[from]
    DailyChallenge(daily_challenges::Error),

    /// Errors from [`serde_json::Error`]
    #[from]
    SerdeJson(#[serde_as(as = "DisplayFromStr")] serde_json::Error),

    /// This error will occur if a request body is not valid JSON.
    #[from]
    JsonRejection(#[serde_as(as = "DisplayFromStr")] JsonRejection),
}

/// This is the error type that is returned to the client.
///
/// This error type can only be retrieved after mapping a server error to a client error.
#[derive(Debug, Serialize, strum_macros::AsRefStr)]
#[serde(tag = "code", content = "details")]
#[allow(non_camel_case_types)]
pub enum ClientError {
    // Auth
    /// This error will occur if the request does not contain an `Authorization` header.
    MISSING_AUTH_HEADER,

    /// This error will occur if the request does not contain a `Bearer` prefix in the
    /// `Authorization` header.
    NO_BEARER_PREFIX,

    /// This error will occur if the token in the `Authorization` header is invalid.
    INVALID_CREDENTIALS,

    /// This error will occur if a server error is not mapped to client error.
    SERVICE_ERROR,

    // User
    /// This error will occur if a user attempts to create a user that already exists in the
    /// database.
    USER_ALREADY_EXISTS,

    /// This error will occur if an authenticated user is not found in the database.
    USER_NOT_FOUND { user_id: String },

    // Invalid Request Body
    /// This error will occur if a request body is not valid JSON or it did not meet the
    /// requirements for serialization.
    INVALID_REQUEST_BODY(String),
}

impl IntoResponse for Error {
    /// Initializes errors to client errors with `INTERNAL_SERVER_ERROR` and injects the server error into the
    /// request through the use of extensions.
    ///
    /// The injected server error will be retrieved later on and will be mapped to a proper client
    /// error.
    fn into_response(self) -> axum::response::Response {
        debug!("{self:?}");

        let mut response = StatusCode::INTERNAL_SERVER_ERROR.into_response();

        response.extensions_mut().insert(Arc::new(self));
        response
    }
}

impl Error {
    /// Maps the injected server error of type [`Error`] to a client error [`ClientError`].
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
                StatusCode::UNPROCESSABLE_ENTITY,
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
