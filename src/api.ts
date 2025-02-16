import { Elysia, t } from "elysia";
import apiRoutes from "./routes";

export const api = new Elysia()
	.model({
		healthcheck: t.Object({
			message: t.String({
				description: "Message if the server is running",
				example: "Welcome to Dogy API",
			}),
		}),
	})
	.get(
		"/",
		() => ({
			message: "Welcome to Dogy API",
		}),
		{
			response: "healthcheck",
			tags: ["Health check"],
		},
	)
	.group("/api/v1", (app) => app.use(apiRoutes));
