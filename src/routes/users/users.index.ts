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
import userPlugin from "./users.plugin";

const userRoutes = new Elysia({
	name: "users/service",
	prefix: "/users",
})
	.use(userPlugin)
	.get(
		"/:id?",
		async ({ internalUserId }) => {
			const result = await getUserById(internalUserId);
			return result;
		},
		{ internalUserId: true },
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
