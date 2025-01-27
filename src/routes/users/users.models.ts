import { createUserSchema } from "@/db/schema/user";
import { createUserSubscriptionSchema } from "@/db/schema/userSubscription";
import { t } from "elysia";

export const createFullUserSchema = t.Intersect([
	createUserSchema,
	t.Object({
		subscription: createUserSubscriptionSchema,
	}),
]);

export const patchUserBaseSchema = t.Partial(createUserSchema);
export const patchUserSubscriptionSchema = t.Partial(
	createUserSubscriptionSchema,
);

export type CreateFullUserSchema = typeof createFullUserSchema.static;
export type PatchUserBaseSchema = typeof patchUserBaseSchema.static;
export type PatchUserSubscriptionSchema =
	typeof patchUserSubscriptionSchema.static;
