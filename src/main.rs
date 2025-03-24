use std::sync::Arc;

use axum::{routing::get, Json, Router};
use config::load_config;
use serde_json::json;
use service::{
    assistant::routes::root_assistant_routes, pets::routes::root_pet_routes,
    users::routes::root_user_routes,
};
use sqlx::{postgres::PgPoolOptions, PgPool};
use tracing_subscriber::EnvFilter;

pub use self::error::{Error, Result};

mod config;
mod error;
mod middleware;
mod service;

#[derive(Clone)]
struct AppState {
    db: Arc<PgPool>,
}

#[tokio::main]
async fn main() -> std::result::Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt()
        .without_time()
        .with_target(false)
        .with_env_filter(EnvFilter::from_default_env())
        .init();

    let config = load_config();
    println!("Port: {}", config.PORT);
    println!("--> Connecting to database...");
    let pool = PgPoolOptions::new()
        .max_connections(10)
        .connect(&config.DATABASE_URL)
        .await
        .expect("Failed to create PgPool.");
    println!("--> Connected to database.");

    //sqlx::migrate!("./migrations").run(&pool).await?;
    let shared_state = AppState { db: Arc::new(pool) };

    let app = Router::new()
        .route(
            "/",
            get(|| async { Json(json!({ "message": "Welcome to Dogy API" })) }),
        )
        .nest("/api/v1", root_user_routes(shared_state.clone()).await)
        .nest("/api/v1", root_pet_routes(shared_state.clone()).await)
        .nest("/api/v1", root_assistant_routes(shared_state.clone()).await)
        .with_state(shared_state)
        .nest(
            "/api/v1",
            service::healthcheck::routes::healthcheck_routes().await,
        );

    // run our app with hyper, listening globally on port 8080
    let listener = tokio::net::TcpListener::bind(format!("0.0.0.0:{}", config.PORT))
        .await
        .unwrap();
    axum::serve(listener, app).await.unwrap();

    Ok(())
}
