import { relations, sql } from "drizzle-orm";
import {
	geometry,
	index,
	pgTable,
	text,
	timestamp,
	uuid,
	varchar,
} from "drizzle-orm/pg-core";
import { v7 } from "uuid";
import placeMetadata from "./placeMetadata";

const place = pgTable(
	"places",
	{
		id: uuid().primaryKey().$defaultFn(v7),
		geom: geometry({ type: "point", srid: 4326, mode: "xy" }),
		updatedAt: timestamp()
			.$defaultFn(() => new Date())
			.$onUpdateFn(() => new Date()),
		gmapsId: varchar({ length: 27 }).notNull().unique(),
		name: varchar().notNull(),
		description: text().notNull(),
		websiteUrl: varchar().notNull(),
		images: text().array().notNull().default(sql`ARRAY[]::text[]`),
	},
	(table) => ({
		gist: index("geom_index").using("gist", table.geom),
	}),
);

export const placeRelations = relations(place, ({ one }) => ({
	metadata: one(placeMetadata, {
		fields: [place.id],
		references: [placeMetadata.placeId],
	}),
}));

export default place;
