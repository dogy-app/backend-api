import { DogyAPIException } from "@/lib/error";
import HTTPStatusCode from "@/lib/status-codes";
import { Elysia } from "elysia";

export class InvalidCredentialsError extends DogyAPIException {
	constructor() {
		super("Invalid credentials. Please provide a valid token.");
		this.name = "InvalidCredentialsError";
		this.statusCode = HTTPStatusCode.UNAUTHORIZED;

		Object.setPrototypeOf(this, InvalidCredentialsError.prototype);
	}
}

export class EmptyCredentialsError extends DogyAPIException {
	constructor() {
		super("Empty credentials. Please provide a valid token.");
		this.name = "EmptyCredentialsError";
		this.statusCode = HTTPStatusCode.UNAUTHORIZED;

		Object.setPrototypeOf(this, EmptyCredentialsError.prototype);
	}
}

export class InvalidAuthenticationType extends DogyAPIException {
	constructor() {
		super(
			"Invalid authentication type. Authentication type must be Bearer token.",
		);
		this.name = "InvalidAuthenticationType";
		this.statusCode = HTTPStatusCode.UNAUTHORIZED;

		Object.setPrototypeOf(this, InvalidAuthenticationType.prototype);
	}
}

export const registerAuthErrors = new Elysia()
	.error({
		InvalidCredentialsError,
		EmptyCredentialsError,
		InvalidAuthenticationType,
	})
	.onError(({ code, error, set }) => {
		set.headers["www-authenticate"] = "Bearer";
		switch (code) {
			case "InvalidCredentialsError":
				set.status = error.statusCode;
				return error.toJSON();
			case "EmptyCredentialsError":
				set.status = error.statusCode;
				return error.toJSON();
			case "InvalidAuthenticationType":
				set.status = error.statusCode;
				return error.toJSON();
		}
	})
	.as("global");
