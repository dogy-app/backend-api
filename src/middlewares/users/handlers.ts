import db from "@/db";
import { user } from "@/db/schema";
import { DogyAPIException } from "@/lib/errors/core";
import { UserNotFoundError } from "@/lib/errors/users";
import { eq } from "drizzle-orm";

export async function getInternalIdFromExternalId(externalId: string) {
	try {
		const userRecord = await db.query.user.findFirst({
			where: eq(user.externalId, externalId),
			columns: {
				id: true,
			},
		});
		if (!userRecord) throw new UserNotFoundError(externalId);
		return userRecord.id;
	} catch (e) {
		if (e instanceof UserNotFoundError) throw e;
		throw new DogyAPIException(
			"User not found. Please message @Sheape to fix error handling.",
		);
	}
}
