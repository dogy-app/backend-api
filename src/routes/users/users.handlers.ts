import db from "@/db";
import type { CreateUserSchema } from "@/db/schema/user";
import user from "@/db/schema/user";
import type { CreateUserSubscriptionSchema } from "@/db/schema/userSubscription";
import userSubscription from "@/db/schema/userSubscription";
import { eq } from "drizzle-orm";
import type {
	CreateFullUserSchema,
	PatchUserBaseSchema,
	PatchUserSubscriptionSchema,
} from "./users.models";

export async function createUser(data: CreateFullUserSchema) {
	const userSubscriptionData =
		data.subscription as unknown as CreateUserSubscriptionSchema;
	const userBase = data as CreateUserSchema;

	const createdUser = await db.transaction(async (tx) => {
		const [newUser] = await tx.insert(user).values(userBase).returning();
		const [newUserSubscription] = await tx
			.insert(userSubscription)
			.values({
				...userSubscriptionData,
				userId: newUser.id,
			})
			.returning();

		const { id: id1, updatedAt, ...userFields } = newUser;
		const { id: id2, userId, ...userSubscriptionFields } = newUserSubscription;

		return {
			...userFields,
			subscription: userSubscriptionFields,
		};
	});

	return createdUser;
}

export async function getUserById(userId: string) {
	const userRecord = await db.query.user.findFirst({
		where: eq(user.id, userId),
		columns: {
			id: false,
			updatedAt: false,
		},
		with: {
			subscription: {
				columns: {
					id: false,
					userId: false,
				},
			},
		},
	});

	return userRecord;
}

export async function updateUser(userId: string, data: PatchUserBaseSchema) {
	await db.update(user).set(data).where(eq(user.id, userId));

	return { message: "User updated successfully" };
}

export async function updateUserSubscription(
	userId: string,
	data: PatchUserSubscriptionSchema,
) {
	await db
		.update(userSubscription)
		.set(data)
		.where(eq(userSubscription.userId, userId));

	return { message: "User subscription updated successfully" };
}

export async function deleteUser(userId: string) {
	await db.delete(user).where(eq(user.id, userId));

	return { message: "User deleted successfully" };
}
