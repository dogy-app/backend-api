package config

import (
	"log/slog"
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	AppEnvironment string
	Port           string
	DatabaseURI    string
	ClerkJWTCert   string
}

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	slog.Warn("Environment variable not set, using default value", "warning", key)
	return fallback
}

func getEnvRequired(key string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	slog.Error("Environment variable not set", "error", key)
	return ""
}

// func loadProductionSecrets() Config {
//     return Config{
//         AppEnvironment: getEnv("APP_ENVIRONMENT", "production"),
//         Port:           getEnv("PORT", "8080"),
//     }
// }

var Env = initConfig()

func initConfig() Config {
	godotenv.Load()
	// if getEnv("APP_ENVIRONMENT", "development") == "production" {
	//     return loadProductionSecrets()
	// }
	return Config{
		AppEnvironment: getEnv("APP_ENVIRONMENT", "development"),
		Port:           getEnv("PORT", "8080"),
		DatabaseURI:    getEnvRequired("DATABASE_CONNECTION_STRING"),
		ClerkJWTCert:   getEnvRequired("CLERK_JWT_CERT"),
	}
}
