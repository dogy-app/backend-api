import app from "./app";

app.listen({
	port: 3000,
	hostname: "localhost",
});

console.log(
	`🦊 Elysia is running at ${app.server?.hostname}:${app.server?.port}`,
);
