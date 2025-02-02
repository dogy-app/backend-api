package api

import (
	"errors"

	"github.com/gofiber/fiber/v2"
)

type APIError struct {
	Message string `json:"message"`
}

func customErrorHandler(c *fiber.Ctx, err error) error {
	code := fiber.StatusInternalServerError
	var e *fiber.Error
	if errors.As(err, &e) {
		code = e.Code
	}

	return c.Status(code).JSON(APIError{Message: err.Error()})
}
