import Elysia from "elysia";

const userService = new Elysia({ name: "users/service", prefix: "/users" });

export default userService;
