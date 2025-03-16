use axum::http::StatusCode;
use dotenv::dotenv;
use jsonwebtoken::{decode, DecodingKey, TokenData, Validation};
use serde::Deserialize;

use crate::config::load_config;

#[derive(Deserialize)]
pub struct Claims {
    pub azp: String,
    pub email_address: String,
    pub user_id: String,
    pub full_name: Option<String>,
    pub role: Option<String>,
    pub sub: String,
    pub iss: String,
    pub jti: String,
    pub exp: usize,
    pub iat: usize,
    pub nbf: usize,
}

pub fn decode_jwt(jwt_token: String) -> Result<TokenData<Claims>, StatusCode> {
    let config = load_config();

    decode(
        &jwt_token,
        &DecodingKey::from_rsa_components(
            config.CLERK_RSA_MODULUS.as_str(),
            config.CLERK_RSA_EXPONENT.as_str(),
        )
        .map_err(|_| StatusCode::UNAUTHORIZED)?,
        &Validation::new(jsonwebtoken::Algorithm::RS256),
    )
    .map_err(|_| StatusCode::UNAUTHORIZED)
}
