import { Role } from "@/lib/types";
import { Elysia } from "elysia";
import { RequiresRolePrivilegeError } from "./auth/auth.errors";
import authPlugin from "./auth/auth.plugin";
import { getInternalIdFromExternalId } from "./users.handlers";

const userPlugin = new Elysia({ name: "users/plugin" })
	.use(authPlugin)
	.macro({
		internalUserId(enabled: boolean) {
			if (!enabled) return;
			return {
				async resolve({ userId }) {
					if (!userId) return;
					const internalUserId = await getInternalIdFromExternalId(userId);
					return {
						internalUserId: internalUserId,
					};
				},
			};
		},
	})
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
	});

export default userPlugin;
