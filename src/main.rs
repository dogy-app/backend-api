//! Main entry point for the Dogy API server.
//! This module sets up the server, database connection, and routes.
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

/// This is the application state that is shared across all axum handlers.
///
/// Remember to not put sensitive information (eg. env var), large objects (files/embedding), or
/// request-specific data in here (auth bearer token).
#[derive(Clone)]
struct AppState {
    /// Postgres Database connection pool. Be sure that the `DATABASE_URL` from Neon does not have
    /// **Connection Pooling** enabled.
    db: Arc<PgPool>,
}

/// Main function to start the server.
///
/// Tracing is initialized based on the build profile.
/// `debug` for debug builds and `info` for release builds.
/// For debug builds, the logs are printed in a human-readable format.
/// For release builds, the logs are printed in a JSON format.
///
/// Config is also loaded from the `.env` file using [`load_config()`].
#[tokio::main]
pub async fn main() -> Result<()> {
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

    // Loads config from .env file.
    let config = load_config();

    info!("Connecting to database...");
    let pool = PgPoolOptions::new()
        .max_connections(10)
        .connect(&config.DATABASE_URL)
        .await
        .expect("Failed to create PgPool.");
    info!("Connected to database.");

    sqlx::migrate!("./migrations").run(&pool).await.unwrap();
    //sqlx::migrate!("./migrations").undo(&pool, 1).await.unwrap();
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
