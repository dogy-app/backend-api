import { t } from "elysia";

const clerkJWTPayload = t.Object({
	sub: t.String(),
	iss: t.String(),
	aud: t.String(),
	iat: t.Number(),
	exp: t.Number(),
	jti: t.String(),
	nbf: t.Number(),
	role: t.Union([t.String(), t.Null()]),
});

const clerkInfo = t.Object({
	userId: t.String(),
	role: t.Union([t.String(), t.Null()]),
});

export type ClerkJWTPayload = typeof clerkJWTPayload.static;
export type ClerkInfo = typeof clerkInfo.static;
