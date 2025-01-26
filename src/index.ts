import { jwt } from "@elysiajs/jwt";
import { swagger } from "@elysiajs/swagger";
import { Elysia } from "elysia";
import env from "./env";

import { NotAuthenticatedError } from "@/errors/users";
import { importSPKI, jwtVerify } from "jose";

interface ClerkJWTPayload {
	sub: string;
	iss: string;
	aud: string;
	iat: number;
	exp: number;
	jti: string;
	nbf: number;
	role: string | null;
}

async function verifyClerkJWT(token: string) {
	try {
		const publicKey = await importSPKI(env.CLERK_JWT_PUBLIC_KEY, "RS256");
		const { payload } = await jwtVerify(token, publicKey);
		return payload as unknown as ClerkJWTPayload;
	} catch (error) {
		console.error("Failed to verify JWT:", error);
		throw new Error("Invalid JWT");
	}
}

const app = new Elysia()
	.use(swagger())
	.use(jwt({ name: "jwt", secret: env.CLERK_SECRET_KEY }))
	.error({ NotAuthenticatedError })
	.onError(({ code, error, set }) => {
		switch (code) {
			case "NotAuthenticatedError":
				set.status = "Unauthorized";
				return error;
		}
	})
	.get("/", async ({ jwt, headers }) => {
		const token = headers.authorization?.split(" ")[1]; // Extract token from Authorization header
		if (!token) {
			throw new NotAuthenticatedError();
		}

		const payload = await verifyClerkJWT(token);

		return payload;
	})
	.listen(3000);

console.log(
	`🦊 Elysia is running at ${app.server?.hostname}:${app.server?.port}`,
);
