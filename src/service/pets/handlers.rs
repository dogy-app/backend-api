use axum::{extract::State, Extension, Json};
use uuid::Uuid;

use crate::{middleware::auth::layer::CurrentUser, AppState};

use super::models::FullPet;

pub async fn create_pet(
    Extension(_current_user): Extension<CurrentUser>,
    State(state): State<AppState>,
    Json(mut pet): Json<FullPet>,
) -> Json<FullPet> {
    let conn = &*state.db;
    println!("--> Starting transaction...");
    let mut txn = conn.begin().await.unwrap();

    // Inserting Base Pet
    let pet_id: (Uuid, ) = sqlx::query_as(
        r#"INSERT INTO pets (name, age, gender, size, photo_url, weight, weight_unit) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id;"#,
    ).bind(&pet.base.name)
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

    txn.commit().await.unwrap();

    pet.base.pet_id = pet_id.0;

    Json(pet)
}
