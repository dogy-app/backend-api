-- name: CreateBasePet :one
INSERT INTO pets (name, birthday, photo_url, gender, size, weight, weight_unit) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *;

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

-- name: DeletePetByID :exec
DELETE FROM pets WHERE id = $1;

-- name: LinkPetToUser :exec
INSERT INTO users_pets_link (pet_id, user_id, is_dog_owner, is_dog_sitter) VALUES ($1, $2, $3, $4);

-- name: GetPetByID :one
SELECT * FROM pets WHERE id = $1;

-- name: GetAllPetsFromUser :many
SELECT
    attr.pet_id,
    attr.is_sterilized,
    COALESCE(breeds.breeds, '{}') AS breeds,
    COALESCE(aggression_levels.aggression_levels, '{}') AS aggression_levels,
    COALESCE(allergies.allergies, '{}') AS allergies,
    COALESCE(behaviors.behaviors, '{}') AS behaviors,
    COALESCE(interactions.interactions, '{}') AS interactions,
    COALESCE(personalities.personalities, '{}') AS personalities,
    COALESCE(reactivities.reactivities, '{}') AS reactivities
FROM pet_attrs attr
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(breed) AS breeds
    FROM pet_attr_breeds
    WHERE pet_attr_id = attr.id
) breeds ON true
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(aggression_level) AS aggression_levels
    FROM pet_attr_aggression_levels
    WHERE pet_attr_id = attr.id
) aggression_levels ON true
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(allergy) AS allergies
    FROM pet_attr_allergies
    WHERE pet_attr_id = attr.id
) allergies ON true
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(behavior) AS behaviors
    FROM pet_attr_behaviors
    WHERE pet_attr_id = attr.id
) behaviors ON true
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(interaction) AS interactions
    FROM pet_attr_interactions
    WHERE pet_attr_id = attr.id
) interactions ON true
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(personality) AS personalities
    FROM pet_attr_personalities
    WHERE pet_attr_id = attr.id
) personalities ON true
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(reactivity) AS reactivities
    FROM pet_attr_reactivities
    WHERE pet_attr_id = attr.id
) reactivities ON true
WHERE pet_id IN (SELECT pet_id FROM users_pets_link WHERE user_id = $1);
