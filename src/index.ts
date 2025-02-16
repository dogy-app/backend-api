import { serve } from "bun";

import app from "./app";
import env from "./env";

app.listen({
	port: 3000,
	hostname: "localhost",
	development: true,
	reusePort: true,
});
