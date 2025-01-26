import { v7 } from "uuid";

import { relations } from "drizzle-orm";
import {
	boolean,
	pgTable,
	timestamp,
	uuid,
	varchar,
} from "drizzle-orm/pg-core";
import pet from "./pet";
import { gender } from "./types";
import userSubscription from "./userSubscription";

const user = pgTable("users", {
	id: uuid().primaryKey().$defaultFn(v7),
	updatedAt: timestamp()
		.$defaultFn(() => new Date())
		.$onUpdateFn(() => new Date()),
	externalId: varchar({ length: 32 }).unique().notNull(),
	name: varchar({ length: 255 }).notNull(),
	timezone: varchar({ length: 30 }).notNull(),
	gender: gender().notNull(),
	hasOnboarded: boolean().default(false),
});

export const userRelations = relations(user, ({ one, many }) => ({
	subscription: one(userSubscription, {
		fields: [user.id],
		references: [userSubscription.userId],
	}),
	pets: many(pet),
}));

export const table = {
	user,
} as const;

export type Table = typeof table;
export default user;
