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

// func (p *PetService) GetAllPetsByUser(c *fiber.Ctx) error {
// 	ctx := context.Background()
//
// 	internalID, ok := c.Locals(utils.AuthInternalID).(uuid.UUID)
// 	if !ok {
// 		return fiber.NewError(fiber.StatusInternalServerError, "Failed to get user ID.")
// 	}
//
// 	pets, err := p.repo.GetAllPetsByUser(ctx, internalID)
// 	if err != nil {
// 		return err
// 	}
//
// 	return c.JSON(pets)
// }

func (p *PetService) DeletePet(c *fiber.Ctx) error {
	ctx := context.Background()
	paramsId := c.Params("id")
	if paramsId == "" {
		return fiber.NewError(fiber.StatusBadRequest, "Missing pet ID.")
	}

	idAsUUID, err := uuid.Parse(paramsId)
	if err != nil {
		return err
	}

	err = p.repo.DeletePetById(ctx, idAsUUID)
	if err != nil {
		return err
	}

	return c.JSON(fiber.Map{"message": "Pet deleted successfully."})
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

func (p *PetService) GetAllPetBreeds(c *fiber.Ctx) error {
	petBreeds := p.repo.GetAllPetBreeds()
	return c.JSON(petBreeds)
}

func (p *PetService) GetAllPetAggressionLevels(c *fiber.Ctx) error {
	petAggressionLevels := p.repo.GetAllPetAggressionLevels()
	return c.JSON(petAggressionLevels)
}

func (p *PetService) GetAllPetAllergies(c *fiber.Ctx) error {
	petAllergies := p.repo.GetAllPetAllergies()
	return c.JSON(petAllergies)
}

func (p *PetService) GetAllPetBehaviors(c *fiber.Ctx) error {
	petBehaviors := p.repo.GetAllPetBehaviors()
	return c.JSON(petBehaviors)
}

func (p *PetService) GetAllPetInteractions(c *fiber.Ctx) error {
	petInteractions := p.repo.GetAllPetInteractions()
	return c.JSON(petInteractions)
}

func (p *PetService) GetAllPetPersonalities(c *fiber.Ctx) error {
	petPersonalities := p.repo.GetAllPetPersonalities()
	return c.JSON(petPersonalities)
}

func (p *PetService) GetAllPetReactivities(c *fiber.Ctx) error {
	petReactivities := p.repo.GetAllPetReactivities()
	return c.JSON(petReactivities)
}
