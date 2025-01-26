import { t } from "elysia";
import HTTPStatusCode from "./status-codes";

const baseErrorResponse = t.Object({
	message: t.String(),
});

export type ErrorResponse = typeof baseErrorResponse.static;

export class DogyAPIException extends Error {
	public statusCode: number = HTTPStatusCode.INTERNAL_SERVER_ERROR;

	constructor(message: string) {
		super(message);
		this.name = "DogyAPIException";

		Object.setPrototypeOf(this, DogyAPIException.prototype);
	}

	public toJSON() {
		return {
			message: this.message,
		} as ErrorResponse;
	}
}
