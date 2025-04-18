use derive_more::From;
use serde::Serialize;
use serde_with::serde_as;

pub type Result<T> = core::result::Result<T, Error>;

#[serde_as]
#[derive(Debug, Serialize, From)]
#[serde(tag = "code", content = "details")]
pub enum Error {
    // Internals
    InvalidDecodingKey,
    InvalidToken,

    // Middleware-related
    MissingAuthHeader,
    NoBearerPrefix,

    // User-related
    UserNotFound { user_id: String },

    // Generic
    AuthFailed,
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> core::result::Result<(), core::fmt::Error> {
        write!(f, "{self:?}")
    }
}

impl std::error::Error for Error {}
