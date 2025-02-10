-- +goose Up
-- +goose StatementBegin
-- Auth and database setup

-- +goose envsub on
CREATE ROLE app_user WITH LOGIN PASSWORD '${APP_USER_PASSWORD}';

GRANT CONNECT ON DATABASE "${DB_NAME}" TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
-- +goose envsub off

-- Allow SELECT, INSERT, UPDATE, and DELETE on all tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- Ensure new tables automatically get the same privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

-- Allow usage on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT ON SEQUENCES TO app_user;

-- UUID v7 from https://gist.github.com/kjmph/5bd772b2c2df145aa645b837da7eca74
CREATE OR REPLACE FUNCTION UUID_GENERATE_V7()
RETURNS UUID
AS $$
BEGIN
  RETURN ENCODE(
    SET_BIT(
      SET_BIT(
        OVERLAY(UUID_SEND(GEN_RANDOM_UUID())
                PLACING SUBSTRING(INT8SEND(FLOOR(EXTRACT(EPOCH FROM CLOCK_TIMESTAMP()) * 1000)::BIGINT) FROM 3)
                FROM 1 FOR 6
        ),
        52, 1
      ),
      53, 1
    ),
    'HEX')::UUID;
END
$$
LANGUAGE PLPGSQL
VOLATILE;

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
CREATE TYPE "public"."pet_breed" AS ENUM('Australian Shepherd', 'American Cocker Spaniel', 'Akita', 'Australian Cattle', 'Airedale Terrier', 'Alaskan Malamute', 'American Staffordshire Terrier', 'Anatolian Shepherd', 'American Eskimo', 'Afghan Hound', 'American Hairless Terrier', 'Australian Terrier', 'American Water Spaniel', 'Affenpinscher', 'American English Coonhound', 'American Foxhound', 'Azawakh', 'American Pit Bull Terrier', 'American White Shepherd', 'Alapaha Blue Blood Bulldog', 'Alaskan Klee Kai', 'Appenzeller Sennenhund', 'Australian Bulldog', 'Australian Kelpie', 'Australian Stumpy Tail Cattle', 'Austrian Black and Tan Hound', 'Austrian Pinscher', 'Alaskan Husky', 'American Bulldog', 'Andalusian Hound', 'American Mastiff', 'Akbash', 'Alano Espanol', 'Ariege Pointer', 'Ariegeois', 'Africanis', 'Aidi', 'American Staghound', 'Alopekis', 'Bulldog', 'Beagle', 'Boxer', 'Boston Terrier', 'Bernese Mountain', 'Brittany', 'Border Collie', 'Basset Hound', 'Belgian Malinois', 'Bichon Frise', 'Bloodhound', 'Bullmastiff', 'Bull Terrier', 'Basenji', 'Boykin Spaniel', 'Brussels Griffon', 'Bouvier des Flandres', 'Border Terrier', 'Borzoi', 'Belgian Tervuren', 'Belgian Sheep', 'Beauceron', 'Boerboel', 'Bearded Collie', 'Black Russian Terrier', 'Black and Tan Coonhound', 'Bluetick Coonhound', 'Bedlington Terrier', 'Barbet', 'Briard', 'Berger Picard', 'Bergamasco', 'Bolognese', 'Basset Bleu de Gascogne', 'Basset Fauve de Bretagne', 'Belgian Shepherd Laekenois', 'Black Mouth Cur', 'Black Norwegian Elkhound', 'Blue Lacy', 'Blue Picardy Spaniel', 'Bohemian Shepherd', 'Bracco Italiano', 'Braque du Bourbonnais', 'Brazilian Terrier', 'Bulgarian Shepherd', 'Basset Artesien Normand', 'Broholmer', 'Biewer Terrier', 'Briquet Griffon Vendeen', 'Bukovina Sheepdog', 'Beagle-Harrier', 'Beaglier', 'Bavarian Mountain Hound', 'Bouvier des Ardennes', 'Bull Arab', 'Cavalier King Charles Spaniel', 'Cane Corso', 'Chihuahua', 'Collie', 'Chesapeake Bay Retriever', 'Cardigan Welsh Corgi', 'Cairn Terrier', 'Chinese Crested', 'Coton De Tulear', 'Chow Chow', 'Clumber Spaniel', 'Curly-Coated Retriever', 'Cirneco dell’Etna', 'Canaan', 'Chinook', 'Cesky Terrier', 'Cockapoo', 'Canadian Eskimo', 'Carolina', 'Carpathian Sheepdog', 'Catahoula Bulldog', 'Catahoula Leopard', 'Catalan Sheepdog', 'Caucasian Ovcharka', 'Central Asian Ovtcharka', 'Croatian Sheepdog', 'Czechoslovakian Wolfdog', 'Cesky Fousek', 'Chart Polski', 'Cairmal', 'Chorkie', 'Cockalier', 'Caravan Hound', 'Cão da Serra de Aires', 'Chippiparai', 'Chizer', 'Cotonese', 'Dachshund', 'Doberman Pinscher', 'Dalmatian', 'Dogue de Bordeaux', 'Dogo Argentino', 'Dandie Dinmont Terrier', 'Dutch Shepherd', 'Double Doodle', 'Deutsche Bracke', 'Dorkie', 'Danish-Swedish Farmdog', 'Dingo', 'Dutch Smoushond', 'Drentse Patrijshond', 'Drever', 'Dunker', 'Dorgi', 'English Springer Spaniel', 'English Cocker Spaniel', 'English Setter', 'English Toy Spaniel', 'Entlebucher Mountain', 'English Foxhound', 'East-European Shepherd', 'English Shepherd', 'Eurasier', 'East Siberian Laika', 'French Bulldog', 'Flat-Coated Retriever', 'Field Spaniel', 'Finnish Lapphund', 'Finnish Spitz', 'Fila Brasileiro', 'French Spaniel', 'Finnish Hound', 'Francais Blanc et Noir', 'German Shepherd', 'Golden Retriever', 'German Shorthaired Pointer', 'Great Dane', 'German Wirehaired Pointer', 'Giant Schnauzer', 'Great Pyrenees', 'Greater Swiss Mountain', 'Gordon Setter', 'German Pinscher', 'Greyhound', 'Glen of Imaal Terrier', 'Grand Basset Griffon Vendeen', 'Goldendoodle', 'German Longhaired Pointer', 'Greenland', 'Griffon bleu de Gascogne', 'Grand Bleu de Gascogne', 'Havanese', 'Harrier', 'Hokkaido', 'Hovawart', 'Hamilton Hound', 'Italian Greyhound', 'Irish Wolfhound', 'Irish Setter', 'Irish Terrier', 'Icelandic Sheepdog', 'Irish Red and White Setter', 'Ibizan Hound', 'Irish Water Spaniel', 'Jack Russell Terrier', 'Japanese Chin', 'Japanese Spitz', 'Jagdterrier', 'Japanese Terrier', 'Jämthund', 'Keeshond', 'Kerry Blue Terrier', 'Kooikerhondje', 'Kuvasz', 'Komondor', 'Korean Jindo', 'Karelian Bear', 'Kishu Ken', 'Koolie', 'Kromfohrlander', 'Kangal', 'King Shepherd', 'Kyi-Leo', 'Karst Shepherd', 'Labrador Retriever', 'Lhasa Apso', 'Lagotto Romagnolo', 'Leonberger', 'Lakeland Terrier', 'Lowchen', 'Large Munsterlander', 'Lancashire Heeler', 'Landseer', 'Lucas Terrier', 'Lurcher', 'Lapponian Herder', 'Miniature Schnauzer', 'Miniature American Shepherd', 'Mastiff', 'Maltese', 'Miniature Pinscher', 'Miniature Bull Terrier', 'Manchester Terrier', 'Miniature Bulldog', 'Miniature Poodle', 'Miniature Shar Pei', 'McNab', 'Mudi', 'Mountain Feist', 'Maremma Sheepdog', 'Mal-Shi', 'Moscow Watchdog', 'Mountain Cur', 'Majestic Tree Hound', 'Newfoundland', 'Nova Scotia Duck Tolling Retriever', 'Norwegian Elkhound', 'Neapolitan Mastiff', 'Norwich Terrier', 'Norfolk Terrier', 'Norwegian Buhund', 'Norwegian Lundehund', 'Norrbottenspets', 'Northern Inuit', 'New Guinea Singing', 'Old English Sheepdog', 'Otterhound', 'Olde English Bulldogge', 'Poodle', 'Pembroke Welsh Corgi', 'Pomeranian', 'Pug', 'Portuguese Water', 'Papillon', 'Pekingese', 'Parson Russell Terrier', 'Pointer', 'Puli', 'Pumi', 'Portuguese Podengo Pequeno', 'Petit Basset Griffon Vendeen', 'Plott Hound', 'Polish Lowland Sheepdog', 'Pharaoh Hound', 'Pyrenean Shepherd', 'Pakistani Mastiff', 'Patterdale Terrier', 'Perro de Presa Canario', 'Perro de Presa Mallorquin', 'Peruvian Inca Orchid', 'Picardy Spaniel', 'Prazsky Krysarik', 'Pont-Audemer Spaniel', 'Pyrenean Mastiff', 'Polish Tatra Sheepdog', 'Puggle', 'Pudelpointer', 'Plummer Terrier', 'Portuguese Pointer', 'Polish Hunting Dog', 'Rottweiler', 'Rhodesian Ridgeback', 'Rat Terrier', 'Redbone Coonhound', 'Russian Toy', 'Russian Spaniel', 'Russian Tsvetnaya Bolonka', 'Romanian Mioritic Shepherd Dog', 'Rajapalayam', 'Rafeiro do Alentejo', 'Siberian Husky', 'Shih Tzu', 'Shetland Sheepdog', 'Shiba Inu', 'St. Bernard', 'Samoyed', 'Scottish Terrier', 'Soft Coated Wheaten Terrier', 'Shar-Pei', 'Staffordshire Bull Terrier', 'Standard Schnauzer', 'Silky Terrier', 'Spinone Italiano', 'Schipperke', 'Smooth Fox Terrier', 'Saluki', 'Swedish Vallhund', 'Sealyham Terrier', 'Spanish Water Dog', 'Scottish Deerhound', 'Sussex Spaniel', 'Skye Terrier', 'Sloughi', 'Small Munsterlander', 'Saarloos Wolfdog', 'Sarplaninac', 'Schapendoes', 'Shikoku', 'Shiloh Shepherd', 'Silken Windhound', 'Spanish Mastiff', 'Swedish Lapphund', 'Shichon', 'Slovensky Cuvac', 'Stabyhoun', 'Spanish Greyhound', 'Seppala Siberian Sleddog', 'South Russian Ovcharka', 'Sapsali', 'Smaland Hound', 'Serbian Hound', 'Tibetan Terrier', 'Toy Fox Terrier', 'Tibetan Spaniel', 'Tibetan Mastiff', 'Treeing Walker Coonhound', 'Toy Poodle', 'Tamaskan Dog', 'Thai Ridgeback', 'Tosa Ken', 'Texas Heeler', 'Tornjak', 'Taco Terrier', 'Thai Bangkaew Dog', 'Transylvanian Hound', 'Vizsla', 'Volpino Italiano', 'Weimaraner', 'West Highland White Terrier', 'Whippet', 'Wirehaired Pointing Griffon', 'Wire Fox Terrier', 'Welsh Terrier', 'Welsh Springer Spaniel', 'Wirehaired Vizsla', 'West Siberian Laika', 'Wetterhoun', 'Xoloitzcuintli', 'Yorkshire Terrier');--> statement-breakpoint
CREATE TYPE "public"."pet_interaction" AS ENUM('Loves other dogs', 'Prefers human company', 'Good with children', 'Good with cats/other pets', 'Enjoys large groups', 'Prefers one-on-one interactions');--> statement-breakpoint
CREATE TYPE "public"."pet_personality" AS ENUM('Playful', 'Energetic', 'Shy', 'Outgoing', 'Calm', 'Reserved', 'Affectionate', 'Independent');--> statement-breakpoint
CREATE TYPE "public"."pet_reactivity" AS ENUM('Non-reactive', 'Reactive to strangers', 'Reactive to noises', 'Reactive to moving objects', 'Reactive to specific situations', 'Reactive to same gender dogs');--> statement-breakpoint
CREATE TYPE "public"."pet_size" AS ENUM('small', 'medium', 'large');--> statement-breakpoint
CREATE TYPE "public"."subscription_type" AS ENUM('active', 'inactive', 'unknown');--> statement-breakpoint
CREATE TYPE "public"."place_category" AS ENUM('dog park', 'misc');
CREATE TYPE "public"."weight_unit" AS ENUM('kg', 'lbs');

