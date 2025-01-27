import { v7 } from "uuid";

import { relations } from "drizzle-orm";
import {
	boolean,
	pgTable,
	timestamp,
	uuid,
	varchar,
} from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-typebox";
import { t } from "elysia";
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

const _createUserSchema = createInsertSchema(user);
const _optionalExternalId = t.Object({
	..._createUserSchema.properties,
	externalId: t.Optional(t.String()),
});
export const createUserSchema = t.Omit(_optionalExternalId, [
	"id",
	"updatedAt",
]);
export type CreateUserSchema = typeof createUserSchema.static;

export default user;
