import { Role } from "@/lib/types";
import Elysia from "elysia";
import authPlugin from "./auth/auth.plugin";
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

const ignorePaths = {
	"/api/v1/users": "POST",
};

const userRoutes = new Elysia({
	name: "users/service",
	prefix: "/users",
})
	.use(authPlugin(ignorePaths))
	.get(
		"/:id?",
		async ({ userInternalId }) => {
			const result = await getUserById(userInternalId);
			return result;
		},
		{ checkPermissions: true },
	)
	.post(
		"/",
		async ({ body, userId }) => {
			body.externalId = userId;
			const result = await createUser(body);
			return result;
		},
		{
			body: createFullUserSchema,
			checkPermissions: true,
		},
	)
	.patch(
		"/:id?",
		async ({ body, userInternalId }) => {
			const result = await updateUser(userInternalId, body);
			return result;
		},
		{
			body: patchUserBaseSchema,
			checkPermissions: true,
		},
	)
	.patch(
		"/subscriptions/:id?",
		async ({ body, userInternalId }) => {
			const result = await updateUserSubscription(userInternalId, body);
			return result;
		},
		{
			body: patchUserSubscriptionSchema,
			checkPermissions: true,
		},
	)
	.delete(
		"/:id?",
		async ({ userInternalId }) => {
			const result = await deleteUser(userInternalId);
			return result;
		},
		{
			checkPermissions: true,
		},
	);

export default userRoutes;
