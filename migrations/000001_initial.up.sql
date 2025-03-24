--- CREATE ROLE web_backend_public WITH LOGIN PASSWORD '${WEB_BACKEND_PUBLIC_PASSWORD}';

GRANT CONNECT ON DATABASE "web-backend" TO web_backend_public;
GRANT USAGE ON SCHEMA public TO web_backend_public;

-- Allow SELECT, INSERT, UPDATE, and DELETE on all tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO web_backend_public;

-- Ensure new tables automatically get the same privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO web_backend_public;

-- Allow usage on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO web_backend_public;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT ON SEQUENCES TO web_backend_public;

CREATE EXTENSION "postgis";
CREATE EXTENSION "pg_uuidv7";
-- CREATE OR REPLACE FUNCTION UUID_GENERATE_V7()
-- RETURNS UUID
-- AS $$
-- BEGIN
--   RETURN ENCODE(
--     SET_BIT(
--       SET_BIT(
--         OVERLAY(UUID_SEND(GEN_RANDOM_UUID())
--                 PLACING SUBSTRING(INT8SEND(FLOOR(EXTRACT(EPOCH FROM CLOCK_TIMESTAMP()) * 1000)::BIGINT) FROM 3)
--                 FROM 1 FOR 6
--         ),
--         52, 1
--       ),
--       53, 1
--     ),
--     'HEX')::UUID;
-- END
-- $$
-- LANGUAGE PLPGSQL
-- VOLATILE;

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE EXTENSION IF NOT EXISTS "postgis";

CREATE TYPE "public"."gender" AS ENUM('male', 'female');--> statement-breakpoint
CREATE TYPE "public"."pet_aggression_level" AS ENUM('Non-aggressive', 'Guarding behavior', 'Mild aggression under specific circumstances', 'Known history of aggression');--> statement-breakpoint
CREATE TYPE "public"."pet_allergy" AS ENUM('None', 'Beef', 'Chicken', 'Lamb', 'Pork', 'Fish', 'Eggs', 'Milk', 'Cheese', 'Barley', 'Wheat', 'Corn', 'Soy', 'Peanuts', 'Sesame', 'Millet', 'Rice', 'Oats', 'Tree Nuts', 'Yeast', 'Fruits');--> statement-breakpoint
CREATE TYPE "public"."pet_behavior" AS ENUM('Obedient', 'Stubborn', 'Curious', 'Alert', 'Relaxed', 'Anxious', 'Fearful', 'Confident', 'Aggressive', 'Timid', 'Dominant', 'Submissive');--> statement-breakpoint
CREATE TYPE "public"."pet_interaction" AS ENUM('Loves other dogs', 'Prefers human company', 'Good with children', 'Good with cats/other pets', 'Enjoys large groups', 'Prefers one-on-one interactions');
CREATE TYPE "public"."pet_personality" AS ENUM('Playful', 'Energetic', 'Shy', 'Outgoing', 'Calm', 'Reserved', 'Affectionate', 'Independent');
CREATE TYPE "public"."pet_reactivity" AS ENUM('Non-reactive', 'Reactive to strangers', 'Reactive to noises', 'Reactive to moving objects', 'Reactive to specific situations', 'Reactive to same gender dogs');
CREATE TYPE "public"."pet_size" AS ENUM('small', 'medium', 'large');
CREATE TYPE "public"."subscription_type" AS ENUM('active', 'inactive', 'unknown');
CREATE TYPE "public"."place_category" AS ENUM('dog park', 'misc');
CREATE TYPE "public"."weight_unit" AS ENUM('kg', 'lbs');

CREATE TABLE IF NOT EXISTS "users" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(255) NOT NULL,
    "external_id" VARCHAR(32) NOT NULL,
    "timezone" VARCHAR(32) NOT NULL,
    "gender" "gender" NOT NULL,
    "has_onboarded" BOOLEAN DEFAULT FALSE NOT NULL,
    CONSTRAINT "users_external_id_unique" UNIQUE("external_id")
);

