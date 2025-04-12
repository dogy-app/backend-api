use jsonwebtoken::{decode, DecodingKey, TokenData, Validation};
use serde::Deserialize;

use crate::config::load_config;

use super::error::{Error, Result};
use super::layer::CurrentUser;

#[allow(dead_code)]
#[derive(Deserialize)]
struct Claims {
    pub role: Option<String>,
    pub sub: String,
    pub iss: String,
    pub jti: String,
    pub exp: usize,
    pub iat: usize,
    pub nbf: usize,
}

fn decode_jwt(jwt_token: &str) -> Result<TokenData<Claims>> {
    let config = load_config();

    decode(
        jwt_token,
        &DecodingKey::from_rsa_components(
            config.CLERK_RSA_MODULUS.as_str(),
            config.CLERK_RSA_EXPONENT.as_str(),
        )
        .map_err(|_| Error::InvalidDecodingKey)?,
        &Validation::new(jsonwebtoken::Algorithm::RS256),
    )
    .map_err(|_| Error::CannotDecodeToken)
}

pub fn authenticate_user(auth_header: &str) -> Result<CurrentUser> {
    let user_info = decode_jwt(auth_header).map_err(|_| Error::CannotDecodeToken);
    match user_info {
        Ok(user) => Ok(CurrentUser {
            user_id: user.claims.sub,
            role: user.claims.role,
            internal_id: None,
        }),
        Err(err) => Err(err),
    }
}

#[cfg(test)]
mod test {
    use super::decode_jwt;
    use crate::config::load_test_config;
    use jsonwebtoken::Algorithm;

    #[test]
    fn test_decode_jwt_ok() {
        let test_config = load_test_config();
        let jwt_token = test_config.JWT_TOKEN.as_str();
        let token_data = decode_jwt(jwt_token).unwrap();
        assert_eq!(token_data.header.alg, Algorithm::RS256);
        assert_eq!(token_data.header.typ, Some("JWT".to_string()));
        assert_eq!(token_data.claims.sub, "user_2ruHSXCzfIRreR2tpttVQBl512a");
        assert_eq!(token_data.claims.role, None);
    }
}
