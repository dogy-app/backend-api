package pets

import (
	"context"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/shopspring/decimal"

	"github.com/dogy-app/backend-api/database/repository"
)

type PetRepository struct {
	db *pgxpool.Pool
}

func NewPetRepository(db *pgxpool.Pool) *PetRepository {
	return &PetRepository{db: db}
}

func (r *PetRepository) GetAllPetBreeds() ([]repository.PetBreed, error) {
	return repository.AllPetBreedValues(), nil
}

// TODO: Refactor and isolate into smaller functions
func (r *PetRepository) CreatePet(
	ctx context.Context,
	pet *CreatePetRequest,
	userId uuid.UUID,
) (CreatePetResponse, error) {
	tx, _ := r.db.Begin(ctx)
	defer tx.Rollback(ctx)

	repo := repository.New(tx)
	birthday, err := time.Parse("2006-01-02", pet.Birthday)
	if err != nil {
		return CreatePetResponse{}, err
	}

	weight, err := decimal.NewFromString(pet.Weight)
	if err != nil {
		return CreatePetResponse{}, err
	}
	petBase, err := repo.CreateBasePet(ctx, repository.CreateBasePetParams{
		Name:     pet.Name,
		Birthday: birthday,
		PhotoUrl: pet.PhotoURL,
		Size:     repository.PetSize(pet.Size),
		Gender:   pet.Gender,
		Weight:   weight,
	})
	if err != nil {
		return CreatePetResponse{}, err
	}

	petAttrBase, err := repo.CreateBasePetAttr(ctx, repository.CreateBasePetAttrParams{
		PetID:        petBase.ID,
		IsSterilized: pet.Attributes.IsSterilized,
	})
	if err != nil {
		return CreatePetResponse{}, err
	}

	for _, aggressionLevel := range pet.Attributes.AggressionLevels {
		err = repo.CreatePetAttrAggressionLevel(ctx, repository.CreatePetAttrAggressionLevelParams{
			PetAttrID:       petAttrBase.ID,
			AggressionLevel: repository.PetAggressionLevel(aggressionLevel),
		})
		if err != nil {
			return CreatePetResponse{}, err
		}
	}

	for _, allergy := range pet.Attributes.Allergies {
		err = repo.CreatePetAttrAllergy(ctx, repository.CreatePetAttrAllergyParams{
			PetAttrID: petAttrBase.ID,
			Allergy:   repository.PetAllergy(allergy),
		})
		if err != nil {
			return CreatePetResponse{}, err
		}
	}

	for _, breed := range pet.Attributes.Breeds {
		err = repo.CreatePetAttrBreed(ctx, repository.CreatePetAttrBreedParams{
			PetAttrID: petAttrBase.ID,
			Breed:     repository.PetBreed(breed),
		})
		if err != nil {
			return CreatePetResponse{}, err
		}
	}

	for _, behavior := range pet.Attributes.Behaviors {
		err = repo.CreatePetAttrBehavior(ctx, repository.CreatePetAttrBehaviorParams{
			PetAttrID: petAttrBase.ID,
			Behavior:  repository.PetBehavior(behavior),
		})
		if err != nil {
			return CreatePetResponse{}, err
		}
	}

	for _, interaction := range pet.Attributes.Interactions {
		err = repo.CreatePetAttrInteractions(ctx, repository.CreatePetAttrInteractionsParams{
			PetAttrID:   petAttrBase.ID,
			Interaction: repository.PetInteraction(interaction),
		})
		if err != nil {
			return CreatePetResponse{}, err
		}
	}

	for _, personality := range pet.Attributes.Personalities {
		err = repo.CreatePetAttrPersonalities(ctx, repository.CreatePetAttrPersonalitiesParams{
			PetAttrID:   petAttrBase.ID,
			Personality: repository.PetPersonality(personality),
		})
		if err != nil {
			return CreatePetResponse{}, err
		}
	}

	for _, reactivity := range pet.Attributes.Reactivities {
		err = repo.CreatePetAttrReactivities(ctx, repository.CreatePetAttrReactivitiesParams{
			PetAttrID:  petAttrBase.ID,
			Reactivity: repository.PetReactivity(reactivity),
		})
		if err != nil {
			return CreatePetResponse{}, err
		}
	}

	err = repo.LinkPetToUser(ctx, repository.LinkPetToUserParams{
		PetID:       petBase.ID,
		UserID:      userId,
		IsDogOwner:  pet.IsDogOwner,
		IsDogSitter: pet.IsDogSitter,
	})
	if err != nil {
		return CreatePetResponse{}, err
	}

	if err = tx.Commit(ctx); err != nil {
		return CreatePetResponse{}, err
	}

	return CreatePetResponse{
		PetID: petBase.ID.String(),
		CreatePetRequest: CreatePetRequest{
			Name:        petBase.Name,
			Birthday:    petBase.Birthday.Format("2006-01-02"),
			PhotoURL:    petBase.PhotoUrl,
			Gender:      petBase.Gender,
			Size:        string(petBase.Size),
			Weight:      petBase.Weight.String(),
			UserPetLink: pet.UserPetLink,
			Attributes:  pet.Attributes,
		},
	}, nil
}
