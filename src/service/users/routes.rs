use axum::{middleware, routing::get, routing::patch, Router};

use crate::{
    middleware::auth::layer::{auth_middleware, get_internal_id},
    AppState,
};

use super::handlers::{
    create_user, delete_user, get_user, update_user_base, update_user_notification,
    update_user_subscription,
};

pub async fn user_routes(app_state: AppState) -> Router<AppState> {
    Router::new()
        .route(
            "/",
            get(get_user)
                .delete(delete_user)
                .patch(update_user_base)
                .route_layer(middleware::from_fn_with_state(
                    app_state.clone(),
                    get_internal_id,
                ))
                .post(create_user),
        )
        .route(
            "/subscriptions",
            patch(update_user_subscription).route_layer(middleware::from_fn_with_state(
                app_state.clone(),
                get_internal_id,
            )),
        )
        .route(
            "/notifications",
            patch(update_user_notification)
                .route_layer(middleware::from_fn_with_state(app_state, get_internal_id)),
        )
        .route_layer(middleware::from_fn(auth_middleware))
}

pub async fn root_user_routes(app_state: AppState) -> Router<AppState> {
    Router::new().nest("/users", user_routes(app_state).await)
}
