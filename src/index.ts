import app from "./app";

app.listen({
	port: 3000,
	hostname: "localhost",
	development: true,
	reusePort: true,
});

console.log(
	`🦊 Elysia is running at ${app.server?.hostname}:${app.server?.port}`,
);
