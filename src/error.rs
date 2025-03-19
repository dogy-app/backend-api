use axum::http::StatusCode;

pub type Result<T> = core::result::Result<T, Error>;

#[derive(Debug)]
pub struct APIError {
    pub status_code: StatusCode,
    pub message: String,
}

#[derive(Debug)]
pub enum Error {
    ConfigMissingEnv(&'static str),
    AuthError(APIError),
}
