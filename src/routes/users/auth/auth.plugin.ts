import env from "@/env";
import jwt from "@elysiajs/jwt";
import { Elysia } from "elysia";
import { EmptyCredentialsError, registerAuthErrors } from "./auth.error";
import { verifyClerkJWT } from "./auth.handler";
import type { ClerkInfo } from "./auth.model";

const authPlugin = new Elysia({ name: "auth/plugin" })
	.use(jwt({ name: "jwt", secret: env.CLERK_SECRET_KEY }))
	.use(registerAuthErrors)
	.derive(async ({ headers }) => {
		if (!headers.authorization) throw new EmptyCredentialsError();
		const token = headers.authorization.split(" ")[1];
		if (!token) throw new EmptyCredentialsError();
		const payload = await verifyClerkJWT(token);
		return { userId: payload?.sub, role: payload?.role } as ClerkInfo;
	})
	.as("plugin");

export default authPlugin;
