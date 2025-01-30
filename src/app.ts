import { logger } from "@bogeychan/elysia-logger";
import swagger from "@elysiajs/swagger";
import { Elysia } from "elysia";
// @ts-ignore Bun can import it safely.
import packageJson from "../package.json";
import { api } from "./api";

const app = new Elysia()
	.use(
		logger({
			level: "info",
			transport: {
				target: "pino-pretty",
				options: {
					colorize: true,
				},
			},
		}),
	)
	.use(
		swagger({
			documentation: {
				info: {
					title: "Dogy Backend API",
					version: packageJson.version,
					description: `Documentation for Dogy Backend API.
                  Please message @Sheape if you have any questions.`,
				},
				tags: [
					{ name: "User", description: "User endpoints" },
					{ name: "Health check", description: "Health check endpoints" },
				],
			},
			path: "/docs",
			scalarConfig: {
				defaultHttpClient: {
					//@ts-ignore. they still use javascript for type definition.
					targetKey: "js",
					clientKey: "axios",
				},
			},
		}),
	)
	.use(api);
export default app;
