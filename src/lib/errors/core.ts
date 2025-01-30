import { INTERNAL_SERVER_ERROR } from "@/lib/status-codes";
import { t } from "elysia";

const baseErrorResponse = t.Object({
	name: t.String(),
	message: t.String(),
});

export type ErrorResponse = typeof baseErrorResponse.static;

export class DogyAPIException extends Error {
	public statusCode: number = INTERNAL_SERVER_ERROR;

	constructor(message: string) {
		super(message);
		this.name = "DogyAPIException";

		Object.setPrototypeOf(this, DogyAPIException.prototype);
	}

	public toJSON() {
		return {
			name: this.name,
			message: this.message,
		} as ErrorResponse;
	}
}
