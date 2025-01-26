import { relations } from "drizzle-orm";
import { boolean, pgTable, uuid } from "drizzle-orm/pg-core";
import { v7 } from "uuid";
import pet from "./pet";
import {
	petAggressionLevel,
	petBehavior,
	petBreed,
	petInteraction,
	petPersonality,
	petReactivity,
} from "./types";

const petAttr = pgTable("pet_attrs", {
	id: uuid().primaryKey().$defaultFn(v7),
	petId: uuid()
		.notNull()
		.unique()
		.references(() => pet.id),
	isSterilized: boolean().notNull(),
});

export const petAttrBreed = pgTable("pet_attr_breeds", {
	id: uuid().primaryKey().$defaultFn(v7),
	petAttrId: uuid()
		.notNull()
		.references(() => petAttr.id),
	breed: petBreed().notNull(),
});

export const petAttrAggressionLevel = pgTable("pet_attr_aggression_levels", {
	id: uuid().primaryKey().$defaultFn(v7),
	petAttrId: uuid()
		.notNull()
		.references(() => petAttr.id),
	aggressionLevel: petAggressionLevel().notNull(),
});

export const petAttrAllergy = pgTable("pet_attr_allergies", {
	id: uuid().primaryKey().$defaultFn(v7),
	petAttrId: uuid()
		.notNull()
		.references(() => petAttr.id),
	allergy: petAggressionLevel().notNull(),
});

export const petAttrBehavior = pgTable("pet_attr_behaviors", {
	id: uuid().primaryKey().$defaultFn(v7),
	petAttrId: uuid()
		.notNull()
		.references(() => petAttr.id),
	behavior: petBehavior().notNull(),
});

export const petAttrInteraction = pgTable("pet_attr_interactions", {
	id: uuid().primaryKey().$defaultFn(v7),
	petAttrId: uuid()
		.notNull()
		.references(() => petAttr.id),
	interaction: petInteraction().notNull(),
});

export const petAttrPersonality = pgTable("pet_attr_personalities", {
	id: uuid().primaryKey().$defaultFn(v7),
	petAttrId: uuid()
		.notNull()
		.references(() => petAttr.id),
	personality: petPersonality().notNull(),
});

export const petAttrReactivity = pgTable("pet_attr_reactivities", {
	id: uuid().primaryKey().$defaultFn(v7),
	petAttrId: uuid()
		.notNull()
		.references(() => petAttr.id),
	reactivity: petReactivity().notNull(),
});

export const petAttrRelations = relations(petAttr, ({ many }) => ({
	aggressionLevels: many(petAttrAggressionLevel),
	allergies: many(petAttrAllergy),
	behaviors: many(petAttrBehavior),
	breeds: many(petAttrBreed),
	interactions: many(petAttrInteraction),
	personalities: many(petAttrPersonality),
	reactivities: many(petAttrReactivity),
}));

export default petAttr;
