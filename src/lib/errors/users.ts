import { CONFLICT, NOT_FOUND } from "@/lib/status-codes";
import { Elysia } from "elysia";
import { DogyAPIException } from "./core";

export class UserNotFoundError extends DogyAPIException {
	constructor(userId: string) {
		super(`User ${userId} not found. Provide a valid user ID.`);
		this.name = "UserNotFoundError";
		this.statusCode = NOT_FOUND;

		Object.setPrototypeOf(this, UserNotFoundError.prototype);
	}
}

export class UserAlreadyExistsError extends DogyAPIException {
	constructor(userId: string) {
		super(`User ${userId} already exists. Provide a unique user ID.`);
		this.name = "UserAlreadyExistsError";
		this.statusCode = CONFLICT;

		Object.setPrototypeOf(this, UserAlreadyExistsError.prototype);
	}
}

export const registerUsersErrors = new Elysia()
	.error({
		UserNotFoundError,
		UserAlreadyExistsError,
	})
	.onError(({ code, error, set }) => {
		switch (code) {
			case "UserNotFoundError":
				set.status = error.statusCode;
				return error.toJSON();
			case "UserAlreadyExistsError":
				set.status = error.statusCode;
				return error.toJSON();
		}
	})
	.as("global");
