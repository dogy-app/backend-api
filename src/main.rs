use std::sync::Arc;
use tracing::info;

use axum::{middleware as mw, routing::get, Json, Router};
use config::load_config;
use middleware::log::layer::log_middleware;
use serde_json::json;
use service::api_v1_routes;
use sqlx::{postgres::PgPoolOptions, PgPool};
use tracing_subscriber::EnvFilter;

pub use self::error::{Error, PayloadJson, Result};

mod config;
mod error;
mod middleware;
mod service;

#[derive(Clone)]
struct AppState {
    db: Arc<PgPool>,
}

#[tokio::main]
async fn main() -> Result<()> {
    #[cfg(debug_assertions)]
    tracing_subscriber::fmt()
        .with_target(false)
        .with_env_filter(EnvFilter::new("debug"))
        .init();

    #[cfg(not(debug_assertions))]
    tracing_subscriber::fmt()
        .json()
        .with_target(false)
        .with_env_filter(EnvFilter::new("info"))
        .init();

    info!("Starting Server");
    let config = load_config();
    info!("Connecting to database...");
    let pool = PgPoolOptions::new()
        .max_connections(10)
        .connect(&config.DATABASE_URL)
        .await
        .expect("Failed to create PgPool.");
    info!("Connected to database.");

    //sqlx::migrate!("./migrations").run(&pool).await?;
    let shared_state = AppState { db: Arc::new(pool) };

    let app = Router::new()
        .route(
            "/",
            get(|| async { Json(json!({ "message": "Welcome to Dogy API" })) }),
        )
        .nest("/api/v1", api_v1_routes(shared_state.clone()).await)
        .layer(mw::map_response(log_middleware));

    // run our app with hyper, listening globally on port 8080
    let listener = tokio::net::TcpListener::bind(format!("0.0.0.0:{}", config.PORT))
        .await
        .unwrap();
    axum::serve(listener, app).await.unwrap();

    Ok(())
}
