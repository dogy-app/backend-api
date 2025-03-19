use super::handlers::healthcheck_v1;
use axum::{routing::get, Router};

pub async fn healthcheck_routes() -> Router {
    Router::new().route("/", get(healthcheck_v1))
}
