-- name: GetUserByID :one
SELECT * FROM users where id = $1;

-- name: CreateBaseUser :one
INSERT INTO users (name, external_id, timezone, gender, has_onboarded) VALUES ($1, $2, $3, $4, $5) RETURNING *;

-- name: CreateUserSubscription :one
INSERT INTO user_subscriptions (user_id, trial_start_date, subscription_type, is_trial_mode) VALUES ($1, $2, $3, $4) RETURNING *;

-- name: CreateUserNotifications :one
INSERT INTO user_notifications (user_id, enabled, is_registered, daily_enabled, playtime_enabled) VALUES ($1, $2, $3, $4, $5) RETURNING *;

