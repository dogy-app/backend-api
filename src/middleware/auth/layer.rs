use axum::http::StatusCode;
use axum::{extract::Request, http::header, middleware::Next, response::Response};
use uuid::Uuid;

use super::core::authenticate_user;

#[derive(Clone)]
pub struct CurrentUser {
    pub user_id: String,
    pub role: Option<String>,
    pub internal_id: Option<Uuid>,
}

pub async fn auth_middleware(mut req: Request, next: Next) -> Result<Response, StatusCode> {
    // Retrieve authorization header
    println!("--> Authenticating user...");
    let auth_header = req
        .headers()
        .get(header::AUTHORIZATION)
        .and_then(|header| header.to_str().ok())
        .ok_or(StatusCode::BAD_REQUEST)
        .unwrap()
        .strip_prefix("Bearer ")
        .ok_or(StatusCode::BAD_REQUEST)
        .unwrap();

    if let Ok(current_user) = authenticate_user(auth_header) {
        req.extensions_mut().insert(current_user);
        Ok(next.run(req).await)
    } else {
        Err(StatusCode::UNAUTHORIZED)
    }
}

pub async fn get_internal_id(mut req: Request, next: Next) -> Result<Response, StatusCode> {
    let current_user = req
        .extensions_mut()
        .get::<CurrentUser>()
        .unwrap()
        .to_owned();

    let query = "SELECT id FROM users where external_id = $1";

    if let Some(_) = current_user.internal_id {
        req.extensions_mut()
            .remove::<CurrentUser>()
            .insert(CurrentUser {
                user_id: current_user.user_id.clone(),
                role: current_user.role.clone(),
                internal_id: Some(internal_id),
            });
        Ok(next.run(req).await)
    } else {
        Err(StatusCode::UNAUTHORIZED)
    }
}
