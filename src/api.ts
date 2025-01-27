import { Elysia } from "elysia";
import apiRoutes from "./routes";

export const api = new Elysia({ prefix: "/api/v1" }).use(apiRoutes);
