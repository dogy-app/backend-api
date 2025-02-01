package middleware

import (
	"context"
	"crypto/rsa"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"strings"

	"github.com/golang-jwt/jwt/v5"
)

const (
	ErrMsgEmptyToken      = "Empty token. Please provide a valid token."
	ErrMsgInvalidToken    = "Invalid token. Please provide a valid token."
	ErrMsgInvalidAuthType = "Invalid authentication type. Please provide a valid token."
)

type ErrorResponse struct {
	Message string `json:"message"`
}

func ErrorAuth(w http.ResponseWriter, msg string) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Add("WWW-Authenticate", "Bearer realm=\"Restricted\"")
	w.WriteHeader(http.StatusUnauthorized)
	json.NewEncoder(w).Encode(ErrorResponse{Message: msg})
}

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

func validateHeader(w http.ResponseWriter, header string) (string, bool) {
	// Check if the Authorization header is empty
	if header == "" {
		ErrorAuth(w, ErrMsgEmptyToken)
		return "", false
	}

	var authToken []string = strings.Split(header, " ")
	if len(authToken) != 2 {
		ErrorAuth(w, ErrMsgInvalidToken)
		return "", false
	}

	if authToken[0] != "Bearer" {
		ErrorAuth(w, ErrMsgInvalidAuthType)
		return "", false
	}
	return authToken[1], true
}

// ValidateToken
func ValidateToken(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		slog.Debug("Validating token...")
		authHeader := r.Header.Get("Authorization")
		authToken, ok := validateHeader(w, authHeader)

		if !ok {
			return
		}

		publicKey, err := importPublicKey("public_key.pem")
		if err != nil {
			slog.Error("Error importing public key.")
		}

		authClaims, err := verifyJWT(authToken, publicKey)
		if err != nil || authClaims.Subject == "" {
			ErrorAuth(w, ErrMsgInvalidToken)
			return
		}

		ctx := context.WithValue(r.Context(), "middleware.auth.id", authClaims.Subject)
		ctx = context.WithValue(ctx, "middleware.auth.role", safeDereference(authClaims.Role))
		req := r.WithContext(ctx)

		slog.Debug("Token validated.")
		next.ServeHTTP(w, req)
	})
}