CREATE TRIGGER trigger_set_updated_at_on_users
BEFORE UPDATE ON "users"
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS "user_notifications" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    "user_id" UUID NOT NULL,
    "enabled" BOOLEAN DEFAULT FALSE NOT NULL,
    "is_registered" BOOLEAN DEFAULT FALSE NOT NULL,
    "daily_enabled" BOOLEAN DEFAULT FALSE NOT NULL,
    "playtime_enabled" BOOLEAN DEFAULT FALSE NOT NULL,
    CONSTRAINT "user_notifications_user_id_unique" UNIQUE("user_id")
);

CREATE TABLE IF NOT EXISTS "user_subscriptions" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    "user_id" UUID NOT NULL,
    "trial_start_date" DATE, -- NULLABLE
    "subscription_type" "subscription_type" NOT NULL,
    "is_trial_mode" BOOLEAN DEFAULT FALSE NOT NULL,
    CONSTRAINT "user_subscriptions_user_id_unique" UNIQUE("user_id")
);

CREATE TABLE IF NOT EXISTS "user_assistant_threads" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID NOT NULL,
    "thread_id" UUID NOT NULL,
    "thread_title" VARCHAR(255) NOT NULL,
    CONSTRAINT "user_assistant_threads_thread_id_unique" UNIQUE("thread_id")
);

CREATE TRIGGER trigger_set_updated_at_on_user_threads
BEFORE UPDATE ON "user_assistant_threads"
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS "pets" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(255) NOT NULL,
    "age" SMALLINT NOT NULL CHECK (age >= 0 AND age <= 100),
    "photo_url" TEXT NOT NULL,
    "gender" "gender" NOT NULL,
    "size" "pet_size" NOT NULL,
    "weight" FLOAT4 NOT NULL,
    "weight_unit" "weight_unit" NOT NULL
);

CREATE TRIGGER trigger_set_updated_at_on_pets
BEFORE UPDATE ON "pets"
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS "pet_attrs" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    "pet_id" UUID NOT NULL,
    "is_sterilized" BOOLEAN DEFAULT FALSE NOT NULL,
    CONSTRAINT "pet_attrs_pet_id_unique" UNIQUE("pet_id")
);

CREATE TABLE "pet_attr_aggression_levels" (
	"id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
	"pet_attr_id" UUID NOT NULL,
	"aggression_levels" "pet_aggression_level"[] NOT NULL,
    CONSTRAINT "pet_attrs_aggression_levels_pet_attr_id_unique" UNIQUE("pet_attr_id")
);

CREATE TABLE "pet_attr_allergies" (
	"id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
	"pet_attr_id" UUID NOT NULL,
	"allergies" "pet_allergy"[] NOT NULL,
    CONSTRAINT "pet_attrs_allergies_pet_attr_id_unique" UNIQUE("pet_attr_id")
);

CREATE TABLE "pet_attr_behaviors" (
	"id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
	"pet_attr_id" UUID NOT NULL,
	"behaviors" "pet_behavior"[] NOT NULL,
    CONSTRAINT "pet_attrs_behaviors_pet_attr_id_unique" UNIQUE("pet_attr_id")
);

CREATE TABLE "pet_attr_breeds" (
	"id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
	"pet_attr_id" UUID NOT NULL,
	"breeds" VARCHAR(255)[] NOT NULL,
    CONSTRAINT "pet_attrs_breeds_pet_attr_id_unique" UNIQUE("pet_attr_id")
);

CREATE TABLE "pet_attr_interactions" (
	"id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
	"pet_attr_id" UUID NOT NULL,
	"interactions" "pet_interaction"[] NOT NULL,
    CONSTRAINT "pet_attrs_interactions_pet_attr_id_unique" UNIQUE("pet_attr_id")
);

CREATE TABLE "pet_attr_personalities" (
	"id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
	"pet_attr_id" UUID NOT NULL,
	"personalities" "pet_personality"[] NOT NULL,
    CONSTRAINT "pet_attrs_personalities_pet_attr_id_unique" UNIQUE("pet_attr_id")
);

CREATE TABLE "pet_attr_reactivities" (
	"id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
	"pet_attr_id" UUID NOT NULL,
	"reactivities" "pet_reactivity"[] NOT NULL,
    CONSTRAINT "pet_attrs_reactivities_pet_attr_id_unique" UNIQUE("pet_attr_id")
);

CREATE TABLE "users_pets_link" (
	"id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
	"pet_id" UUID NOT NULL,
	"user_id" UUID NOT NULL,
    "is_dog_owner" BOOLEAN DEFAULT TRUE NOT NULL,
    "is_dog_sitter" BOOLEAN DEFAULT FALSE NOT NULL
);

