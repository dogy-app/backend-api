import { describe, expect, test } from "bun:test";
import {
	EmptyCredentialsError,
	InvalidCredentialsError,
} from "@/lib/errors/auth";
import { inspect } from "bun";
import { Elysia } from "elysia";
import { verifyClerkJWT } from "./handlers";
import authPlugin from "./plugin";

declare module "bun" {
	interface Env {
		CLERK_JWT_TOKEN: string;
	}
}

describe("Auth", () => {
	test("empty token", async () => {
		expect(verifyClerkJWT("")).rejects.toThrow(EmptyCredentialsError);
	});
	test("invalid token", async () => {
		expect(verifyClerkJWT("ehjakr")).rejects.toThrow(InvalidCredentialsError);
	});
	test("invalid long token", async () => {
		expect(
			verifyClerkJWT(
				"ttest1test1test1test1test1test1test1test1test1test1test1test1est1",
			),
		).rejects.toThrow(InvalidCredentialsError);
	});
	test("valid token (non-admin)", async () => {
		expect(verifyClerkJWT(process.env.CLERK_JWT_TOKEN)).resolves.toEqual({
			azp: "https://neat-cat-12.accounts.dev",
			exp: 2053148066,
			iat: 1737788066,
			iss: "https://neat-cat-12.clerk.accounts.dev",
			jti: "eff3b3fcd8716c5407e7",
			nbf: 1737788061,
			role: null,
			sub: "user_2ruHSXCzfIRreR2tpttVQBl512a",
		});
	});
});

describe("Auth (Plugin integration)", () => {
	const app = new Elysia().use(authPlugin).get("/", ({ userId, role }) => {
		return {
			user: userId,
			role: role,
		};
	});

	test("no token provided", async () => {
		const response = await app.handle(new Request("http://localhost/"));

		const responseContent = await response.json();
		expect(response.status).toBe(401);
		expect(responseContent.message).toBe(
			"Empty credentials. Please provide a valid token.",
		);
		expect(response.headers.get("www-authenticate")).toBe("Bearer");
	});

	test("empty token", async () => {
		const response = await app.handle(
			new Request("http://localhost/", { headers: { Authorization: "" } }),
		);
		const responseContent = await response.json();
		expect(response.status).toBe(401);
		expect(responseContent.message).toBe(
			"Empty credentials. Please provide a valid token.",
		);
		expect(response.headers.get("www-authenticate")).toBe("Bearer");
	});

	test("invalid token without Bearer keyword", async () => {
		const response = await app.handle(
			new Request("http://localhost/", {
				headers: { Authorization: "test1" },
			}),
		);
		const responseContent = await response.json();
		expect(response.status).toBe(401);
		expect(responseContent.message).toBe(
			"Invalid authentication type. Authentication type must be Bearer token.",
		);
		expect(response.headers.get("www-authenticate")).toBe("Bearer");
	});

	test("invalid token with Bearer keyword", async () => {
		const response = await app.handle(
			new Request("http://localhost/", {
				headers: { Authorization: "Bearer test1" },
			}),
		);
		const responseContent = await response.json();
		expect(response.status).toBe(401);
		expect(responseContent.message).toBe(
			"Invalid credentials. Please provide a valid token.",
		);
		expect(response.headers.get("www-authenticate")).toBe("Bearer");
	});

	test("valid token (non-admin)", async () => {
		const response = await app.handle(
			new Request("http://localhost/", {
				headers: { Authorization: `Bearer ${process.env.CLERK_JWT_TOKEN}` },
			}),
		);
		const responseContent = await response.json();
		expect(response.status).toBe(200);
		expect(responseContent).toEqual({
			user: "user_2ruHSXCzfIRreR2tpttVQBl512a",
			role: null,
		});
	});
});
