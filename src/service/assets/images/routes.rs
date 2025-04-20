use axum::{extract::DefaultBodyLimit, routing::post, Router};

use super::handlers::{delete_image, upload_image};

async fn images_routes() -> Router {
    Router::new()
        .route("/", post(upload_image).delete(delete_image))
        .route_layer(DefaultBodyLimit::max(20971520)) // Maximum upload file size of 20MB.
}

pub async fn root_images_routes() -> Router {
    Router::new().nest("/images", images_routes().await)
}
