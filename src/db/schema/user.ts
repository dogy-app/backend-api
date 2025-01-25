import { v7 } from "uuid";

import {
	boolean,
	pgTable,
	timestamp,
	uuid,
	varchar,
} from "drizzle-orm/pg-core";
import { genderEnum } from "./types";

const user = pgTable("users", {
	id: uuid().primaryKey().$defaultFn(v7),
	updatedAt: timestamp()
		.$defaultFn(() => new Date())
		.$onUpdateFn(() => new Date()),
	externalId: varchar({ length: 32 }).unique().notNull(),
	name: varchar({ length: 255 }).notNull(),
	timezone: varchar({ length: 30 }).notNull(),
	gender: genderEnum().notNull(),
	hasOnboarded: boolean().default(false),
});

export default user;
