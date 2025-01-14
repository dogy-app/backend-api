from enum import Enum


# Enums
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class AgeGroup(str, Enum):
    UNDER_18 = "under 18"
    AGE_18_24 = "18-24"
    AGE_25_34 = "25-34"
    AGE_35_44 = "35-44"
    AGE_45_54 = "45-54"
    AGE_55_64 = "55-64"
    AGE_65_PLUS = "65+"

class UserRole(str, Enum):
    DOG_OWNER = "dog owner"
    DOG_SITTER = "dog sitter"
    BOTH = "both"

class SubscriptionType(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNKNOWN = "unknown"

class PetSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class PlaceType(str, Enum):
    DOG_PARK = "dog park"

class PetAggressionLevel(str, Enum):
    NON_AGGRESSIVE = "Non-aggressive"
    GUARDING_BEHAVIOR = "Guarding behavior"
    MILD_AGGRESSION = "Mild aggression under specific circumstances"
    KNOWN_AGGRESSION = "Known history of aggression"

class PetAllergy(str, Enum):
    """None is a possible value"""
    NONE = "None"
    BEEF = "Beef"
    CHICKEN = "Chicken"
    LAMB = "Lamb"
    PORK = "Pork"
    FISH = "Fish"
    EGGS = "Eggs"
    MILK = "Milk"
    CHEESE = "Cheese"
    BARLEY = "Barley"
    WHEAT = "Wheat"
    CORN = "Corn"
    SOY = "Soy"
    PEANUTS = "Peanuts"
    SESAME = "Sesame"
    MILLET = "Millet"
    RICE = "Rice"
    OATS = "Oats"
    TREE_NUTS = "Tree Nuts"
    YEAST = "Yeast"
    FRUITS = "Fruits"

class PetBehavior(str, Enum):
    OBEDIENT = "Obedient"
    STUBBORN = "Stubborn"
    CURIOUS = "Curious"
    ALERT = "Alert"
    RELAXED = "Relaxed"
    ANXIOUS = "Anxious"
    FEARFUL = "Fearful"
    CONFIDENT = "Confident"
    AGGRESSIVE = "Aggressive"
    TIMID = "Timid"
    DOMINANT = "Dominant"
    SUBMISSIVE = "Submissive"

class PetInteraction(str, Enum):
    LOVES_OTHER_DOGS = "Loves other dogs"
    PREFERS_HUMAN_COMPANY = "Prefers human company"
    GOOD_WITH_CHILDREN = "Good with children"
    GOOD_WITH_OTHER_PETS = "Good with cats/other pets"
    ENJOYS_LARGE_GROUPS = "Enjoys large groups"
    PREFERS_ONE_TO_ONE = "Prefers one-on-one interactions"

class PetPersonality(str, Enum):
    PLAYFUL = "Playful"
    ENERGETIC = "Energetic"
    SHY = "Shy"
    OUTGOING = "Outgoing"
    CALM = "Calm"
    RESERVED = "Reserved"
    AFFECTIONATE = "Affectionate"
    INDEPENDENT = "Independent"

class PetReactivity(str, Enum):
    """None is a possible value"""
    NONE = "Non-reactive"
    STRANGERS = "Reactive to strangers"
    NOISES = "Reactive to noises"
    MOVING_OBJECTS = "Reactive to moving objects"
    SPECIFIC_SITUATIONS = "Reactive to specific situations"
    SAME_GENDER = "Reactive to same gender dogs"
