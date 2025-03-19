use axum::{extract::Extension, Json};
use sqlx::postgres::PgConnection;
use sqlx::Connection;
use uuid::Uuid;

use crate::middleware::auth::layer::CurrentUser;
use crate::service::users::models::UserNotification;
use crate::{config::load_config, service::users::models::UserSubscription};

use super::models::{FullUser, User};

pub async fn create_user(
    Extension(current_user): Extension<CurrentUser>,
    Json(mut user): Json<FullUser>,
) -> Json<FullUser> {
    let config = load_config();
    println!("--> Connecting to Neon DB...");
    let mut conn = PgConnection::connect(&config.DATABASE_URL).await.unwrap();
    println!("--> Starting transaction...");
    let mut txn = conn.begin().await.unwrap();

    // Inserting Base User
    let user_id: (Uuid, ) = sqlx::query_as(
        r"
INSERT INTO users (name, external_id, timezone, gender, has_onboarded) VALUES ($1, $2, $3, $4, $5) RETURNING id;
",
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
        r"
INSERT INTO user_subscriptions (user_id, trial_start_date, subscription_type, is_trial_mode) VALUES ($1, $2, $3, $4);
",
    )
    .bind(user_id.0)
    .bind(user.subscription.trial_start_date)
    .bind(&user.subscription.subscription_type)
    .bind(user.subscription.is_trial_mode)
    .execute(&mut *txn)
    .await
    .unwrap();

    sqlx::query(
        r"
INSERT INTO user_notifications (user_id, enabled, is_registered, daily_enabled, playtime_enabled) VALUES ($1, $2, $3, $4, $5);
;
",
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
    println!("--> Created User: {}", &current_user.user_id);

    user.base.external_id = current_user.user_id;

    Json(user)
}

pub async fn get_user(Extension(current_user): Extension<CurrentUser>) -> Json<FullUser> {
    println!("--> GET /users test");
    let query = r"
    SELECT u.*, us.trial_start_date,
    us.subscription_type,
    us.is_trial_mode,
    un.enabled,
    un.is_registered,
    un.daily_enabled,
    un.playtime_enabled
    FROM users u
    LEFT JOIN user_subscriptions us ON u.id = us.user_id
    LEFT JOIN user_notifications un ON u.id = un.user_id
    WHERE u.id = $1;
    ";

    let config = load_config();
    println!("--> Connecting to Neon DB...");
    let mut conn = PgConnection::connect(&config.DATABASE_URL).await.unwrap();
    println!("--> Starting transaction...");

    let (user, user_subscription, user_notifications) =
        sqlx::query_as::<_, (User, UserSubscription, UserNotification)>(query)
            .bind(current_user.internal_id.unwrap())
            .fetch_one(&mut conn)
            .await
            .unwrap();

    let full_user = FullUser {
        base: user,
        subscription: user_subscription,
        notifications: user_notifications,
    };

    Json(full_user)
}