CREATE TABLE IF NOT EXISTS "users" (
    "id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
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
    "id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
    "user_id" UUID NOT NULL,
    "enabled" BOOLEAN DEFAULT FALSE NOT NULL,
    "is_registered" BOOLEAN DEFAULT FALSE NOT NULL,
    "daily_enabled" BOOLEAN DEFAULT FALSE NOT NULL,
    "playtime_enabled" BOOLEAN DEFAULT FALSE NOT NULL,
    CONSTRAINT "user_notifications_user_id_unique" UNIQUE("user_id")
);

CREATE TABLE IF NOT EXISTS "user_subscriptions" (
    "id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
    "user_id" UUID NOT NULL,
    "trial_start_date" DATE NOT NULL,
    "subscription_type" "subscription_type" NOT NULL,
    "is_trial_mode" BOOLEAN DEFAULT FALSE NOT NULL,
    CONSTRAINT "user_subscriptions_user_id_unique" UNIQUE("user_id")
);

CREATE TABLE IF NOT EXISTS "pets" (
    "id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
    "created_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(255) NOT NULL,
    "birthday" DATE NOT NULL,
    "photo_url" TEXT NOT NULL,
    "gender" "gender" NOT NULL,
    "size" "pet_size" NOT NULL,
    "weight" NUMERIC(5,2) NOT NULL,
    "weight_unit" "weight_unit" NOT NULL
);

