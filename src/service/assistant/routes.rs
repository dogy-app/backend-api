use axum::{
    middleware,
    routing::{get, post},
    Router,
};

use crate::{
    middleware::auth::layer::{auth_middleware, get_internal_id},
    AppState,
};

use super::{
    daily_challenges::routes::root_daily_challenge_routes,
    handlers::{
        get_all_threads_from_user, link_user_to_thread, unlink_thread_from_user,
        update_thread_title,
    },
};

async fn thread_routes(app_state: AppState) -> Router<AppState> {
    Router::new()
        .route("/", get(get_all_threads_from_user))
        .route(
            "/{thread_id}",
            post(link_user_to_thread)
                .patch(update_thread_title)
                .delete(unlink_thread_from_user),
        )
        .route_layer(middleware::from_fn_with_state(
            app_state.clone(),
            get_internal_id,
        ))
        .route_layer(middleware::from_fn(auth_middleware))
}

pub async fn root_threads_routes(app_state: AppState) -> Router<AppState> {
    Router::new().nest("/threads", thread_routes(app_state).await)
}

pub async fn root_assistant_routes(app_state: AppState) -> Router<AppState> {
    Router::new()
        .nest("/assistant", root_threads_routes(app_state.clone()).await)
        .nest("/assistant", root_daily_challenge_routes(app_state).await)
}
