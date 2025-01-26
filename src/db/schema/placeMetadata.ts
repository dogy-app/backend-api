import { pgTable, text, uuid, varchar } from "drizzle-orm/pg-core";
import { v7 } from "uuid";
import place from "./place";

const placeMetadata = pgTable("places_metadata", {
	id: uuid().primaryKey().$defaultFn(v7),
	city: varchar().notNull(),
	country: varchar().notNull(),
	fullAddress: text().notNull(),
	placeId: uuid()
		.notNull()
		.unique()
		.references(() => place.id),
});

export default placeMetadata;
