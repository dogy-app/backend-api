import { envious } from "@pitininja/envious";
import { Type } from "@sinclair/typebox";

const env = envious(
	Type.Object({
		GOOGLE_API_KEY: Type.String({
			description: "Google API Key",
			minLength: 39,
			maxLength: 39,
		}),
		CLERK_SECRET_KEY: Type.String(),
		CLERK_JWT_PUBLIC_KEY: Type.String(),
		DATABASE_CONNECTION_STRING: Type.String(),
	}),
);

export default env;
