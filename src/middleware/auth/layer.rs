//! This module contains the axum middleware layer for authentication.
use axum::extract::State;
use axum::{extract::Request, http::header, middleware::Next, response::Response};
use tracing::debug;
use uuid::Uuid;

use crate::AppState;

use super::core::authenticate_user;
use super::Error as AuthError;
use crate::{Error, Result};

/// Represents the metadata about the current user.
///
/// This is passed throughout the middlewares and also handlers.
#[derive(Clone, Debug, PartialEq)]
pub struct CurrentUser {
    /// Clerk User ID of the current user.
    pub user_id: String,

    /// Clerk Role (normally None for regular users) of the current user.
    #[allow(dead_code)]
    pub role: Option<String>,

    /// Database User ID of the current user. Initially, this should be None as we will retrieve
    /// the internal ID from the database after authentication occurs.
    pub internal_id: Option<Uuid>,
}

/// Axum middleware for authentication.
///
/// Accepts `Authorization` header from a request and validates it.
/// Afterwards, it'll decode the JWT token and inject the user's details
/// into the request.
pub async fn auth_middleware(mut req: Request, next: Next) -> Result<Response> {
    // Retrieve authorization header
    let auth_header = req
        .headers()
        .get(header::AUTHORIZATION)
        .and_then(|header| header.to_str().ok())
        .ok_or(Error::Auth(AuthError::MissingAuthHeader))?
        .strip_prefix("Bearer ")
        .ok_or(Error::Auth(AuthError::NoBearerPrefix))?;

    let current_user = authenticate_user(auth_header)?;

    // Inject the current user's details for both request and response.
    // Injecting it to response is necessary in order for it to be extracted later on in
    // response_mapper or logging middleware.
    req.extensions_mut().insert(current_user.clone());
    let mut res = next.run(req).await;
    res.extensions_mut().insert(current_user);
    Ok(res)
}

/// Axum middleware for retrieving the internal ID for the current user.
///
/// If it passes through authentication but fails to retrieve the internal ID of the user,
/// it'll simply return a [`AuthError::UserNotFound`] error.
pub async fn get_internal_id(
    State(state): State<AppState>,
    mut req: Request,
    next: Next,
) -> Result<Response> {
    let current_user = req.extensions_mut().get::<CurrentUser>().unwrap().clone();

    let query = "SELECT id FROM users where external_id = $1";
    let user_id = &current_user.user_id;
    let internal_id: Uuid = sqlx::query_scalar(query)
        .bind(user_id)
        .fetch_one(&*state.db)
        .await
        .unwrap_or(None)
        .ok_or(Error::Auth(AuthError::UserNotFound {
            user_id: user_id.to_string(),
        }))?;

    let updated_user = CurrentUser {
        internal_id: Some(internal_id),
        ..current_user
    };
    debug!("Current user: {:?}", &updated_user);
    req.extensions_mut().insert(updated_user);
    Ok(next.run(req).await)
}

#[cfg(test)]
mod test {
    use super::*;
    use crate::middleware::{log::layer::log_middleware, test::*};
    use axum::middleware;
    use axum_test::TestServer;
    use reqwest::StatusCode;
    use serde_json::json;
    use std::env;
    use testcontainers::ContainerAsync;
    use testcontainers_modules::postgres::Postgres;

    #[cfg(test)]
    fn setup_test_server_with_auth() -> TestServer {
        let test_route = setup_test_router()
            .route_layer(middleware::from_fn(auth_middleware))
            .layer(middleware::map_response(log_middleware));

        TestServer::new(test_route).unwrap()
    }

    #[cfg(test)]
    fn setup_test_server_with_assert_user() -> TestServer {
        let test_route = setup_test_router()
            .layer(middleware::from_fn(assert_current_user_in_extensions_mw))
            .route_layer(middleware::from_fn(auth_middleware))
            .layer(middleware::map_response(log_middleware));

        TestServer::new(test_route).unwrap()
    }

    #[cfg(test)]
    async fn setup_test_server_with_state(
        create_user: bool,
    ) -> (TestServer, ContainerAsync<Postgres>) {
        let (state, container) = setup_test_db().await;
        if create_user {
            sqlx::query(
                r#"INSERT INTO users (name, external_id, timezone, gender, has_onboarded)
                VALUES ('Test User', 'user_2ruHSXCzfIRreR2tpttVQBl512a', 'Europe/Stockholm', 'male', true);
                "#,
            )
            .execute(&*state.db)
            .await
            .unwrap();
        }
        let test_route = setup_test_router()
            .layer(middleware::from_fn(assert_current_user_full_in_ext_mw))
            .layer(middleware::from_fn_with_state(state, get_internal_id))
            .layer(middleware::from_fn(auth_middleware))
            .layer(middleware::map_response(log_middleware));

        println!(
            "host: {}",
            container.get_host_port_ipv4(5432).await.unwrap()
        );

        (TestServer::new(test_route).unwrap(), container)
    }

