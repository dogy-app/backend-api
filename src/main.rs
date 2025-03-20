use std::sync::Arc;

use axum::{routing::get, Json, Router};
use config::load_config;
use serde_json::json;
use service::users::routes::root_user_routes;
use sqlx::{postgres::PgPoolOptions, Connection, PgConnection, PgPool};
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

    //let mut conn = PgConnection::connect(&config.DATABASE_URL).await.unwrap();
    //sqlx::migrate!("./migrations").run(&mut conn).await?;
    //let row = sqlx::query("SELECT 1 + 1 AS result")
    //    .fetch_one(&mut conn)
    //    .await?;
    //
    //let sum: i32 = row.get("result");
    //
    //println!("result: {}", sum);
    //
    let shared_state = AppState { db: Arc::new(pool) };

    let app = Router::new()
        .route(
            "/",
            get(|| async { Json(json!({ "message": "Welcome to Dogy API" })) }),
        )
        .nest("/api/v1", root_user_routes(shared_state.clone()).await)
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
