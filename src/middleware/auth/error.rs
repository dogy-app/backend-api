pub type Result<T> = core::result::Result<T, Error>;

#[derive(Debug)]
pub enum Error {
    InvalidDecodingKey,
    CannotDecodeToken,
    MissingAuthHeader,
    NoBearerPrefix,
}