    #[cfg(test)]
    async fn assert_current_user_in_extensions_mw(req: Request, next: Next) -> Result<Response> {
        let current_user = req.extensions().get::<CurrentUser>().unwrap();
        assert_eq!(current_user.user_id, "user_2ruHSXCzfIRreR2tpttVQBl512a");
        assert_eq!(current_user.role, None);
        assert_eq!(current_user.internal_id, None);
        Ok(next.run(req).await)
    }

    #[cfg(test)]
    async fn assert_current_user_full_in_ext_mw(req: Request, next: Next) -> Result<Response> {
        let current_user = req.extensions().get::<CurrentUser>().unwrap();
        assert_eq!(current_user.user_id, "user_2ruHSXCzfIRreR2tpttVQBl512a");
        assert_eq!(current_user.role, None);
        assert!(current_user.internal_id.is_some());
        Ok(next.run(req).await)
    }

    #[tokio::test]
    async fn test_auth_middleware_ok() {
        let app = setup_test_server_with_auth();
        let _ = dotenv::from_filename(".env.test");
        let jwt_token = env::var("JWT_TOKEN").unwrap();

        let response = app
            .get("/")
            .add_header("Authorization", format!("Bearer {}", jwt_token))
            .await;

        response.assert_status(StatusCode::OK);
        response.assert_text("Middleware test succeeded");
    }

    #[tokio::test]
    async fn test_auth_middleware_missing_auth_header_err() {
        let app = setup_test_server_with_auth();

        let response = app.get("/").await;

        response.assert_status(StatusCode::UNAUTHORIZED);
        response.assert_header("content-type", "application/json");
        response.assert_json(&json!({
            "status": "error",
            "code": "MISSING_AUTH_HEADER"
        }));
    }

    #[tokio::test]
    async fn test_auth_middleware_no_bearer_prefix_err() {
        let app = setup_test_server_with_auth();

        let response = app.get("/").add_header("Authorization", "some_token").await;

        response.assert_status(StatusCode::UNAUTHORIZED);
        response.assert_header("content-type", "application/json");
        response.assert_json(&json!({
            "status": "error",
            "code": "NO_BEARER_PREFIX"
        }));
    }

    #[tokio::test]
    async fn test_auth_middleware_invalid_token_err() {
        let app = setup_test_server_with_auth();

        let response = app
            .get("/")
            .add_header("Authorization", "Bearer invalid_token")
            .await;

        response.assert_status(StatusCode::UNAUTHORIZED);
        response.assert_header("content-type", "application/json");
        response.assert_json(&json!({
            "status": "error",
            "code": "INVALID_CREDENTIALS"
        }));
    }

    #[tokio::test]
    async fn test_auth_middleware_current_user_ext_ok() {
        let app = setup_test_server_with_assert_user();
        let _ = dotenv::from_filename(".env.test");
        let jwt_token = env::var("JWT_TOKEN").unwrap();

        let response = app
            .get("/")
            .add_header("Authorization", format!("Bearer {}", jwt_token))
            .await;

        response.assert_status(StatusCode::OK);
        response.assert_text("Middleware test succeeded");
    }

    #[tokio::test]
    async fn test_get_internal_id_mw_ok() {
        let (app, container) = setup_test_server_with_state(true).await;
        let _ = dotenv::from_filename(".env.test");
        let jwt_token = env::var("JWT_TOKEN").unwrap();

        let response = app
            .get("/")
            .add_header("Authorization", format!("Bearer {}", jwt_token))
            .await;

        response.assert_status(StatusCode::OK);
        response.assert_text("Middleware test succeeded");
        debug!(
            "Host: {}",
            container.get_host_port_ipv4(5432).await.unwrap()
        );
    }

    #[tokio::test]
    async fn test_get_internal_id_mw_user_not_found_err() {
        let (app, container) = setup_test_server_with_state(false).await;
        let _ = dotenv::from_filename(".env.test");
        let jwt_token = env::var("JWT_TOKEN").unwrap();

        let response = app
            .get("/")
            .add_header("Authorization", format!("Bearer {}", jwt_token))
            .await;

        response.assert_status(StatusCode::NOT_FOUND);
        response.assert_header("content-type", "application/json");
        response.assert_json(&json!({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "details": {
                "user_id": "user_2ruHSXCzfIRreR2tpttVQBl512a"
            }
        }));
        debug!(
            "Host: {}",
            container.get_host_port_ipv4(5432).await.unwrap()
        );
    }
}
