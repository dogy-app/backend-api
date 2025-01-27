import { boolean, date, pgTable, uuid } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-typebox";
import { t } from "elysia";
import { v7 } from "uuid";
import { subscriptionType } from "./types";
import user from "./user";

const userSubscription = pgTable("user_subscriptions", {
	id: uuid()
		.primaryKey()
		.$defaultFn(() => v7()),
	userId: uuid("user_id")
		.notNull()
		.unique()
		.references(() => user.id, { onDelete: "cascade" }),
	trialStartDate: date("trial_start_date").notNull(),
	subscriptionType: subscriptionType("subscription_type").notNull(),
	isRegistered: boolean("is_registered").notNull().default(false),
	isTrialMode: boolean("is_trial_mode").notNull().default(false),
});

const _createUserSubscriptionSchema = createInsertSchema(userSubscription);
export const createUserSubscriptionSchema = t.Omit(
	_createUserSubscriptionSchema,
	["id", "userId"],
);

export type CreateUserSubscriptionSchema =
	typeof createUserSubscriptionSchema.static;

export default userSubscription;
