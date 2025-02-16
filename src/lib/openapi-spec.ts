import { apiReference } from "@scalar/hono-api-reference";

import type { AppOpenAPI } from "./types";

//@ts-ignore since we're using bun runtime anyways.
import packageMetadata from "../../package.json";

export default function configureOpenAPI(app: AppOpenAPI) {
	app.doc("/openapi.json", {
		openapi: "3.0.0",
		info: {
			version: packageMetadata.version,
			title: "Dogy Backend API",
		},
	});

	app.get(
		"/docs",
		apiReference({
			theme: "kepler",
			defaultHttpClient: {
				targetKey: "js",
				clientKey: "axios",
			},
			spec: {
				url: "/openapi.json",
			},
		}),
	);
}
