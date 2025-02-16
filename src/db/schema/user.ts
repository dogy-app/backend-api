import { v7 } from "uuid";

import { like, relations } from "drizzle-orm";
import {
	boolean,
	pgTable,
	timestamp,
	uuid,
	varchar,
} from "drizzle-orm/pg-core";
import { createInsertSchema, createSelectSchema } from "drizzle-zod";
import pet from "./pet";
import { gender } from "./types";
import userSubscription from "./userSubscription";

const user = pgTable("users", {
	id: uuid().primaryKey().$defaultFn(v7),
	updatedAt: timestamp("updated_at")
		.defaultNow()
		.$onUpdateFn(() => new Date()),
	externalId: varchar("external_id", { length: 32 }).unique().notNull(),
	name: varchar({ length: 255 }).notNull(),
	timezone: varchar({ length: 30 }).notNull(),
	gender: gender().notNull(),
	hasOnboarded: boolean("has_onboarded").default(false),
});

export const userRelations = relations(user, ({ one, many }) => ({
	subscription: one(userSubscription, {
		fields: [user.id],
		references: [userSubscription.userId],
	}),
	pets: many(pet),
}));

export const selectUserSchema = createSelectSchema(user).omit({
	id: true,
	updatedAt: true,
});
export const insertUserSchema = createInsertSchema(user);

const userSubscriptionSchema = createSelectSchema(userSubscription);

export const selectFullUserSchema = selectUserSchema.extend({
	subscription: userSubscriptionSchema.omit({
		id: true,
		userId: true,
	}),
});

export default user;
