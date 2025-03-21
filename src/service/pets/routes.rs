use axum::{
    middleware,
    routing::{get, patch, post},
    Router,
};

use crate::{
    middleware::auth::layer::{auth_middleware, get_internal_id},
    AppState,
};

use super::handlers::{
    create_pet, delete_pet, get_all_pets, get_pet, update_base_pet, update_pet_attributes,
};

async fn pet_routes(app_state: AppState) -> Router<AppState> {
    Router::new()
        .route("/", post(create_pet).get(get_all_pets))
        .route(
            "/{pet_id}",
            get(get_pet).delete(delete_pet).patch(update_base_pet),
        )
        .route("/attributes/{pet_id}", patch(update_pet_attributes))
        .route_layer(middleware::from_fn_with_state(
            app_state.clone(),
            get_internal_id,
        ))
        .route_layer(middleware::from_fn(auth_middleware))
}

pub async fn root_pet_routes(app_state: AppState) -> Router<AppState> {
    Router::new().nest("/pets", pet_routes(app_state).await)
}
