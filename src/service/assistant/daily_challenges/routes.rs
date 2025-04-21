use axum::{middleware, routing::post, Router};

use crate::{
    middleware::auth::layer::{auth_middleware, get_internal_id},
    AppState,
};

use super::handlers::create_daily_challenge;

async fn daily_challenge_routes(app_state: AppState) -> Router<AppState> {
    Router::new()
        .route(
            "/{pet_id}",
            post(create_daily_challenge).route_layer(middleware::from_fn_with_state(
                app_state.clone(),
                get_internal_id,
            )),
        )
        .route_layer(middleware::from_fn(auth_middleware))
}

pub async fn root_daily_challenge_routes(app_state: AppState) -> Router<AppState> {
    Router::new().nest("/challenges/daily", daily_challenge_routes(app_state).await)
}
