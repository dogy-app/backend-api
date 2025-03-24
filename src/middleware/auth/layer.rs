use axum::extract::State;
use axum::http::StatusCode;
use axum::{extract::Request, http::header, middleware::Next, response::Response};
use uuid::Uuid;

use crate::AppState;

use super::core::authenticate_user;

#[derive(Clone, Debug)]
pub struct CurrentUser {
    pub user_id: String,
    #[allow(dead_code)]
    pub role: Option<String>,
    pub internal_id: Option<Uuid>,
}

pub async fn auth_middleware(mut req: Request, next: Next) -> Result<Response, StatusCode> {
    // Retrieve authorization header
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

pub async fn get_internal_id(
    State(state): State<AppState>,
    mut req: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    let current_user = req.extensions_mut().get::<CurrentUser>().unwrap().clone();

    let query = "SELECT id FROM users where external_id = $1";
    let internal_id: Option<Uuid> = sqlx::query_scalar(query)
        .bind(&current_user.user_id)
        .fetch_one(&*state.db)
        .await
        .unwrap_or(None);

    if internal_id.is_some() {
        let updated_user = CurrentUser {
            internal_id,
            ..current_user
        };
        println!("Current user: {:?}", updated_user);
        req.extensions_mut().insert(updated_user);
        Ok(next.run(req).await)
    } else {
        Err(StatusCode::UNAUTHORIZED)
    }
}
