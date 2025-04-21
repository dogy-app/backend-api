CREATE TABLE IF NOT EXISTS user_daily_challenges (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v7 (),
  "created_at" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  "user_id" UUID NOT NULL,
  "challenge" TEXT NOT NULL
);

CREATE TRIGGER trigger_set_updated_at_on_user_daily_challenges BEFORE
UPDATE ON "user_daily_challenges" FOR EACH ROW EXECUTE FUNCTION set_updated_at ();

ALTER TABLE "user_daily_challenges" ADD CONSTRAINT "user_daily_challenges_user_id_users_id" FOREIGN KEY ("user_id") REFERENCES "public"."users" ("id") ON DELETE cascade ON UPDATE no action;
