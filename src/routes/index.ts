import { Elysia } from "elysia";
import userRoutes from "./users/users.index";

const apiRoutes = new Elysia().use(userRoutes);

export default apiRoutes;
