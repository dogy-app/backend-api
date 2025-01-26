import { pgEnum } from "drizzle-orm/pg-core";
import {
	Gender,
	PetAggressionLevel,
	PetAllergy,
	PetBehavior,
	PetBreed,
	PetInteraction,
	PetPersonality,
	PetReactivity,
	PetSize,
	PlaceType,
	SubscriptionType,
	enumToPgEnum,
} from "./enums";

export const gender = pgEnum("gender", enumToPgEnum(Gender));
export const subscriptionType = pgEnum(
	"subscription_type",
	enumToPgEnum(SubscriptionType),
);

export const placeType = pgEnum("place_type", enumToPgEnum(PlaceType));

/**** Pet Enums ****/

export const petSize = pgEnum("pet_size", enumToPgEnum(PetSize));
export const petBreed = pgEnum("pet_breed", enumToPgEnum(PetBreed));
export const petAggressionLevel = pgEnum(
	"pet_aggression_level",
	enumToPgEnum(PetAggressionLevel),
);
export const petAllergy = pgEnum("pet_allergy", enumToPgEnum(PetAllergy));
export const petBehavior = pgEnum("pet_behavior", enumToPgEnum(PetBehavior));
export const petInteraction = pgEnum(
	"pet_interaction",
	enumToPgEnum(PetInteraction),
);
export const petPersonality = pgEnum(
	"pet_personality",
	enumToPgEnum(PetPersonality),
);
export const petReactivity = pgEnum(
	"pet_reactivity",
	enumToPgEnum(PetReactivity),
);
