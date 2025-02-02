package middleware

import (
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/logger"
)

const (
	maxLogLength = 200
)

func truncateString(s string, maxLength int) string {
	if len(s) <= maxLength {
		return s
	}
	return s[:maxLength]
}

type LogEntry struct {
	Timestamp  string `json:"timestamp"`
	Level      string `json:"level"`
	Method     string `json:"method"`
	Endpoint   string `json:"endpoint"`
	StatusCode int    `json:"status_code"`
	Request    string `json:"request"`
	Response   string `json:"response"`
}

func Logger(c *fiber.Ctx) error {
	logger.New(logger.Config{
		Format: "${time} ${status} - ${method} ${path}\n",
	})
	return c.Next()
}
