use axum::{middleware, routing::post, Router};

use crate::{middleware::auth::layer::auth_middleware, AppState};

use super::handlers::create_pet;

async fn pet_routes() -> Router<AppState> {
    Router::new()
        .route("/", post(create_pet))
        .route_layer(middleware::from_fn(auth_middleware))
}

pub async fn root_pet_routes() -> Router<AppState> {
    Router::new().nest("/pets", pet_routes().await)
}
