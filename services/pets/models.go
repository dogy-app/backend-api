package pets

import "github.com/dogy-app/backend-api/database/repository"

type (
	UserPetLink struct {
		IsDogOwner  bool `json:"isDogOwner"`
		IsDogSitter bool `json:"isDogSitter"`
	}
	PetAttr struct {
		AggressionLevels []repository.PetAggressionLevel `json:"aggressionLevels"`
		Allergies        []repository.PetAllergy         `json:"allergies"`
		Behaviors        []repository.PetBehavior        `json:"behaviors"`
		Breeds           []repository.PetBreed           `json:"breeds"`
		Interactions     []repository.PetInteraction     `json:"interactions"`
		Personalities    []repository.PetPersonality     `json:"personalities"`
		Reactivities     []repository.PetReactivity      `json:"reactivities"`
		IsSterilized     bool                            `json:"isSterilized"`
	}
	CreatePetRequest struct {
		Name       string            `json:"name"`
		Birthday   string            `json:"birthday"`
		PhotoURL   string            `json:"photoUrl"`
		Gender     repository.Gender `json:"gender"`
		Size       string            `json:"size"`
		Weight     string            `json:"weight"`
		Attributes PetAttr           `json:"attributes"`
		UserPetLink
	}
	CreatePetResponse struct {
		PetID string `json:"petID"`
		CreatePetRequest
	}
)
