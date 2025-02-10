-- name: GetInternalID :one
SELECT id FROM users where external_id = $1;

-- name: CreateBaseUser :one
INSERT INTO users (name, external_id, timezone, gender, has_onboarded) VALUES ($1, $2, $3, $4, $5) RETURNING *;

-- name: CreateUserSubscription :one
INSERT INTO user_subscriptions (user_id, trial_start_date, subscription_type, is_trial_mode) VALUES ($1, $2, $3, $4) RETURNING *;

-- name: CreateUserNotifications :one
INSERT INTO user_notifications (user_id, enabled, is_registered, daily_enabled, playtime_enabled) VALUES ($1, $2, $3, $4, $5) RETURNING *;

-- name: DeleteUser :exec
DELETE FROM users WHERE id = $1;

-- name: GetUserByID :one
SELECT sqlc.embed(users), sqlc.embed(user_subscriptions), sqlc.embed(user_notifications)
FROM users
LEFT JOIN user_subscriptions ON users.id = user_subscriptions.user_id
LEFT JOIN user_notifications ON users.id = user_notifications.user_id
WHERE users.id = $1;

-- name: UpdateBaseUser :exec
UPDATE users
SET
    name = COALESCE(sqlc.narg('name'), name),
    external_id = COALESCE(sqlc.narg('external_id'), external_id),
    timezone = COALESCE(sqlc.narg('timezone'), timezone),
    gender = COALESCE(sqlc.narg('gender'), gender),
    has_onboarded = COALESCE(sqlc.narg('has_onboarded'), has_onboarded)
WHERE id = sqlc.arg('id');

-- name: UpdateUserSubscription :exec
UPDATE user_subscriptions
SET
    trial_start_date = COALESCE(sqlc.narg('trial_start_date'), trial_start_date),
    subscription_type = COALESCE(sqlc.narg('subscription_type'), subscription_type),
    is_trial_mode = COALESCE(sqlc.narg('is_trial_mode'), is_trial_mode)
WHERE id = sqlc.arg('id');

-- name: UpdateUserNotifications :exec
UPDATE user_notifications
SET
    enabled = COALESCE(sqlc.narg('enabled'), enabled),
    is_registered = COALESCE(sqlc.narg('is_registered'), is_registered),
    daily_enabled = COALESCE(sqlc.narg('daily_enabled'), daily_enabled),
    playtime_enabled = COALESCE(sqlc.narg('playtime_enabled'), playtime_enabled)
WHERE id = sqlc.arg('id');

-- name: UpdateUserPetLink :exec
UPDATE users_pets_link
SET
    is_dog_owner = COALESCE(sqlc.narg('is_dog_owner'), is_dog_owner),
    is_dog_sitter = COALESCE(sqlc.narg('is_dog_sitter'), is_dog_sitter),
    user_id = COALESCE(sqlc.narg('user_id'), user_id),
    pet_id = COALESCE(sqlc.narg('pet_id'), pet_id)
WHERE id = sqlc.arg('id');
