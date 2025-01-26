export class NotAuthenticatedError extends Error {
	constructor() {
		super("You are not authenticated. Please provide a valid token.");
		this.name = "NotAuthenticatedError";
	}
}
