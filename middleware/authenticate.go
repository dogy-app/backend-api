package middleware

import (
	"context"
	"crypto/rsa"
	"fmt"
	"log"
	"log/slog"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"

	"github.com/dogy-app/backend-api/config"
	"github.com/dogy-app/backend-api/services/users"
	"github.com/dogy-app/backend-api/utils"
)

const (
	ErrMsgEmptyToken      = "Empty token. Please provide a valid token."
	ErrMsgInvalidToken    = "Invalid token. Please provide a valid token."
	ErrMsgInvalidAuthType = "Invalid authentication type. Please provide a valid token."
)

type ClerkAuthClaims struct {
	Role *string `json:"role"`
	jwt.RegisteredClaims
}

func safeDereference(s *string) string {
	if s == nil {
		return ""
	}
	return *s
}

func importPublicKey(publicKeyStr string) (*rsa.PublicKey, error) {
	key, err := jwt.ParseRSAPublicKeyFromPEM([]byte(publicKeyStr))
	if err != nil {
		return nil, fmt.Errorf("Error parsing public key: %v", err)
	}
	return key, nil
}

// Parsing JWT
func verifyJWT(tokenString string, publicKey *rsa.PublicKey) (*ClerkAuthClaims, error) {
	slog.Debug("Parsing jwt token...")
	token, err := jwt.ParseWithClaims(
		tokenString,
		&ClerkAuthClaims{},
		func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodRSA); !ok {
				return nil, fmt.Errorf("Unexpected signing method: %v", token.Header["alg"])
			}
			return publicKey, nil
		},
	)
	if err != nil {
		slog.Error("Error parsing token")
	} else if _, ok := token.Claims.(*ClerkAuthClaims); ok && token.Valid {
		slog.Debug("Token is valid!!")
		return token.Claims.(*ClerkAuthClaims), nil
	} else {
		slog.Debug("Token is invalid!!")
		return &ClerkAuthClaims{}, err
	}

	return &ClerkAuthClaims{}, err
}

func validateHeader(header string) (string, error) {
	// Check if the Authorization header is empty
	if header == "" {
		log.Println(ErrMsgEmptyToken)
		return "", fiber.NewError(fiber.StatusUnauthorized, ErrMsgEmptyToken)
	}

	var authToken []string = strings.Split(header, " ")
	if len(authToken) != 2 {
		log.Println(ErrMsgInvalidToken)
		return "", fiber.NewError(fiber.StatusUnauthorized, ErrMsgInvalidToken)
	}

	if authToken[0] != "Bearer" {
		log.Println(ErrMsgInvalidAuthType)
		return "", fiber.NewError(fiber.StatusUnauthorized, ErrMsgInvalidAuthType)
	}
	return authToken[1], nil
}

// ValidateToken
func ValidateToken(c *fiber.Ctx) error {
	log.Println("Validating token...")
	authHeader := c.Get("Authorization")

	authToken, err := validateHeader(authHeader)
	if err != nil {
		c.Set("WWW-Authenticate", "Bearer realm=\"Restricted\"")
		return err
	}

	publicKey, err := importPublicKey(config.Env.ClerkJWTCert)
	if err != nil {
		slog.Error("Error importing public key.")
	}

	authClaims, err := verifyJWT(authToken, publicKey)
	if err != nil || authClaims.Subject == "" {
		return fiber.NewError(fiber.StatusUnauthorized, ErrMsgInvalidToken)
	}

	c.Locals(utils.AuthUserID, authClaims.Subject)
	// c.Locals(utils.AuthRole, safeDereference(authClaims.Role))

	log.Println(authClaims.Subject)
	// log.Println(safeDereference(authClaims.Role))
	slog.Debug("Token validated.")
	return c.Next()
}

type DBConfig struct {
	UserRepo *users.UserRepository
}

func CurrentUserID(config DBConfig) fiber.Handler {
	return func(c *fiber.Ctx) error {
		userID, ok := c.Locals(utils.AuthUserID).(string)
		// role, _ := c.Locals(utils.AuthUserID).(string)
		log.Println("User ID: ", userID)
		// log.Println("User Role: ", role)

		if !ok {
			return fiber.NewError(
				fiber.StatusNotFound,
				"User internal ID not found. Invalid JWT Token.",
			)
		}
		ctx := context.Background()
		paramsId := c.Params("id")

		var internalID uuid.UUID
		var err error
		if paramsId != "" {
			_internalID, _err := config.UserRepo.GetInternalID(ctx, paramsId)
			internalID = _internalID
			err = _err
		} else {
			_internalID, _err := config.UserRepo.GetInternalID(ctx, userID)
			internalID = _internalID
			err = _err
		}

		if internalID == uuid.Nil {
			return fiber.NewError(
				fiber.StatusNotFound,
				"User internal ID not found on the database.",
			)
		}

		if err != nil {
			return fiber.NewError(fiber.StatusInternalServerError, "Failed to get user ID.")
		}

		c.Locals(utils.AuthInternalID, internalID)
		return c.Next()
	}
}
