use axum::Router;
use images::routes::root_images_routes;

pub mod images;

pub async fn root_assets_routes() -> Router {
    Router::new().nest("/assets", root_images_routes().await)
}
