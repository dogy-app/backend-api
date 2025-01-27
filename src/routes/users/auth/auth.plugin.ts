import env from "@/env";
import { Role } from "@/lib/types";
import jwt from "@elysiajs/jwt";
import { Elysia } from "elysia";
import { getInternalIdFromExternalId } from "../users.handlers";
import {
	EmptyCredentialsError,
	InvalidAuthenticationType,
	InvalidCredentialsError,
	RequiresRolePrivilegeError,
	registerAuthErrors,
} from "./auth.errors";
import { verifyClerkJWT } from "./auth.handlers";

const authPlugin = (ignorePaths: Record<string, string>) =>
	new Elysia({ name: "auth/plugin" })
		.use(jwt({ name: "jwt", secret: env.CLERK_SECRET_KEY }))
		.use(registerAuthErrors)
		.derive(async ({ headers, params, path, request }) => {
			if (!headers.authorization) throw new EmptyCredentialsError();
			if (headers.authorization.split(" ")[0] !== "Bearer")
				throw new InvalidAuthenticationType();
			const token = headers.authorization.split(" ")[1];
			if (!token) throw new EmptyCredentialsError();
			const payload = await verifyClerkJWT(token);
			if (!payload?.sub) throw new InvalidCredentialsError();
			const role = !payload.role ? Role.USER : payload.role;
			if (ignorePaths[path] === request.method) {
				return {
					userId: payload.sub,
					internalId: "",
					userInternalId: "",
					role,
				};
			}
			const internalId = await getInternalIdFromExternalId(payload.sub);
			// Might cause error if the user doesn't exist on db but the path is
			// post /users/
			if (!internalId) {
				throw new InvalidCredentialsError();
			}

			//@ts-ignore
			const userInternalId = !params.id
				? internalId
				: //@ts-ignore
					await getInternalIdFromExternalId(params.id);

			// TODO: Add a check to see if the user exist.
			if (!userInternalId) throw new InvalidCredentialsError();
			return { internalId, userInternalId, role };
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
		.macro({
			checkPermissions(enabled: boolean) {
				return {
					beforeHandle({ internalId, userInternalId, role }) {
						if (!enabled) return;
						if (role === Role.ADMIN) return;
						if (internalId !== userInternalId)
							throw new RequiresRolePrivilegeError();
					},
				};
			},
		})
		.as("plugin");

export default authPlugin;
