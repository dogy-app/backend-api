import { selectUserSchema } from "@/db/schema/user";
import { createRoute, z } from "@hono/zod-openapi";
import { OK } from "stoker/http-status-codes";
import { jsonContent } from "stoker/openapi/helpers";

const tags = ["Users"];

const schemas = {
	userIdParamSchema: z.object({
		id: z
			.string()
			.length(32, "The Clerk ID must be 32 characters long.")
			.openapi({
				param: {
					name: "id",
					in: "path",
					description: "The Clerk ID of the user to retrieve.",
				},
				example: "user_2ru8ImUxicEolN1tuWBq2FeqdmV",
			}),
	}),
};

export const get = createRoute({
	path: "/{id}",
	method: "get",
	tags,
	request: {
		params: schemas.userIdParamSchema,
	},
	responses: {
		[OK]: jsonContent(selectUserSchema, "The requested user."),
	},
});
