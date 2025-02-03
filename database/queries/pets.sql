-- name: CreateBasePet :one
INSERT INTO pets (name, birthday, photo_url, gender, size, weight) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *;

-- name: CreateBasePetAttr :one
INSERT INTO pet_attrs (pet_id, is_sterilized) VALUES ($1, $2) RETURNING *;

-- name: CreatePetAttrAggressionLevel :exec
INSERT INTO pet_attr_aggression_levels (pet_attr_id, aggression_level) VALUES ($1, $2);

-- name: CreatePetAttrAllergy :exec
INSERT INTO pet_attr_allergies (pet_attr_id, allergy) VALUES ($1, $2);

-- name: CreatePetAttrBehavior :exec
INSERT INTO pet_attr_behaviors (pet_attr_id, behavior) VALUES ($1, $2);

-- name: CreatePetAttrBreed :exec
INSERT INTO pet_attr_breeds (pet_attr_id, breed) VALUES ($1, $2);

-- name: CreatePetAttrInteractions :exec
INSERT INTO pet_attr_interactions (pet_attr_id, interaction) VALUES ($1, $2);

-- name: CreatePetAttrPersonalities :exec
INSERT INTO pet_attr_personalities (pet_attr_id, personality) VALUES ($1, $2);

-- name: CreatePetAttrReactivities :exec
INSERT INTO pet_attr_reactivities (pet_attr_id, reactivity) VALUES ($1, $2);

-- name: LinkPetToUser :exec
INSERT INTO users_pets_link (pet_id, user_id, is_dog_owner, is_dog_sitter) VALUES ($1, $2, $3, $4);
