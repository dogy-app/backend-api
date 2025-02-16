import { serve } from "bun";

import app from "./app";
import env from "./env";

const port = env?.PORT;

serve({
	fetch: app.fetch,
	port,
});
