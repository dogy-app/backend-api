import env from "@/env";
import { importSPKI, jwtVerify } from "jose";
import { EmptyCredentialsError, InvalidCredentialsError } from "./auth.error";
import type { ClerkJWTPayload } from "./auth.model";

export async function verifyClerkJWT(token: string) {
	try {
		if (!token) throw new EmptyCredentialsError();
		const publicKey = await importSPKI(env.CLERK_JWT_PUBLIC_KEY, "RS256");

		const { payload } = await jwtVerify(token, publicKey);
		if (!payload) throw new InvalidCredentialsError();

		return payload as unknown as ClerkJWTPayload;
	} catch (e) {
		if (e instanceof InvalidCredentialsError) throw e;
	}
}
