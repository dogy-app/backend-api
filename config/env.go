package config

import (
	"log/slog"
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	Port string
}

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	slog.Warn("Environment variable not set, using default value", "warning", key)
	return fallback
}

var Env = initConfig()

func initConfig() Config {
	godotenv.Load()
	return Config{
		Port: getEnv("PORT", "8080"),
	}
}
