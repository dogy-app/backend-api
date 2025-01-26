import config from "$/drizzle.config";
import { db } from "@/db";
import { migrate } from "drizzle-orm/node-postgres/migrator";

await migrate(db, { migrationsFolder: config.out! });
