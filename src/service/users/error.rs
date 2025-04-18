use serde::Serialize;
use serde_with::{serde_as, DisplayFromStr};
use sqlx::Error as SqlxError;

pub type Result<T> = core::result::Result<T, Error>;

#[serde_as]
#[derive(Debug, Serialize)]
pub enum Error {
    UserAlreadyExists,
    Sqlx(#[serde_as(as = "DisplayFromStr")] sqlx::Error),
}

impl From<SqlxError> for Error {
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

impl core::fmt::Display for Error {
    fn fmt(&self, fmt: &mut core::fmt::Formatter) -> core::result::Result<(), core::fmt::Error> {
        write!(fmt, "{self:?}")
    }
}

impl std::error::Error for Error {}
