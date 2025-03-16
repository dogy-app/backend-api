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

mod test {
    use jsonwebtoken::Algorithm;

    use super::*;

    #[test]
    fn test_decode_jwt_ok() {
        let jwt_token = "eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDIyMkFBQSIsImtpZCI6Imluc18ycnN0V2dNOGN2SlltZVloMXZwTU95WWo4NnYiLCJ0eXAiOiJKV1QifQ.eyJhenAiOiJodHRwczovL25lYXQtY2F0LTEyLmFjY291bnRzLmRldiIsImVtYWlsX2FkZHJlc3MiOiJ0ZXN0X2NsZXJrQGRvZ3kuYXBwIiwiZXhwIjoyMDU3NDU5NDIxLCJmdWxsX25hbWUiOm51bGwsImlhdCI6MTc0MjA5OTQyMSwiaXNzIjoiaHR0cHM6Ly9uZWF0LWNhdC0xMi5jbGVyay5hY2NvdW50cy5kZXYiLCJqdGkiOiI4ZjkxNDg0MWFhZmEyODkxOTg0OSIsIm5iZiI6MTc0MjA5OTQxNiwicm9sZSI6bnVsbCwic3ViIjoidXNlcl8ycnVIU1hDemZJUnJlUjJ0cHR0VlFCbDUxMmEiLCJ1c2VyX2lkIjoidXNlcl8ycnVIU1hDemZJUnJlUjJ0cHR0VlFCbDUxMmEifQ.bJ1GHjtkKgPSQdCvUrXcqpzEsqXR3JxmxomlWU_1egqNDrtoaH3jCiyW3i5wW2M3IFhfCuQjFsKL1pM7eVItpWBWua0mTZq4X6SHu4EeWM2Kg6N5fy5EzsgB9t9a1a-vND8k7SwhjfDmshGYJLOHxgYGPEcu1gMaz3MLgS7TjDiNDYxrjZn0yXSfSoy45Es16R-c8cX_Gn4Uz0DTw0u0SLN-CFR9suoe-6eps_c8xUqWf_n9bRcFleKhOWQwSODIcDv5V33sw9FwgEefUmhQYkGkte15OEFBxzuN2g-7NIDQew7Lc_OzYTjw_6-5HWm2pVJHahvc01EWQk7TbchxSw".to_string();
        let token_data = decode_jwt(jwt_token).unwrap();
        assert_eq!(token_data.header.alg, Algorithm::RS256);
        assert_eq!(token_data.header.typ, Some("JWT".to_string()));
        assert_eq!(token_data.claims.sub, "user_2ruHSXCzfIRreR2tpttVQBl512a");
        assert_eq!(token_data.claims.role, None);
    }
}
