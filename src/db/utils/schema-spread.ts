/**
 * @lastModified 2025-01-26
 * @see https://elysiajs.com/recipe/drizzle.html#utility
 */

import { Kind, type TObject, type TSchema } from "@sinclair/typebox";
import { createInsertSchema, createSelectSchema } from "drizzle-typebox";

import type { Table } from "drizzle-orm";
import { table } from "../schema/user";

type Spread<
	T extends TObject | Table,
	Mode extends "select" | "insert" | undefined,
> = T extends TObject<infer Fields>
	? { [K in keyof Fields]: Fields[K] }
	: T extends Table
		? Mode extends "select"
			? ReturnType<typeof createSelectSchema<T>>
			: Mode extends "insert"
				? ReturnType<typeof createInsertSchema<T>>
				: {}
		: {};

/**
 * Spread a Drizzle schema into a plain object
 */
export const spread = <
	T extends TObject | Table,
	Mode extends "select" | "insert" | undefined,
>(
	schema: T,
	mode?: Mode,
): Spread<T, Mode> => {
	const newSchema: Record<string, TSchema> = {};
	let targetSchema: TObject;

	if (schema instanceof Table) {
		targetSchema =
			mode === "insert"
				? createInsertSchema(schema)
				: createSelectSchema(schema);
	} else if (Kind in schema) {
		targetSchema = schema as TObject;
	} else {
		throw new Error("Invalid schema type");
	}

	for (const key of Object.keys(targetSchema.properties))
		newSchema[key] = targetSchema.properties[key];

	return newSchema as Spread<T, Mode>;
};

const a = spread(table.user, "insert");

/**
 * Spread multiple Drizzle Tables into plain objects
 */
export const spreads = <
	T extends Record<string, TObject | Table>,
	Mode extends "select" | "insert" | undefined,
>(
	models: T,
	mode?: Mode,
): { [K in keyof T]: Spread<T[K], Mode> } => {
	return Object.fromEntries(
		Object.entries(models).map(([key, value]) => [key, spread(value, mode)]),
	) as any;
};
