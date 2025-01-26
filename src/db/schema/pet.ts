import { relations } from "drizzle-orm";
import {
	date,
	numeric,
	pgTable,
	timestamp,
	uuid,
	varchar,
} from "drizzle-orm/pg-core";
import { v7 } from "uuid";
import petAttr from "./petAttr";
import { gender, petSize } from "./types";

const pet = pgTable("pets", {
	id: uuid().primaryKey().$defaultFn(v7),
	updatedAt: timestamp()
		.$defaultFn(() => new Date())
		.$onUpdateFn(() => new Date()),
	name: varchar().notNull(),
	birthday: date().notNull(),
	photoUrl: varchar().notNull(),
	gender: gender().notNull(),
	size: petSize().notNull(),
	weight: numeric({ precision: 5, scale: 2 }).notNull(),
});

export const petRelations = relations(pet, ({ one }) => ({
	attributes: one(petAttr, {
		fields: [pet.id],
		references: [petAttr.petId],
	}),
}));

export default pet;
