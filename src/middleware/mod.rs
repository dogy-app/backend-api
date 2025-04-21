pub mod auth;
pub mod log;

#[cfg(test)]
mod test {
    use crate::config::load_config;
    use crate::AppState;
    use axum::Router;
    use sqlx::postgres::PgPoolOptions;
    use std::sync::Arc;
    use testcontainers::ContainerAsync;
    use testcontainers_modules::postgres::Postgres;
    use testcontainers_modules::testcontainers::{runners::AsyncRunner, ImageExt};

    #[cfg(test)]
    pub fn setup_test_router() -> Router {
        dotenv::from_filename(".env.test").unwrap();
        let _ = load_config();

        Router::new().route(
            "/",
            axum::routing::get(|| async { "Middleware test succeeded" }),
        )
    }

    #[cfg(test)]
    pub async fn setup_test_db() -> (AppState, ContainerAsync<Postgres>) {
        let container_instance = Postgres::default()
            .with_init_sql(
                "CREATE ROLE web_backend_public WITH LOGIN PASSWORD 'testpassword';
                 CREATE DATABASE \"web-backend\";
                "
                .to_string()
                .into_bytes(),
            )
            .with_name("sheape/postgis-uuidv7")
            .with_tag("1.0.0")
            .start()
            .await
            .unwrap();

        let host_port = container_instance.get_host_port_ipv4(5432).await.unwrap();

        let pool = PgPoolOptions::new()
            .max_connections(1)
            .connect(&format!(
                "postgres://web_backend_public:testpassword@localhost:{}/web-backend",
                host_port
            ))
            .await
            .expect("Failed to create PgPool.");

        let admin_pool = PgPoolOptions::new()
            .max_connections(1)
            .connect(&format!(
                "postgres://postgres:postgres@localhost:{}/web-backend",
                host_port
            ))
            .await
            .expect("Failed to create PgPool.");

        sqlx::migrate!("./migrations")
            .run(&admin_pool)
            .await
            .unwrap();

        (AppState { db: Arc::new(pool) }, container_instance)
    }
}
