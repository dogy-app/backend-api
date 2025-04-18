//! This module contains the axum middleware layer for authentication.
use axum::extract::State;
use axum::{extract::Request, http::header, middleware::Next, response::Response};
use tracing::debug;
use uuid::Uuid;

use crate::AppState;

use super::core::authenticate_user;
use super::Error as AuthError;
use crate::{Error, Result};

/// Represents the metadata about the current user.
///
/// This is passed throughout the middlewares and also handlers.
#[derive(Clone, Debug)]
pub struct CurrentUser {
    /// Clerk User ID of the current user.
    pub user_id: String,

    /// Clerk Role (normally None for regular users) of the current user.
    #[allow(dead_code)]
    pub role: Option<String>,

    /// Database User ID of the current user. Initially, this should be None as we will retrieve
    /// the internal ID from the database after authentication occurs.
    pub internal_id: Option<Uuid>,
}

/// Axum middleware for authentication.
///
/// Accepts `Authorization` header from a request and validates it.
/// Afterwards, it'll decode the JWT token and inject the user's details
/// into the request.
pub async fn auth_middleware(mut req: Request, next: Next) -> Result<Response> {
    // Retrieve authorization header
    let auth_header = req
        .headers()
        .get(header::AUTHORIZATION)
        .and_then(|header| header.to_str().ok())
        .ok_or(Error::Auth(AuthError::MissingAuthHeader))?
        .strip_prefix("Bearer ")
        .ok_or(Error::Auth(AuthError::NoBearerPrefix))?;

    let current_user = authenticate_user(auth_header)?;

    // Inject the current user's details for both request and response.
    // Injecting it to response is necessary in order for it to be extracted later on in
    // response_mapper or logging middleware.
    req.extensions_mut().insert(current_user.clone());
    let mut res = next.run(req).await;
    res.extensions_mut().insert(current_user);
    Ok(res)
}

/// Axum middleware for retrieving the internal ID for the current user.
///
/// If it passes through authentication but fails to retrieve the internal ID of the user,
/// it'll simply return a [`AuthError::UserNotFound`] error.
pub async fn get_internal_id(
    State(state): State<AppState>,
    mut req: Request,
    next: Next,
) -> Result<Response> {
    let current_user = req.extensions_mut().get::<CurrentUser>().unwrap().clone();

    let query = "SELECT id FROM users where external_id = $1";
    let user_id = &current_user.user_id;
    let internal_id: Uuid = sqlx::query_scalar(query)
        .bind(user_id)
        .fetch_one(&*state.db)
        .await
        .unwrap_or(None)
        .ok_or(Error::Auth(AuthError::UserNotFound {
            user_id: user_id.to_string(),
        }))?;

    let updated_user = CurrentUser {
        internal_id: Some(internal_id),
        ..current_user
    };
    debug!("Current user: {:?}", updated_user);
    req.extensions_mut().insert(updated_user);
    Ok(next.run(req).await)
}
