use axum::{
    middleware,
    routing::{get, post},
    Router,
};

use crate::{
    middleware::auth::layer::{auth_middleware, get_internal_id},
    AppState,
};

use super::handlers::{create_daily_challenge, get_daily_challenge_streak};

async fn daily_challenge_routes(app_state: AppState) -> Router<AppState> {
    Router::new()
        .route("/{pet_id}", post(create_daily_challenge))
        .route("/", get(get_daily_challenge_streak))
        .layer(middleware::from_fn_with_state(
            app_state.clone(),
            get_internal_id,
        ))
        .layer(middleware::from_fn(auth_middleware))
}

pub async fn root_daily_challenge_routes(app_state: AppState) -> Router<AppState> {
    Router::new().nest("/challenges/daily", daily_challenge_routes(app_state).await)
}
