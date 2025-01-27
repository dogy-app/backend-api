import env from "@/env";
import jwt from "@elysiajs/jwt";
import { Elysia } from "elysia";
import { RequiresRolePrivilegeError, registerAuthErrors } from "./auth.errors";
import { retrieveDataFromPayload } from "./auth.handlers";

const authPlugin = new Elysia({ name: "auth/plugin" })
	.use(jwt({ name: "jwt", secret: env.CLERK_SECRET_KEY }))
	.use(registerAuthErrors)
	.derive({ as: "scoped" }, async ({ headers }) => {
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
	});

export default authPlugin;
