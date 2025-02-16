import { Elysia, t } from "elysia";
import userRoutes from "./users/users.index";

const apiRoutes = new Elysia()
	.model({
		"healthcheck.v1": t.Object({
			message: t.String({
				description: "Message if the endpoint for v1 is running",
				example: "Welcome to Dogy API v1",
			}),
		}),
	})
	.get(
		"/",
		() => ({
			message: "Welcome to Dogy API v1",
		}),
		{
			detail: {
				summary: "Health check for v1",
			},
			response: "healthcheck.v1",
			tags: ["Health check"],
		},
	)
	.use(userRoutes);

export default apiRoutes;
