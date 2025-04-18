//! This module contains the core functionality of authentication middleware.
use jsonwebtoken::{decode, DecodingKey, TokenData, Validation};
use serde::Deserialize;

use crate::config::load_config;

use super::error::{Error, Result};
use super::layer::CurrentUser;

/// Represents the payload after decoding a token.
#[allow(dead_code)]
#[derive(Deserialize)]
pub struct Claims {
    /// Role of the authenticated user. Can either be None or a valid clerk role such as
    /// `org:admin`.
    pub role: Option<String>,

    /// Clerk user ID of the authenticated user.
    pub sub: String,

    /// Domain of the clerk backend.
    pub iss: String,

    /// Unique ID of the token.
    pub jti: String,

    /// Expiration timestamp of the token.
    pub exp: usize,

    /// Timestamp when the token was issued.
    pub iat: usize,

    /// Timestamp before the token is invalid.
    pub nbf: usize,
}

/// Decodes a JWT token into a [`TokenData<Claims>`].
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
    .map_err(|_| Error::InvalidToken)
}

/// Retrieve the user information from a JWT token. Do not include the `Bearer` prefix, only the
/// actual JWT token.
pub fn authenticate_user(auth_header: &str) -> Result<CurrentUser> {
    let user_info = decode_jwt(auth_header).map_err(|_| Error::InvalidToken);
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
