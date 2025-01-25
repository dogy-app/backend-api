import env from "@/env";
import { drizzle } from "drizzle-orm/node-postgres";

export const db = drizzle(env.DATABASE_CONNECTION_STRING);

export type db = typeof db;
export default db;
