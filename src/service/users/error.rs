//! This module contains the error types for users in axum handlers.
//!
//! This follows the rust-10x production code convention for handling errors.
//! See [this video](https://www.youtube.com/watch?v=j-VQCYP7wyw) to know more about it.

use serde::Serialize;
use serde_with::{serde_as, DisplayFromStr};
use sqlx::Error as SqlxError;

//pub type Result<T> = core::result::Result<T, Error>;

/// Error types for users in axum handlers.
#[serde_as]
#[derive(Debug, Serialize)]
pub enum Error {
    /// This error will occur if a user tries to create a new user with an existing `user_id`.
    UserAlreadyExists,

    /// This error wraps [`sqlx::Error`] for the error codes that haven't been map.
    ///
    /// Serves as a fallback error if in case an unknown error with no mapping occurs.
    Sqlx(#[serde_as(as = "DisplayFromStr")] sqlx::Error),
}

impl From<SqlxError> for Error {
    /// Maps generic sqlx errors into a user-defined error type. Otherwise, just return generic
    /// sqlx error as a `String`.
    fn from(err: SqlxError) -> Self {
        if let SqlxError::Database(db_err) = &err {
            if let Some(code) = db_err.code() {
                match code.as_ref() {
                    "23505" => Error::UserAlreadyExists,
                    //"23503" => Error::Sqlx(SqlxError::Database(DatabaseError::ForeignKeyViolation)),
                    _ => Error::Sqlx(err),
                }
            } else {
                Error::Sqlx(err)
            }
        } else {
            Error::Sqlx(err)
        }
    }
}

// Boilerplate for Errors
impl core::fmt::Display for Error {
    fn fmt(&self, fmt: &mut core::fmt::Formatter) -> core::result::Result<(), core::fmt::Error> {
        write!(fmt, "{self:?}")
    }
}

impl std::error::Error for Error {}
