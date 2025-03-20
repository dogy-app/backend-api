use serde::{Deserialize, Serialize};
use sqlx::Type;

#[derive(Serialize, Type, Deserialize)]
#[serde(rename_all = "lowercase")]
#[sqlx(type_name = "gender", rename_all = "lowercase")]
pub enum Gender {
    Male,
    Female,
}

#[derive(Serialize, Type, Deserialize)]
#[serde(rename_all = "lowercase")]
#[sqlx(type_name = "pet_size", rename_all = "lowercase")]
pub enum PetSize {
    Small,
    Medium,
    Large,
}

#[derive(Serialize, Type, Deserialize)]
#[serde(rename_all = "lowercase")]
#[sqlx(type_name = "weight_unit", rename_all = "lowercase")]
pub enum WeightUnit {
    Kg,
    Lbs,
}

#[derive(Serialize, Type, Deserialize)]
#[serde(rename_all = "lowercase")]
#[sqlx(type_name = "pet_aggression_level")]
pub enum PetAggressionLevel {
    #[serde(rename = "Non-aggressive")]
    #[sqlx(rename = "Non-aggressive")]
    NonAggressive,

    #[serde(rename = "Guarding behavior")]
    #[sqlx(rename = "Guarding behavior")]
    GuardingBehavior,

    #[serde(rename = "Mild aggression under specific circumstances")]
    #[sqlx(rename = "Mild aggression under specific circumstances")]
    MildAggression,

    #[serde(rename = "Known history of aggression")]
    #[sqlx(rename = "Known history of aggression")]
    KnownHistoryAggression,
}

#[derive(Serialize, Type, Deserialize)]
#[sqlx(type_name = "pet_allergy")]
pub enum PetAllergy {
    Beef,
    Chicken,
    Lamb,
    Pork,
    Fish,
    Eggs,
    Milk,
    Cheese,
    Barley,
    Wheat,
    Corn,
    Soy,
    Peanuts,
    Sesame,
    Millet,
    Rice,
    Oats,
    #[serde(rename = "Tree Nuts")]
    #[sqlx(rename = "Tree Nuts")]
    TreeNuts,
    Yeast,
    Fruits,
}

#[derive(Serialize, Type, Deserialize)]
#[sqlx(type_name = "pet_behavior")]
pub enum PetBehavior {
    Obedient,
    Stubborn,
    Curious,
    Alert,
    Relaxed,
    Anxious,
    Fearful,
    Confident,
    Aggressive,
    Timid,
    Dominant,
    Submissive,
}

#[derive(Serialize, Type, Deserialize)]
#[sqlx(type_name = "pet_interaction")]
pub enum PetInteraction {
    #[serde(rename = "Loves other dogs")]
    #[sqlx(rename = "Loves other dogs")]
    LovesOtherDogs,

    #[serde(rename = "Prefers human company")]
    #[sqlx(rename = "Prefers human company")]
    PrefersHumanCompany,

    #[serde(rename = "Good with children")]
    #[sqlx(rename = "Good with children")]
    GoodWithChildren,

    #[serde(rename = "Good with cats/other pets")]
    #[sqlx(rename = "Good with cats/other pets")]
    GoodWithCats,

    #[serde(rename = "Enjoys large groups")]
    #[sqlx(rename = "Enjoys large groups")]
    EnjoysLargeGroups,

    #[serde(rename = "Prefers one-on-one interactions")]
    #[sqlx(rename = "Prefers one-on-one interactions")]
    PrefersOneToOne,
}

#[derive(Serialize, Type, Deserialize)]
#[sqlx(type_name = "pet_personality")]
pub enum PetPersonality {
    Playful,
    Energetic,
    Shy,
    Outgoing,
    Calm,
    Reserved,
    Affectionate,
    Independent,
}

#[derive(Serialize, Type, Deserialize)]
#[sqlx(type_name = "pet_reactivity")]
pub enum PetReactivity {
    #[serde(rename = "Non-reactive")]
    #[sqlx(rename = "Non-reactive")]
    NonReactive,

    #[serde(rename = "Reactive to strangers")]
    #[sqlx(rename = "Reactive to strangers")]
    Strangers,

    #[serde(rename = "Reactive to noises")]
    #[sqlx(rename = "Reactive to noises")]
    Noises,

    #[serde(rename = "Reactive to moving objects")]
    #[sqlx(rename = "Reactive to moving objects")]
    MovingObjects,

    #[serde(rename = "Reactive to specific situations")]
    #[sqlx(rename = "Reactive to specific situations")]
    SpecificSituations,

    #[serde(rename = "Reactive to same gender dogs")]
    #[sqlx(rename = "Reactive to same gender dogs")]
    SameGenderDogs,
}

#[derive(Serialize, Type, Deserialize)]
#[sqlx(type_name = "pet_breed")]
pub enum PetBreed {
    #[serde(rename = "Australian Shepherd")]
    #[sqlx(rename = "Australian Shepherd")]
    AustralianShepherd,

    #[serde(rename = "American Cocker Spaniel")]
    #[sqlx(rename = "American Cocker Spaniel")]
    AmericanCockerSpaniel,

    Akita,

    #[serde(rename = "Australian Cattle")]
    #[sqlx(rename = "Australian Cattle")]
    AustralianCattle,
}

//trait DbEnum {
//    fn to_db_value(&self) -> &'static str;
//    fn from_db_value(value: &str) -> Option<Self>
//    where
//        Self: Sized;
//}
//
//impl DbEnum for PetAggressionLevel {
//    fn to_db_value(&self) -> &'static str {
//        match self {
//            PetAggressionLevel::NonAggressive => "Non-aggressive",
//            PetAggressionLevel::GuardingBehavior => "Guarding behavior",
//            PetAggressionLevel::MildAggression => "Mild aggression under specific circumstances",
//            PetAggressionLevel::KnownHistoryAggression => "Known history of aggression",
//        }
//    }
//    fn from_db_value(value: &str) -> Option<Self>
//    where
//        Self: Sized,
//    {
//        match value {
//            "Non-aggressive" => Some(PetAggressionLevel::NonAggressive),
//            "Guarding behavior" => Some(PetAggressionLevel::GuardingBehavior),
//            "Mild aggression under specific circumstances" => {
//                Some(PetAggressionLevel::MildAggression)
//            }
//            "Known history of aggression" => Some(PetAggressionLevel::KnownHistoryAggression),
//            _ => None,
//        }
//    }
//}
