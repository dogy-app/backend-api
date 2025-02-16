import env from "@/env";
import {
	EmptyCredentialsError,
	InvalidAuthenticationType,
	InvalidCredentialsError,
} from "@/lib/errors/auth";
import { DogyAPIException } from "@/lib/errors/core";
import { Role } from "@/lib/types";
import { JWSInvalid, importSPKI, jwtVerify } from "jose";
import type { ClerkJWTPayload } from "./models";

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

export function retrieveTokenFromHeaders(
	headers: Record<string, string | undefined>,
): string {
	try {
		if (!headers.authorization) throw new EmptyCredentialsError();
		if (headers.authorization.split(" ")[0] !== "Bearer")
			throw new InvalidAuthenticationType();
		const token = headers.authorization.split(" ")[1];
		if (!token) throw new EmptyCredentialsError();
		return token;
	} catch (e) {
		if (
			e instanceof InvalidAuthenticationType ||
			e instanceof EmptyCredentialsError
		)
			throw e;
		throw new DogyAPIException(
			"Invalid Authorization header. Please message @Sheape to fix error handling.",
		);
	}
}

export async function retrieveDataFromPayload(
	headers: Record<string, string | undefined>,
): Promise<Record<string, string>> {
	const token = retrieveTokenFromHeaders(headers);
	const payload = await verifyClerkJWT(token);
	if (!payload?.sub) throw new InvalidCredentialsError();
	const role = !payload.role ? Role.USER : payload.role;
	return { role, userId: payload.sub };
}
