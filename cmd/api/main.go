package api

import (
	"fmt"
	"log"
	"net/http"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/logger"

	"github.com/dogy-app/backend-api/database"
	"github.com/dogy-app/backend-api/middleware"
	"github.com/dogy-app/backend-api/services/users"
)

type APIServer struct {
	addr string
}

func NewAPIServer(addr string) *APIServer {
	return &APIServer{addr: addr}
}

func (s *APIServer) Start() error {
	database.ConnectDB()
	defer database.CloseDB()

	app := fiber.New(fiber.Config{
		AppName:      "Dogy API",
		Prefork:      false,
		ErrorHandler: customErrorHandler,
	})
	log.Println("Listening on", s.addr)

	app.Use(logger.New(logger.Config{
		Format: "${time} ${status} - ${method} ${path}\n",
	}))

	// --------- / ----------- //
	app.Get("/", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{"message": "Welcome to Dogy API"})
	})

	// --------- /api/v1 ----------- //
	api := app.Group("/api")
	v1 := api.Group("/v1")

	// Register routes here for v1 endpoints
	v1.Get("/", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{"message": "Welcome to Dogy API v1"})
	})

	// --------- /users ----------- //
	usersRepo := users.NewUserRepository(database.Pool)
	userSvc := users.NewUserService(database.Pool)

	usersRoutes := v1.Group("/users")
	usersRoutes.Use(middleware.ValidateToken)
	usersRoutes.Post("/:id?", userSvc.CreateUser)

	usersRoutes.Use(middleware.CurrentUserID(middleware.DBConfig{
		UserRepo: usersRepo,
	}))
	usersRoutes.Get("/:id?", userSvc.GetUserByID)
	usersRoutes.Delete("/:id?", userSvc.DeleteUser)

	if err := app.Listen(fmt.Sprintf(":%s", s.addr)); err != http.ErrServerClosed {
		log.Fatal(err)
		return err
	}
	return nil
}
