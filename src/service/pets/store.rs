use sqlx::{query_as, Executor, Postgres};
use uuid::Uuid;

use super::models::{FullPet, JoinedFullPet, PetAttributes, PetBase};

pub async fn retrieve_full_pet<'e, E>(conn: E, pet_id: Uuid) -> FullPet
where
    E: Executor<'e, Database = Postgres>,
{
    let pet = query_as::<_, JoinedFullPet>(
        r#"SELECT p.*, attr.is_sterilized, attr_aggr.aggression_levels,
          attr_all.allergies, attr_be.behaviors, attr_br.breeds,
          attr_int.interactions, attr_pe.personalities, attr_re.reactivities
        FROM pets p
        LEFT JOIN pet_attrs attr ON p.id = attr.pet_id
        LEFT JOIN pet_attr_aggression_levels attr_aggr ON attr.id = attr_aggr.pet_attr_id
        LEFT JOIN pet_attr_allergies attr_all ON attr.id = attr_all.pet_attr_id
        LEFT JOIN pet_attr_behaviors attr_be ON attr.id = attr_be.pet_attr_id
        LEFT JOIN pet_attr_breeds attr_br ON attr.id = attr_br.pet_attr_id
        LEFT JOIN pet_attr_interactions attr_int ON attr.id = attr_int.pet_attr_id
        LEFT JOIN pet_attr_personalities attr_pe ON attr.id = attr_pe.pet_attr_id
        LEFT JOIN pet_attr_reactivities attr_re ON attr.id = attr_re.pet_attr_id
        WHERE p.id = $1;
        "#,
    )
    .bind(pet_id)
    .fetch_one(conn)
    .await
    .unwrap();

    FullPet {
        base: PetBase {
            pet_id: pet.id,
            name: pet.name,
            age: pet.age,
            gender: pet.gender,
            size: pet.size,
            photo_url: pet.photo_url,
            weight: pet.weight,
            weight_unit: pet.weight_unit,
        },
        attributes: PetAttributes {
            aggression_levels: pet.aggression_levels,
            allergies: pet.allergies,
            breeds: pet.breeds,
            behaviors: pet.behaviors,
            interactions: pet.interactions,
            personalities: pet.personalities,
            reactivities: pet.reactivities,
            sterilized: pet.is_sterilized,
        },
    }
}
