import swagger from "@elysiajs/swagger";
import { Elysia } from "elysia";
import { api } from "./api";

const app = new Elysia().use(swagger()).use(api);
export default app;