CREATE TABLE "places" (
	"id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "location" GEOMETRY(POINT, 4326) NOT NULL,
    "gmaps_id" VARCHAR(27) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "type" "place_category" NOT NULL,
    "website_url" TEXT NOT NULL,
    "images" TEXT[] NOT NULL,
    CONSTRAINT "places_gmaps_id_unique" UNIQUE("gmaps_id")
);

CREATE TRIGGER trigger_set_updated_at_on_places
BEFORE UPDATE ON "places"
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TABLE "places_metadata" (
	"id" UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    "place_id" UUID NOT NULL,
    "city" TEXT NOT NULL,
    "country" TEXT NOT NULL,
    "full_address" TEXT NOT NULL,
    CONSTRAINT "places_metadata_place_id_unique" UNIQUE("place_id")
);

ALTER TABLE "pet_attrs" ADD CONSTRAINT "pet_attrs_pet_id_pets_id_fk" FOREIGN KEY ("pet_id") REFERENCES "public"."pets"("id") ON DELETE cascade ON UPDATE no action;
ALTER TABLE "pet_attr_aggression_levels" ADD CONSTRAINT "pet_attr_aggression_levels_pet_attr_id_pet_attrs_id_fk" FOREIGN KEY ("pet_attr_id") REFERENCES "public"."pet_attrs"("id") ON DELETE cascade ON UPDATE no action;
ALTER TABLE "pet_attr_allergies" ADD CONSTRAINT "pet_attr_allergies_pet_attr_id_pet_attrs_id_fk" FOREIGN KEY ("pet_attr_id") REFERENCES "public"."pet_attrs"("id") ON DELETE cascade ON UPDATE no action;
ALTER TABLE "pet_attr_behaviors" ADD CONSTRAINT "pet_attr_behaviors_pet_attr_id_pet_attrs_id_fk" FOREIGN KEY ("pet_attr_id") REFERENCES "public"."pet_attrs"("id") ON DELETE cascade ON UPDATE no action;
ALTER TABLE "pet_attr_breeds" ADD CONSTRAINT "pet_attr_breeds_pet_attr_id_pet_attrs_id_fk" FOREIGN KEY ("pet_attr_id") REFERENCES "public"."pet_attrs"("id") ON DELETE cascade ON UPDATE no action;
ALTER TABLE "pet_attr_interactions" ADD CONSTRAINT "pet_attr_interactions_pet_attr_id_pet_attrs_id_fk" FOREIGN KEY ("pet_attr_id") REFERENCES "public"."pet_attrs"("id") ON DELETE cascade ON UPDATE no action;
ALTER TABLE "pet_attr_personalities" ADD CONSTRAINT "pet_attr_personalities_pet_attr_id_pet_attrs_id_fk" FOREIGN KEY ("pet_attr_id") REFERENCES "public"."pet_attrs"("id") ON DELETE cascade ON UPDATE no action;
ALTER TABLE "pet_attr_reactivities" ADD CONSTRAINT "pet_attr_reactivities_pet_attr_id_pet_attrs_id_fk" FOREIGN KEY ("pet_attr_id") REFERENCES "public"."pet_attrs"("id") ON DELETE cascade ON UPDATE no action;
ALTER TABLE "user_subscriptions" ADD CONSTRAINT "user_subscriptions_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE cascade;
ALTER TABLE "user_notifications" ADD CONSTRAINT "user_notifications_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE cascade;
ALTER TABLE "users_pets_link" ADD CONSTRAINT "users_pets_link_user_id_users_id" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE no action;
ALTER TABLE "users_pets_link" ADD CONSTRAINT "users_pets_link_pet_id_pets_id" FOREIGN KEY ("pet_id") REFERENCES "public"."pets"("id") ON DELETE cascade ON UPDATE no action;
ALTER TABLE "user_assistant_threads" ADD CONSTRAINT "user_assistant_threads_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE no action;
ALTER TABLE "places_metadata" ADD CONSTRAINT "places_metadata_place_id_places_id_fk" FOREIGN KEY ("place_id") REFERENCES "public"."places"("id") ON DELETE cascade ON UPDATE no action;
