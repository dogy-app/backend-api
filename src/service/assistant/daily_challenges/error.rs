use derive_more::From;
use serde::Serialize;
use serde_with::{serde_as, DisplayFromStr};
use uuid::Uuid;

//pub type Result<T> = std::result::Result<T, Error>;

#[serde_as]
#[derive(Debug, From, Serialize, strum_macros::AsRefStr)]
pub enum Error {
    ChallengeAlreadyCompleted {
        challenge_id: Uuid,
    },
    MissingTimezoneForUser,

    #[from]
    Sqlx(#[serde_as(as = "DisplayFromStr")] sqlx::Error),
}

// Boilerplate for Errors
impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> core::result::Result<(), core::fmt::Error> {
        write!(f, "{self:?}")
    }
}

impl std::error::Error for Error {}
