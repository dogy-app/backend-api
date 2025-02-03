package utils

type (
	userIDCtx     string
	roleCtx       string
	internalIDCtx string
)

const (
	AuthUserID     userIDCtx     = "auth_user_id"
	AuthRole       roleCtx       = "auth_role"
	AuthInternalID internalIDCtx = "auth_internal_id"
)
