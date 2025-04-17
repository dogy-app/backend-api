use axum::extract::State;
use axum::{extract::Extension, Json};
use serde_json::{json, Value};
use sqlx::QueryBuilder;
use uuid::Uuid;

use crate::middleware::auth::layer::CurrentUser;
use crate::service::users::models::JoinedFullUser;
use crate::AppState;

use super::models::{
    FullUser, User, UserNotification, UserNotificationUpdate, UserSubscription,
    UserSubscriptionUpdate, UserUpdate,
};

pub async fn create_user(
    Extension(current_user): Extension<CurrentUser>,
    State(state): State<AppState>,
    Json(mut user): Json<FullUser>,
) -> Json<FullUser> {
    let conn = &*state.db;
    let mut txn = conn.begin().await.unwrap();

    // Inserting Base User
    let user_id: (Uuid,) = sqlx::query_as(
        r#"INSERT INTO users (name, external_id, timezone, gender, has_onboarded)
        VALUES ($1, $2, $3, $4, $5) RETURNING id;
        "#,
    )
    .bind(&user.base.name)
    .bind(&current_user.user_id)
    .bind(&user.base.timezone)
    .bind(&user.base.gender)
    .bind(user.base.has_onboarded)
    .fetch_one(&mut *txn)
    .await
    .unwrap();

    sqlx::query(
        r#"INSERT
        INTO user_subscriptions (user_id, trial_start_date, subscription_type, is_trial_mode)
        VALUES ($1, $2, $3, $4);
        "#,
    )
    .bind(user_id.0)
    .bind(user.subscription.trial_start_date)
    .bind(&user.subscription.subscription_type)
    .bind(user.subscription.is_trial_mode)
    .execute(&mut *txn)
    .await
    .unwrap();

    sqlx::query(
        r#"INSERT
        INTO user_notifications (user_id, enabled, is_registered, daily_enabled, playtime_enabled)
        VALUES ($1, $2, $3, $4, $5);
        "#,
    )
    .bind(user_id.0)
    .bind(user.notifications.enabled)
    .bind(user.notifications.is_registered)
    .bind(user.notifications.daily_enabled)
    .bind(user.notifications.playtime_enabled)
    .execute(&mut *txn)
    .await
    .unwrap();

    txn.commit().await.unwrap();

    user.base.external_id = current_user.user_id;

    Json(user)
}

pub async fn get_user(
    State(state): State<AppState>,
    Extension(current_user): Extension<CurrentUser>,
) -> Json<FullUser> {
    let conn = &*state.db;
    let query = r#"
    SELECT u.*, us.trial_start_date, us.subscription_type, us.is_trial_mode,
        un.enabled, un.is_registered, un.daily_enabled, un.playtime_enabled
    FROM users u
    LEFT JOIN user_subscriptions us ON u.id = us.user_id
    LEFT JOIN user_notifications un ON u.id = un.user_id
    WHERE u.id = $1;
    "#;

    let user_info = sqlx::query_as::<_, JoinedFullUser>(query)
        .bind(current_user.internal_id.unwrap())
        .fetch_one(conn)
        .await
        .unwrap();

    let full_user = FullUser {
        base: User {
            external_id: user_info.external_id,
            name: user_info.name,
            timezone: user_info.timezone,
            gender: user_info.gender,
            has_onboarded: user_info.has_onboarded,
        },
        notifications: UserNotification {
            enabled: user_info.enabled,
            is_registered: user_info.is_registered,
            daily_enabled: user_info.daily_enabled,
            playtime_enabled: user_info.playtime_enabled,
        },
        subscription: UserSubscription {
            trial_start_date: user_info.trial_start_date,
            subscription_type: user_info.subscription_type,
            is_trial_mode: user_info.is_trial_mode,
        },
    };

    Json(full_user)
}

pub async fn update_user_base(
    State(state): State<AppState>,
    Extension(current_user): Extension<CurrentUser>,
    Json(user): Json<UserUpdate>,
) -> Json<UserUpdate> {
    let conn = &*state.db;
    let query = r#"
    UPDATE users
    SET
        name = COALESCE($2, name),
        timezone = COALESCE($3, timezone),
        gender = COALESCE($4, gender),
        has_onboarded = COALESCE($5, has_onboarded)
    WHERE id = $1;
        "#;

    sqlx::query(query)
        .bind(current_user.internal_id.unwrap())
        .bind(&user.name)
        .bind(&user.timezone)
        .bind(&user.gender)
        .bind(user.has_onboarded)
        .execute(conn)
        .await
        .unwrap();

    Json(user)
}

pub async fn update_user_subscription(
    State(state): State<AppState>,
    Extension(current_user): Extension<CurrentUser>,
    Json(user_sub): Json<UserSubscriptionUpdate>,
) -> Json<UserSubscriptionUpdate> {
    let conn = &*state.db;
    let mut query_builder = QueryBuilder::new(
        r#"
        UPDATE user_subscriptions SET
        subscription_type = COALESCE(
        "#,
    );

    query_builder
        .push_bind(&user_sub.subscription_type)
        .push(r#", subscription_type), is_trial_mode = COALESCE( "#)
        .push_bind(user_sub.is_trial_mode)
        .push(", is_trial_mode) ");

    if let Some(trial_date) = user_sub.trial_start_date {
        match trial_date {
            Some(date) => {
                query_builder.push(",trial_start_date = ").push_bind(date);
            }
            None => {
                query_builder.push(",trial_start_date = NULL");
            }
        }
    }

    query_builder
        .push("\nWHERE user_id = ")
        .push_bind(current_user.internal_id.unwrap())
        .push(";");

    let query = query_builder.build();
    query.execute(conn).await.unwrap();

    Json(user_sub)
}

pub async fn update_user_notification(
    State(state): State<AppState>,
    Extension(current_user): Extension<CurrentUser>,
    Json(user_notif): Json<UserNotificationUpdate>,
) -> Json<UserNotificationUpdate> {
    let conn = &*state.db;
    let query = r#"
    UPDATE user_notifications
    SET
        enabled = COALESCE($2, enabled),
        is_registered = COALESCE($3, is_registered),
        daily_enabled = COALESCE($4, daily_enabled),
        playtime_enabled = COALESCE($5, playtime_enabled)
    WHERE user_id = $1;
    "#;

    sqlx::query(query)
        .bind(current_user.internal_id.unwrap())
        .bind(user_notif.enabled)
        .bind(user_notif.is_registered)
        .bind(user_notif.daily_enabled)
        .bind(user_notif.playtime_enabled)
        .execute(conn)
        .await
        .unwrap();

    Json(user_notif)
}

pub async fn delete_user(
    State(state): State<AppState>,
    Extension(current_user): Extension<CurrentUser>,
) -> Json<Value> {
    let conn = &*state.db;
    sqlx::query("DELETE FROM users WHERE id = $1;")
        .bind(current_user.internal_id.unwrap())
        .execute(conn)
        .await
        .unwrap();

    Json(json!({ "message": "User deleted successfully" }))
}
