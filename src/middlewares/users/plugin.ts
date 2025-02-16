import { RequiresRolePrivilegeError } from "@/lib/errors/auth";
import { Role } from "@/lib/types";
import authPlugin from "@/middlewares/auth/plugin";

import { Elysia, t } from "elysia";
import { getInternalIdFromExternalId } from "./handlers";

const userPlugin = new Elysia({ name: "users/plugin" })
	.use(authPlugin)
	.guard({
		params: t.Object({
			id: t.Number(),
		}),
	})
	.resolve(async ({ userId, params }) => {
		if (!userId) return;
		const internalUserId = await getInternalIdFromExternalId(userId);
		return { internalUserId };
	})
	//.macro({
	//	internalUserId(enabled: boolean) {
	//		if (!enabled) return;
	//		return {
	//			async resolve({ userId }) {
	//				if (!userId) return;
	//				const internalUserId = await getInternalIdFromExternalId(userId);
	//				return {
	//					internalUserId: internalUserId,
	//				};
	//			},
	//		};
	//	},
	//})
	.macro({
		checkPermissionsFor(inputUserId: string) {
			return {
				beforeHandle({ userId, role }) {
					if (!inputUserId) return;
					if (role === Role.ADMIN) return;
					if (userId !== inputUserId) throw new RequiresRolePrivilegeError();
				},
			};
		},
	})
	.as("plugin");

export default userPlugin;
