use axum::{
    extract::{Path, State},
    Extension, Json,
};
use serde_json::{json, Value};
use uuid::Uuid;

use crate::{middleware::auth::layer::CurrentUser, AppState};

use super::{
    models::{
        AllFullPet, FullPet, JoinedFullPet, PetAttributes, PetBase, UpdatePetAttributes,
        UpdatePetBase,
    },
    store::retrieve_full_pet,
};

pub async fn create_pet(
    Extension(current_user): Extension<CurrentUser>,
    State(state): State<AppState>,
    Json(mut pet): Json<FullPet>,
) -> Json<FullPet> {
    let conn = &*state.db;
    let mut txn = conn.begin().await.unwrap();

    // Inserting Base Pet
    let pet_id: (Uuid,) = sqlx::query_as(
        r#"INSERT INTO pets (name, age, gender, size, photo_url, weight, weight_unit)
        VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id;"#,
    )
    .bind(&pet.base.name)
    .bind(pet.base.age)
    .bind(&pet.base.gender)
    .bind(&pet.base.size)
    .bind(&pet.base.photo_url)
    .bind(pet.base.weight)
    .bind(&pet.base.weight_unit)
    .fetch_one(&mut *txn)
    .await
    .unwrap();

    // Inserting Pet Attributes
    let pet_attrs_id: (Uuid,) = sqlx::query_as(
        "INSERT INTO pet_attrs (pet_id, is_sterilized) VALUES ($1, $2) RETURNING id; ",
    )
    .bind(pet_id.0)
    .bind(pet.attributes.sterilized)
    .fetch_one(&mut *txn)
    .await
    .unwrap();

    sqlx::query(
        "INSERT INTO pet_attr_aggression_levels (pet_attr_id, aggression_levels) VALUES ($1, $2);",
    )
    .bind(pet_attrs_id.0)
    .bind(&pet.attributes.aggression_levels)
    .execute(&mut *txn)
    .await
    .unwrap();

    sqlx::query("INSERT INTO pet_attr_allergies (pet_attr_id, allergies) VALUES ($1, $2);")
        .bind(pet_attrs_id.0)
        .bind(&pet.attributes.allergies)
        .execute(&mut *txn)
        .await
        .unwrap();

    sqlx::query("INSERT INTO pet_attr_behaviors (pet_attr_id, behaviors) VALUES ($1, $2);")
        .bind(pet_attrs_id.0)
        .bind(&pet.attributes.behaviors)
        .execute(&mut *txn)
        .await
        .unwrap();

    sqlx::query("INSERT INTO pet_attr_breeds (pet_attr_id, breeds) VALUES ($1, $2);")
        .bind(pet_attrs_id.0)
        .bind(&pet.attributes.breeds)
        .execute(&mut *txn)
        .await
        .unwrap();

    sqlx::query("INSERT INTO pet_attr_interactions (pet_attr_id, interactions) VALUES ($1, $2);")
        .bind(pet_attrs_id.0)
        .bind(&pet.attributes.interactions)
        .execute(&mut *txn)
        .await
        .unwrap();

    sqlx::query("INSERT INTO pet_attr_personalities (pet_attr_id, personalities) VALUES ($1, $2);")
        .bind(pet_attrs_id.0)
        .bind(&pet.attributes.personalities)
        .execute(&mut *txn)
        .await
        .unwrap();

    sqlx::query("INSERT INTO pet_attr_reactivities (pet_attr_id, reactivities) VALUES ($1, $2);")
        .bind(pet_attrs_id.0)
        .bind(&pet.attributes.reactivities)
        .execute(&mut *txn)
        .await
        .unwrap();

    sqlx::query(
        "INSERT INTO users_pets_link
        (pet_id, user_id, is_dog_owner, is_dog_sitter)
        VALUES ($1, $2, TRUE, FALSE);",
    )
    .bind(pet_id.0)
    .bind(current_user.internal_id.unwrap())
    .execute(&mut *txn)
    .await
    .unwrap();

    txn.commit().await.unwrap();

    pet.base.pet_id = pet_id.0;

    Json(pet)
}

pub async fn get_pet(
    Extension(_current_user): Extension<CurrentUser>,
    State(state): State<AppState>,
    Path(pet_id): Path<Uuid>,
) -> Json<FullPet> {
    let conn = &*state.db;
    let pet: FullPet = retrieve_full_pet(conn, pet_id).await;

    Json(pet)
}

pub async fn get_all_pets(
    Extension(current_user): Extension<CurrentUser>,
    State(state): State<AppState>,
) -> Json<AllFullPet> {
    let conn = &*state.db;
    let pets_row = sqlx::query_as::<_, JoinedFullPet>(
        r#"SELECT p.*, attr.is_sterilized, attr_aggr.aggression_levels,
          attr_all.allergies, attr_be.behaviors, attr_br.breeds,
          attr_int.interactions, attr_pe.personalities, attr_re.reactivities
        FROM pets p
        LEFT JOIN users_pets_link upl ON p.id = upl.pet_id
        LEFT JOIN pet_attrs attr ON p.id = attr.pet_id
        LEFT JOIN pet_attr_aggression_levels attr_aggr ON attr.id = attr_aggr.pet_attr_id
        LEFT JOIN pet_attr_allergies attr_all ON attr.id = attr_all.pet_attr_id
        LEFT JOIN pet_attr_behaviors attr_be ON attr.id = attr_be.pet_attr_id
        LEFT JOIN pet_attr_breeds attr_br ON attr.id = attr_br.pet_attr_id
        LEFT JOIN pet_attr_interactions attr_int ON attr.id = attr_int.pet_attr_id
        LEFT JOIN pet_attr_personalities attr_pe ON attr.id = attr_pe.pet_attr_id
        LEFT JOIN pet_attr_reactivities attr_re ON attr.id = attr_re.pet_attr_id
        WHERE upl.user_id = $1
        "#,
    )
    .bind(current_user.internal_id.unwrap())
    .fetch_all(conn)
    .await
    .unwrap();

    let pets = pets_row
        .into_iter()
        .map(|pet| FullPet {
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
        })
        .collect();

    Json(AllFullPet { pets })
}

