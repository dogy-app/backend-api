import env from "@/env";
import {
	RequiresRolePrivilegeError,
	registerAuthErrors,
} from "@/lib/errors/auth";
import jwt from "@elysiajs/jwt";
import { Elysia } from "elysia";
import { retrieveDataFromPayload } from "./handlers";

const authPlugin = new Elysia({ name: "auth/plugin" })
	.use(jwt({ name: "jwt", secret: env.CLERK_SECRET_KEY }))
	.use(registerAuthErrors)
	.derive(async ({ headers }) => {
		const { role, userId } = await retrieveDataFromPayload(headers);
		return { role, userId };
	})
	.macro({
		requiresRole(userRole: string) {
			return {
				beforeHandle({ role }) {
					if (userRole !== role) throw new RequiresRolePrivilegeError();
				},
			};
		},
	})
	.as("plugin");

export default authPlugin;