CREATE TRIGGER trigger_set_updated_at_on_pets
BEFORE UPDATE ON "pets"
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS "pet_attrs" (
    "id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
    "pet_id" UUID NOT NULL,
    "is_sterilized" BOOLEAN DEFAULT FALSE NOT NULL,
    CONSTRAINT "pet_attrs_pet_id_unique" UNIQUE("pet_id")
);

CREATE TABLE "pet_attr_aggression_levels" (
	"id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
	"pet_attr_id" UUID NOT NULL,
	"aggression_level" "pet_aggression_level" NOT NULL
);

CREATE TABLE "pet_attr_allergies" (
	"id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
	"pet_attr_id" UUID NOT NULL,
	"allergy" "pet_allergy" NOT NULL
);

CREATE TABLE "pet_attr_behaviors" (
	"id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
	"pet_attr_id" UUID NOT NULL,
	"behavior" "pet_behavior" NOT NULL
);

CREATE TABLE "pet_attr_breeds" (
	"id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
	"pet_attr_id" UUID NOT NULL,
	"breed" "pet_breed" NOT NULL
);

CREATE TABLE "pet_attr_interactions" (
	"id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
	"pet_attr_id" UUID NOT NULL,
	"interaction" "pet_interaction" NOT NULL
);

CREATE TABLE "pet_attr_personalities" (
	"id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
	"pet_attr_id" UUID NOT NULL,
	"personality" "pet_personality" NOT NULL
);

