import env from "@/env";
import { drizzle } from "drizzle-orm/node-postgres";
import * as schema from "./schema";

export const db = drizzle(env.DATABASE_CONNECTION_STRING, { schema });

export type db = typeof db;
export default db;
