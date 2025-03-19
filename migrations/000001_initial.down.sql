DROP TABLE IF EXISTS "places_metadata";

DROP TRIGGER IF EXISTS trigger_set_updated_at_on_places ON "places";

DROP TABLE IF EXISTS "places";

DROP TABLE IF EXISTS "users_pets_link";

DROP TABLE IF EXISTS "pet_attr_reactivities";

DROP TABLE IF EXISTS "pet_attr_personalities";

DROP TABLE IF EXISTS "pet_attr_interactions";

DROP TABLE IF EXISTS "pet_attr_breeds";

DROP TABLE IF EXISTS "pet_attr_behaviors";

DROP TABLE IF EXISTS "pet_attr_allergies";

DROP TABLE IF EXISTS "pet_attr_aggression_levels";

DROP TRIGGER IF EXISTS trigger_set_updated_at_on_pets ON "pets";

DROP TABLE IF EXISTS "pet_attrs";

DROP TABLE IF EXISTS "pets";

DROP TABLE IF EXISTS "user_subscriptions";

DROP TABLE IF EXISTS "user_notifications";

DROP TRIGGER IF EXISTS trigger_set_updated_at_on_users ON "users";

DROP TABLE IF EXISTS "users";

DROP TYPE IF EXISTS "public"."weight_unit";

DROP TYPE IF EXISTS "public"."place_category";

DROP TYPE IF EXISTS "public"."subscription_type";

DROP TYPE IF EXISTS "public"."pet_size";

DROP TYPE IF EXISTS "public"."pet_reactivity";

DROP TYPE IF EXISTS "public"."pet_personality";

DROP TYPE IF EXISTS "public"."pet_interaction";

DROP TYPE IF EXISTS "public"."pet_breed";

DROP TYPE IF EXISTS "public"."pet_behavior";

DROP TYPE IF EXISTS "public"."pet_allergy";

DROP TYPE IF EXISTS "public"."pet_aggression_level";

DROP TYPE IF EXISTS "public"."gender";

DROP EXTENSION IF EXISTS "pg_uuidv7";

DROP EXTENSION IF EXISTS "postgis";

DROP FUNCTION set_updated_at ();

DROP FUNCTION uuid_generate_v7 ();

-- Revoke usage on sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE USAGE,
SELECT
  ON SEQUENCES
FROM
  web_backend_public;

REVOKE USAGE,
SELECT
  ON ALL SEQUENCES IN SCHEMA public
FROM
  web_backend_public;

-- Revoke privileges on tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE
SELECT
,
  INSERT,
UPDATE,
DELETE ON TABLES
FROM
  web_backend_public;

REVOKE
SELECT
,
  INSERT,
UPDATE,
DELETE ON ALL TABLES IN SCHEMA public
FROM
  web_backend_public;

-- Revoke usage on schema
REVOKE USAGE ON SCHEMA public
FROM
  web_backend_public;

-- Revoke connect on database
-- +goose envsub on
REVOKE CONNECT ON DATABASE "${DB_NAME}"
FROM
  web_backend_public;

-- +goose envsub off
-- Drop the role
DROP ROLE web_backend_public;
