CREATE TABLE IF NOT EXISTS "user_daily_streaks" (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v7 (),
  "created_at" TIMESTAMPTZ,
  "updated_at" TIMESTAMPTZ,
  "user_id" UUID NOT NULL,
  "challenge" TEXT NOT NULL
);

CREATE TRIGGER trigger_set_updated_at_on_user_daily_streaks BEFORE
UPDATE ON "user_daily_streaks" FOR EACH ROW EXECUTE FUNCTION set_updated_at ();

ALTER TABLE "user_daily_streaks" ADD CONSTRAINT "user_daily_streaks_user_id_users_id" FOREIGN KEY ("user_id") REFERENCES "public"."users" ("id") ON DELETE cascade ON UPDATE no action;
