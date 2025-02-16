import { UserNotFoundError, registerUsersErrors } from "@/lib/errors/users";
import { Role } from "@/lib/types";
import userPlugin from "@/middlewares/users/plugin";
import Elysia from "elysia";
import {
	createUser,
	deleteUser,
	getUserById,
	updateUser,
	updateUserSubscription,
} from "./users.handlers";
import {
	createFullUserSchema,
	patchUserBaseSchema,
	patchUserSubscriptionSchema,
} from "./users.models";

const userRoutes = new Elysia({
	name: "users/service",
	prefix: "/users",
})
	.use(userPlugin)
	.get("/:id?", async ({ params, internalUserId }) => {
		if (!params.id) throw UserNotFoundError;
		const result = await getUserById(params.id);
		return result;
	})
	.post(
		"/:id?",
		async ({ body, params, internalUserId }) => {
			if (!params.id) throw UserNotFoundError;
			body.externalId = params.id;
			const result = await createUser(body);
			return result;
		},
		{
			body: createFullUserSchema,
		},
	)
	.patch(
		"/:id?",
		async ({ body, params }) => {
			if (!params.id) throw UserNotFoundError;
			const result = await updateUser(params.id, body);
			return result;
		},
		{
			body: patchUserBaseSchema,
		},
	)
	.patch(
		"/subscriptions/:id?",
		async ({ body, params }) => {
			if (!params.id) throw UserNotFoundError;
			const result = await updateUserSubscription(params.id, body);
			return result;
		},
		{
			body: patchUserSubscriptionSchema,
		},
	)
	.delete("/:id?", async ({ params }) => {
		if (!params.id) throw UserNotFoundError;
		const result = await deleteUser(params.id);
		return result;
	});

export default userRoutes;
