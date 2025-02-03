package users

import (
	"context"
	"errors"
	"log"

	"github.com/gofiber/fiber/v2"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgxpool"
)

type UserService struct {
	repo *UserRepository
}

func NewUserService(db *pgxpool.Pool) *UserService {
	return &UserService{repo: NewUserRepository(db)}
}

func (s *UserService) GetUserByID(c *fiber.Ctx) error {
	// if c.Params("id") != "" {
	// 	c.Locals()
	// }
	// return c.JSON(fiber.Map{
	// 	"externalID":    "user_2ruHSXCzfIRreR2tpttVQBl512a",
	// 	"gender":        req.Gender,
	// 	"hasOnboarded":  req.HasOnboarded,
	// 	"name":          req.Name,
	// 	"timezone":      req.Timezone,
	// 	"notifications": req.Notifications,
	// 	"subscription":  req.Subscription,
	// })
	return c.JSON(fiber.Map{
		"externalId":   "user_2ruHSXCzfIRreR2tpttVQBl512a",
		"gender":       "male",
		"hasOnboarded": false,
		"name":         "John Doe",
		"timezone":     "Europe/Sweden",
		"subscription": fiber.Map{
			"isRegistered":     false,
			"isTrialMode":      false,
			"subscriptionType": "active",
			"trialStartDate":   "2025-01-22",
		},
	})
}

func (s *UserService) CreateUser(c *fiber.Ctx) error {
	req := new(CreateUserRequest)
	if err := c.BodyParser(req); err != nil {
		return err
	}

	ctx := context.Background()
	userResponse, err := s.repo.CreateUser(ctx, req, "user_2ruHSXCzfIRreR2tpttVQBl512a")
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
	// return c.JSON(fiber.Map{
	// 	"externalId": "user_2ruHSXCzfIRreR2tpttVQBl512a",
	// })
}
