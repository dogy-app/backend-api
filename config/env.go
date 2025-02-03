package config

import (
	"log/slog"
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	Port        string
	DatabaseURI string
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

var Env = initConfig()

func initConfig() Config {
	godotenv.Load()
	return Config{
		Port:        getEnv("PORT", "8080"),
		DatabaseURI: getEnvRequired("DATABASE_CONNECTION_STRING"),
	}
}