CREATE TABLE "pet_attr_reactivities" (
	"id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
	"pet_attr_id" UUID NOT NULL,
	"reactivity" "pet_reactivity" NOT NULL
);

CREATE TABLE "users_pets_link" (
	"id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
	"pet_id" UUID NOT NULL,
	"user_id" UUID NOT NULL,
    "is_dog_owner" BOOLEAN DEFAULT TRUE NOT NULL,
    "is_dog_sitter" BOOLEAN DEFAULT FALSE NOT NULL
);

CREATE TABLE "places" (
	"id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
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
	"id" UUID PRIMARY KEY DEFAULT UUID_GENERATE_V7(),
    "place_id" UUID NOT NULL,
    "city" TEXT NOT NULL,
    "country" TEXT NOT NULL,
    "full_address" TEXT NOT NULL,
    CONSTRAINT "places_metadata_place_id_unique" UNIQUE("place_id")
);

ALTER TABLE "pet_attrs" ADD CONSTRAINT "pet_attrs_pet_id_pets_id_fk" FOREIGN KEY ("pet_id") REFERENCES "public"."pets"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "pet_attr_aggression_levels" ADD CONSTRAINT "pet_attr_aggression_levels_pet_attr_id_pet_attrs_id_fk" FOREIGN KEY ("pet_attr_id") REFERENCES "public"."pet_attrs"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "pet_attr_allergies" ADD CONSTRAINT "pet_attr_allergies_pet_attr_id_pet_attrs_id_fk" FOREIGN KEY ("pet_attr_id") REFERENCES "public"."pet_attrs"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "pet_attr_behaviors" ADD CONSTRAINT "pet_attr_behaviors_pet_attr_id_pet_attrs_id_fk" FOREIGN KEY ("pet_attr_id") REFERENCES "public"."pet_attrs"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "pet_attr_breeds" ADD CONSTRAINT "pet_attr_breeds_pet_attr_id_pet_attrs_id_fk" FOREIGN KEY ("pet_attr_id") REFERENCES "public"."pet_attrs"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "pet_attr_interactions" ADD CONSTRAINT "pet_attr_interactions_pet_attr_id_pet_attrs_id_fk" FOREIGN KEY ("pet_attr_id") REFERENCES "public"."pet_attrs"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "pet_attr_personalities" ADD CONSTRAINT "pet_attr_personalities_pet_attr_id_pet_attrs_id_fk" FOREIGN KEY ("pet_attr_id") REFERENCES "public"."pet_attrs"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "pet_attr_reactivities" ADD CONSTRAINT "pet_attr_reactivities_pet_attr_id_pet_attrs_id_fk" FOREIGN KEY ("pet_attr_id") REFERENCES "public"."pet_attrs"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "user_subscriptions" ADD CONSTRAINT "user_subscriptions_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE cascade;
ALTER TABLE "user_notifications" ADD CONSTRAINT "user_notifications_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE cascade;
ALTER TABLE "users_pets_link" ADD CONSTRAINT "users_pets_link_user_id_users_id" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE no action;
ALTER TABLE "users_pets_link" ADD CONSTRAINT "users_pets_link_pet_id_pets_id" FOREIGN KEY ("pet_id") REFERENCES "public"."pets"("id") ON DELETE cascade ON UPDATE no action;
ALTER TABLE "places_metadata" ADD CONSTRAINT "places_metadata_place_id_places_id_fk" FOREIGN KEY ("place_id") REFERENCES "public"."places"("id") ON DELETE cascade ON UPDATE no action;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
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

DROP EXTENSION IF EXISTS "postgis";
DROP FUNCTION set_updated_at();
DROP FUNCTION uuid_generate_v7();
-- Revoke usage on sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public
REVOKE USAGE, SELECT ON SEQUENCES FROM app_user;
REVOKE USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public FROM app_user;

-- Revoke privileges on tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES FROM app_user;
REVOKE SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public FROM app_user;

-- Revoke usage on schema
REVOKE USAGE ON SCHEMA public FROM app_user;

-- Revoke connect on database
-- +goose envsub on
REVOKE CONNECT ON DATABASE "${DB_NAME}" FROM app_user;
-- +goose envsub off

-- Drop the role
DROP ROLE app_user;
-- +goose StatementEnd
