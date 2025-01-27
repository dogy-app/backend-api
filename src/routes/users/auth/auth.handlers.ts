import env from "@/env";
import { DogyAPIException } from "@/lib/error";
import { JWSInvalid, importSPKI, jwtVerify } from "jose";
import { EmptyCredentialsError, InvalidCredentialsError } from "./auth.errors";
import type { ClerkJWTPayload } from "./auth.models";

export async function verifyClerkJWT(token: string) {
	try {
		if (!token) throw new EmptyCredentialsError();
		const publicKey = await importSPKI(env.CLERK_JWT_PUBLIC_KEY, "RS256");

		const { payload } = await jwtVerify(token, publicKey);
		return payload as unknown as ClerkJWTPayload;
	} catch (e) {
		if (
			e instanceof InvalidCredentialsError ||
			e instanceof EmptyCredentialsError
		)
			throw e;

		if (e instanceof JWSInvalid) throw new InvalidCredentialsError();

		throw new DogyAPIException(
			"Invalid JWT token. Please message @Sheape to fix error handling.",
		);
	}
}
