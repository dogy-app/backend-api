import { pgEnum } from "drizzle-orm/pg-core";

const genderEnum = pgEnum("gender", ["male", "female"]);

export { genderEnum };
