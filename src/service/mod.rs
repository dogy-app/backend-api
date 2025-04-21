use assets::root_assets_routes;
use assistant::routes::root_assistant_routes;
use axum::Router;
use pets::routes::root_pet_routes;
use users::routes::root_user_routes;

use crate::AppState;

pub mod assets;
pub mod assistant;
pub mod healthcheck;
pub mod pets;
pub mod users;

pub async fn api_v1_routes(shared_state: AppState) -> Router {
    Router::new()
        .merge(root_user_routes(shared_state.clone()).await)
        .merge(root_pet_routes(shared_state.clone()).await)
        .merge(root_assistant_routes(shared_state.clone()).await)
        .with_state(shared_state)
        .merge(root_assets_routes().await)
        .merge(healthcheck::routes::healthcheck_routes().await)
}
