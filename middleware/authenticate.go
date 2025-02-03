package middleware

import (
	"crypto/rsa"
	"fmt"
	"log"
	"log/slog"
	"os"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/golang-jwt/jwt/v5"
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

func safeDereference(s *string) *string {
	if s == nil {
		return nil
	}
	return s
}

func importPublicKey(path string) (*rsa.PublicKey, error) {
	publicKeyFile, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("Error opening public key file: %v", err)
	}
	key, err := jwt.ParseRSAPublicKeyFromPEM(publicKeyFile)
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

type keyType struct{}

var (
	AuthUserId   keyType
	AuthUserRole keyType
)

// ValidateToken
func ValidateToken(c *fiber.Ctx) error {
	log.Println("Validating token...")
	authHeader := c.Get("Authorization")

	authToken, err := validateHeader(authHeader)
	if err != nil {
		c.Set("WWW-Authenticate", "Bearer realm=\"Restricted\"")
		return err
	}

	publicKey, err := importPublicKey("public_key.pem")
	if err != nil {
		slog.Error("Error importing public key.")
	}

	authClaims, err := verifyJWT(authToken, publicKey)
	if err != nil || authClaims.Subject == "" {
		return fiber.NewError(fiber.StatusUnauthorized, ErrMsgInvalidToken)
	}

	c.Locals(AuthUserId, authClaims.Subject)
	c.Locals(AuthUserRole, safeDereference(authClaims.Role))

	slog.Debug("Token validated.")
	return c.Next()
}
