import { swagger } from "@elysiajs/swagger";
import { Elysia } from "elysia";

import { registerAuthErrors } from "./routes/users/auth/auth.error";
import authPlugin from "./routes/users/auth/auth.plugin";

const app = new Elysia()
	.use(swagger())
	.use(registerAuthErrors)
	.use(authPlugin)
	.get("/", ({ userId, role }) => {
		return {
			user: userId,
			role: role,
		};
	})
	.listen(3000);

console.log(
	`🦊 Elysia is running at ${app.server?.hostname}:${app.server?.port}`,
);
