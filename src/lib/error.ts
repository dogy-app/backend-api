import HTTPStatusCode from "./status-codes";

export class DogyAPIException extends Error {
	public statusCode: number = HTTPStatusCode.INTERNAL_SERVER_ERROR;

	constructor(message: string) {
		super(message);
		this.name = "DogyAPIException";

		Object.setPrototypeOf(this, DogyAPIException.prototype);
	}
}