pub async fn delete_pet(
    Extension(_current_user): Extension<CurrentUser>,
    State(state): State<AppState>,
    Path(pet_id): Path<Uuid>,
) -> Json<Value> {
    let conn = &*state.db;
    sqlx::query("DELETE FROM pets WHERE id = $1;")
        .bind(pet_id)
        .execute(conn)
        .await
        .unwrap();

    Json(json!({ "message": format!("Pet {} deleted successfully", pet_id) }))
}

pub async fn update_base_pet(
    State(state): State<AppState>,
    Path(pet_id): Path<Uuid>,
    Json(pet): Json<UpdatePetBase>,
) -> Json<UpdatePetBase> {
    let conn = &*state.db;
    sqlx::query(
        r#"
    UPDATE pets
    SET
        name = COALESCE($2, name),
        age = COALESCE($3, age),
        gender = COALESCE($4, gender),
        size = COALESCE($5, size),
        photo_url = COALESCE($6, photo_url),
        weight = COALESCE($7, weight),
        weight_unit = COALESCE($8, weight_unit)
    WHERE id = $1;
        "#,
    )
    .bind(pet_id)
    .bind(&pet.name)
    .bind(pet.age)
    .bind(&pet.gender)
    .bind(&pet.size)
    .bind(&pet.photo_url)
    .bind(pet.weight)
    .bind(&pet.weight_unit)
    .execute(conn)
    .await
    .unwrap();

    Json(pet)
}

pub async fn update_pet_attributes(
    State(state): State<AppState>,
    Path(pet_id): Path<Uuid>,
    Json(pet): Json<UpdatePetAttributes>,
) -> Json<UpdatePetAttributes> {
    let conn = &*state.db;
    let mut txn = conn.begin().await.unwrap();
    let attr_id = sqlx::query_as::<_, (Uuid,)>(
        r#"SELECT pa.id FROM pet_attrs pa
WHERE pa.pet_id = $1;"#,
    )
    .bind(pet_id)
    .fetch_one(&mut *txn)
    .await
    .unwrap();

    if let Some(aggression_levels) = &pet.aggression_levels {
        sqlx::query(
            r#"
        UPDATE pet_attr_aggression_levels
        SET
            aggression_levels = $2
        WHERE
            pet_attr_id = $1;
        "#,
        )
        .bind(attr_id.0)
        .bind(aggression_levels)
        .execute(&mut *txn)
        .await
        .unwrap();
    }

    if let Some(allergies) = &pet.allergies {
        sqlx::query(
            r#"
        UPDATE pet_attr_allergies
        SET
            allergies = $2
        WHERE
            pet_attr_id = $1;
        "#,
        )
        .bind(attr_id.0)
        .bind(allergies)
        .execute(&mut *txn)
        .await
        .unwrap();
    }

    if let Some(behaviors) = &pet.behaviors {
        sqlx::query(
            r#"
        UPDATE pet_attr_behaviors
        SET
            behaviors = $2
        WHERE
            pet_attr_id = $1;
        "#,
        )
        .bind(attr_id.0)
        .bind(behaviors)
        .execute(&mut *txn)
        .await
        .unwrap();
    }

    if let Some(breeds) = &pet.breeds {
        sqlx::query(
            r#"
        UPDATE pet_attr_breeds
        SET
            breeds = $2
        WHERE
            pet_attr_id = $1;
        "#,
        )
        .bind(attr_id.0)
        .bind(breeds)
        .execute(&mut *txn)
        .await
        .unwrap();
    }

    if let Some(interactions) = &pet.interactions {
        sqlx::query(
            r#"
        UPDATE pet_attr_interactions
        SET
            interactions = $2
        WHERE
            pet_attr_id = $1;
        "#,
        )
        .bind(attr_id.0)
        .bind(interactions)
        .execute(&mut *txn)
        .await
        .unwrap();
    }

    if let Some(personalities) = &pet.personalities {
        sqlx::query(
            r#"
        UPDATE pet_attr_personalities
        SET
            personalities = $2
        WHERE
            pet_attr_id = $1;
        "#,
        )
        .bind(attr_id.0)
        .bind(personalities)
        .execute(&mut *txn)
        .await
        .unwrap();
    }

    if let Some(reactivities) = &pet.reactivities {
        sqlx::query(
            r#"
        UPDATE pet_attr_reactivities
        SET
            reactivities = $2
        WHERE
            pet_attr_id = $1;
        "#,
        )
        .bind(attr_id.0)
        .bind(reactivities)
        .execute(&mut *txn)
        .await
        .unwrap();
    }

    if let Some(sterilized) = &pet.sterilized {
        sqlx::query(
            r#"
        UPDATE pet_attrs
        SET
            is_sterilized = $2
        WHERE
            id = $1;
        "#,
        )
        .bind(attr_id.0)
        .bind(sterilized)
        .execute(&mut *txn)
        .await
        .unwrap();
    }

    txn.commit().await.unwrap();

    Json(pet)
}
