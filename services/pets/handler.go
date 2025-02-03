package pets

import (
	"context"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/dogy-app/backend-api/utils"
)

type PetService struct {
	repo *PetRepository
}

func NewPetService(db *pgxpool.Pool) *PetService {
	return &PetService{repo: NewPetRepository(db)}
}

func (p *PetService) GetAllPetBreeds(c *fiber.Ctx) error {
	petBreeds, err := p.repo.GetAllPetBreeds()
	if err != nil {
		return err
	}
	return c.JSON(petBreeds)
}

func (p *PetService) CreatePet(c *fiber.Ctx) error {
	req := new(CreatePetRequest)
	if err := c.BodyParser(req); err != nil {
		return err
	}

	ctx := context.Background()
	internalID, ok := c.Locals(utils.AuthInternalID).(uuid.UUID)
	if !ok {
		return fiber.NewError(fiber.StatusInternalServerError, "Failed to get user ID.")
	}

	response, err := p.repo.CreatePet(ctx, req, internalID)
	if err != nil {
		return err
	}

	return c.JSON(response)
}
