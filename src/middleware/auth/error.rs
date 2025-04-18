//! This module contains the error types about authentication.
use derive_more::From;
use serde::Serialize;
use serde_with::serde_as;

/// Result Type for Auth.
pub type Result<T> = core::result::Result<T, Error>;

/// Error types for Authentication.
#[serde_as]
#[derive(Debug, Serialize, From)]
#[serde(tag = "code", content = "details")]
pub enum Error {
    // Internals
    /// This error will occur if the decoding key is invalid.
    ///
    /// Namely, if either the decoding key which is `RSA_MODULUS` is empty or if its invalid.
    InvalidDecodingKey,

    /// This error will occur if the token provider in the `Authorization` header is invalid after
    /// decoding.
    InvalidToken,

    // Middleware-related
    /// This error will occur if the request does not contain an `Authorization` header.
    MissingAuthHeader,

    /// This error will occur if the request does not contain a `Bearer` prefix in the
    /// `Authorization` header.
    NoBearerPrefix,

    // User-related
    /// This error will occur if an authenticated user is not found in the database.
    UserNotFound { user_id: String },
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> core::result::Result<(), core::fmt::Error> {
        write!(f, "{self:?}")
    }
}

impl std::error::Error for Error {}
