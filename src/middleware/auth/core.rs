//! This module contains the core functionality of authentication middleware.
use jsonwebtoken::{decode, DecodingKey, TokenData, Validation};
use serde::Deserialize;
use tracing::debug;

use crate::config::load_config;

use super::error::{Error, Result};
use super::layer::CurrentUser;

/// Represents the payload after decoding a token.
#[allow(dead_code)]
#[derive(Debug, Deserialize)]
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
    debug!("JWT Token: {:?}", jwt_token);
    debug!("Config: {:?}", config);
    let decoding_key = DecodingKey::from_rsa_components(
        config.CLERK_RSA_MODULUS.as_str(),
        config.CLERK_RSA_EXPONENT.as_str(),
    )
    .map_err(|_| Error::InvalidDecodingKey)?;

    decode(
        jwt_token,
        &decoding_key,
        &Validation::new(jsonwebtoken::Algorithm::RS256),
    )
    .map_err(|_| Error::InvalidToken)
}

/// Retrieve the user information from a JWT token. Do not include the `Bearer` prefix, only the
/// actual JWT token.
pub fn authenticate_user(auth_header: &str) -> Result<CurrentUser> {
    let user_info = decode_jwt(auth_header)?;
    Ok(CurrentUser {
        user_id: user_info.claims.sub,
        role: user_info.claims.role,
        internal_id: None,
    })
}

#[cfg(test)]
mod test {
    use crate::middleware::auth::core::authenticate_user;
    use crate::middleware::auth::layer::CurrentUser;
    use std::env;

    use super::decode_jwt;
    use jsonwebtoken::Algorithm;

    #[test]
    fn test_decode_jwt_ok() {
        let _ = dotenv::from_filename(".env.test");
        let jwt_token = env::var("JWT_TOKEN").unwrap();

        let token_data = decode_jwt(jwt_token.as_str()).unwrap();
        assert_eq!(token_data.header.alg, Algorithm::RS256);
        assert_eq!(token_data.header.typ, Some("JWT".to_string()));
        assert_eq!(token_data.claims.sub, "user_2ruHSXCzfIRreR2tpttVQBl512a");
        assert_eq!(token_data.claims.role, None);
    }

    // This test will fail if you use `cargo test` because env vars are shared
    // even across threads.
    //
    // Use `cargo nextest run` instead as it runs tests in parallel and isolation.
    #[test]
    fn test_decode_jwt_invalid_decoding_key_err() {
        unsafe {
            env::set_var("DATABASE_URL", "test_url");
            env::set_var("LANGGRAPH_ASSISTANT_ENDPOINT", "test_url");
            env::set_var("CLERK_RSA_MODULUS", "invalid_base64@string!");
            env::set_var("CLERK_RSA_EXPONENT", "test827@0.");
        }

        let _ = dotenv::from_filename(".env.test");
        let jwt_token = env::var("JWT_TOKEN").unwrap();
        let token_data = decode_jwt(jwt_token.as_str());
        dbg!("Token data: {:?}", &token_data);
        assert!(
            matches!(token_data, Err(super::Error::InvalidDecodingKey)),
            "Expected InvalidDecodingKey error"
        );
    }

    #[test]
    fn test_decode_jwt_invalid_token_err() {
        let _ = dotenv::from_filename(".env.test");
        let jwt_token = "invalid_token";
        let token_data = decode_jwt(jwt_token);
        dbg!("Token data: {:?}", &token_data);
        assert!(
            matches!(token_data, Err(super::Error::InvalidToken)),
            "Expected InvalidToken error"
        );
    }

    #[test]
    fn test_authenticate_user_ok() {
        let _ = dotenv::from_filename(".env.test");
        let jwt_token = env::var("JWT_TOKEN").unwrap();

        let current_user = authenticate_user(jwt_token.as_str()).unwrap();
        assert_eq!(
            current_user,
            CurrentUser {
                user_id: String::from("user_2ruHSXCzfIRreR2tpttVQBl512a"),
                role: None,
                internal_id: None,
            }
        );
    }

    #[test]
    fn test_authenticate_user_invalid_token_err() {
        let jwt_token = "invalid_token";

        let _ = dotenv::from_filename(".env.test");
        let current_user = authenticate_user(jwt_token);
        assert!(
            matches!(current_user, Err(super::Error::InvalidToken)),
            "Expected InvalidToken error"
        );
    }

    #[test]
    fn test_authenticate_user_invalid_decoding_key_err() {
        unsafe {
            env::set_var("DATABASE_URL", "test_url");
            env::set_var("LANGGRAPH_ASSISTANT_ENDPOINT", "test_url");
            env::set_var("CLERK_RSA_MODULUS", "invalid_base64@string!");
            env::set_var("CLERK_RSA_EXPONENT", "test827@0.");
        }

        let _ = dotenv::from_filename(".env.test");
        let jwt_token = env::var("JWT_TOKEN").unwrap();

        let current_user = authenticate_user(jwt_token.as_str());
        dbg!("Current user: {:?}", &current_user);
        assert!(
            matches!(current_user, Err(super::Error::InvalidDecodingKey)),
            "Expected InvalidDecodingKey error"
        );
    }
}
