package users

import (
	"github.com/gofiber/fiber/v2"

	"github.com/dogy-app/backend-api/api"
)

type UserService struct{}

var _ api.ServerInterface = (*UserService)(nil)

func (h *UserService) GetApiV1UsersById(c *fiber.Ctx) error {
	return c.JSON(fiber.Map{
		"message": "Successfully retrieved user",
	})
}
