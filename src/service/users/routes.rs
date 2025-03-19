use axum::{middleware, routing::get, Router};

use crate::middleware::auth::layer::auth_middleware;

use super::handlers::{create_user, get_user};

pub async fn user_routes() -> Router {
    Router::new()
        .route("/", get(get_user).post(create_user))
        .route_layer(middleware::from_fn(auth_middleware))
}

pub async fn root_user_routes() -> Router {
    Router::new().nest("/users", user_routes().await)
}
