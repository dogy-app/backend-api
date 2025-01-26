import { boolean, date, pgTable, uuid } from "drizzle-orm/pg-core";
import { v7 } from "uuid";
import { subscriptionType } from "./types";
import user from "./user";

const userSubscription = pgTable("user_subscriptions", {
	id: uuid()
		.primaryKey()
		.$defaultFn(() => v7()),
	userId: uuid()
		.notNull()
		.unique()
		.references(() => user.id),
	trialStartDate: date().notNull(),
	subscriptionType: subscriptionType().notNull(),
	isRegistered: boolean().notNull().default(false),
	isTrialMode: boolean().notNull().default(false),
});

export default userSubscription;
