package users

import (
	"context"
	"errors"
	"log"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/dogy-app/backend-api/utils"
)

type UserService struct {
	repo *UserRepository
}

func NewUserService(db *pgxpool.Pool) *UserService {
	return &UserService{repo: NewUserRepository(db)}
}

func (s *UserService) GetUserByID(c *fiber.Ctx) error {
	ctx := context.Background()
	internalID, ok := c.Locals(utils.AuthInternalID).(uuid.UUID)
	if !ok {
		return fiber.NewError(fiber.StatusInternalServerError, "Failed to get user ID.")
	}

	userResponse, err := s.repo.GetUser(ctx, internalID)
	if err != nil {
		return fiber.NewError(fiber.StatusInternalServerError, "Failed to get user.")
	}

	return c.JSON(userResponse)
}

func (s *UserService) CreateUser(c *fiber.Ctx) error {
	req := new(CreateUserRequest)
	if err := c.BodyParser(req); err != nil {
		return err
	}

	userID, ok := c.Locals(utils.AuthUserID).(string)
	log.Println(userID)
	if !ok {
		return fiber.NewError(fiber.StatusInternalServerError, "Failed to get user ID.")
	}

	ctx := context.Background()
	userResponse, err := s.repo.CreateUser(ctx, req, userID)
	if err != nil {
		var pgErr *pgconn.PgError
		if ok := errors.As(err, &pgErr); ok {
			if pgErr.Code == "23505" {
				return fiber.NewError(
					fiber.StatusConflict,
					"Cannot create user. User already exists",
				)
			}
		}
		return fiber.NewError(fiber.StatusInternalServerError, "Failed to create user.")
	}

	log.Println(userResponse)
	return c.JSON(userResponse)
}

func (s *UserService) DeleteUser(c *fiber.Ctx) error {
	ctx := context.Background()
	internalID, ok := c.Locals(utils.AuthInternalID).(uuid.UUID)
	if !ok {
		return fiber.NewError(fiber.StatusInternalServerError, "Failed to get user ID.")
	}
	err := s.repo.DeleteUser(ctx, internalID)
	if err != nil {
		return fiber.NewError(fiber.StatusInternalServerError, "Failed to delete user.")
	}
	return c.JSON(fiber.Map{"message": "User deleted successfully."})
}
