use jsonwebtoken::{decode, DecodingKey, TokenData, Validation};
use serde::Deserialize;

use crate::config::load_config;

use super::error::{Error, Result};
use super::layer::CurrentUser;

#[derive(Deserialize)]
struct Claims {
    pub azp: String,
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

mod test {
    use super::decode_jwt;
    use jsonwebtoken::Algorithm;

    #[test]
    fn test_decode_jwt_ok() {
        let jwt_token = "eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDIyMkFBQSIsImtpZCI6Imluc18ycnN0V2dNOGN2SlltZVloMXZwTU95WWo4NnYiLCJ0eXAiOiJKV1QifQ.eyJhenAiOiJodHRwczovL25lYXQtY2F0LTEyLmFjY291bnRzLmRldiIsImV4cCI6MjA1NzcwOTU3OCwiaWF0IjoxNzQyMzQ5NTc4LCJpc3MiOiJodHRwczovL25lYXQtY2F0LTEyLmNsZXJrLmFjY291bnRzLmRldiIsImp0aSI6IjIxMDgxODQwMDI1NmY4OWE4NjIyIiwibmJmIjoxNzQyMzQ5NTczLCJyb2xlIjpudWxsLCJzdWIiOiJ1c2VyXzJydUhTWEN6ZklScmVSMnRwdHRWUUJsNTEyYSJ9.U3RITdKOE_MN78aIP8IG7aYcrVlGhq_I2wnpgpsHBgNVKWnKXYtymquOSv0taszAI7n3Ju_MyA896xjOIjaTIj3rjmV1-5XNK35kubT1GEiDmM1HSTN0jd4snE8jIW1F3TgqCd89ZdVlxo5FwTUqZ877xmOcJkOjyTq9W9wLK6Ep_pjW6uuoVzq4vFcFMKZV7aOd2g3aZ4LbLTMlIxjpAg3n1FnKNZsfwp3gBu-h5cxB5mn73_Ak4B9nLP0ti-NrrVeHEmesT68GZzOwu4cGF4Gjxy_BFSO64ruJwrMtB1ZAMztve2gHHvdvvIv0caaCp4lejnUhgNhSVzbEP8iLMg";
        let token_data = decode_jwt(jwt_token).unwrap();
        assert_eq!(token_data.header.alg, Algorithm::RS256);
        assert_eq!(token_data.header.typ, Some("JWT".to_string()));
        assert_eq!(token_data.claims.sub, "user_2ruHSXCzfIRreR2tpttVQBl512a");
        assert_eq!(token_data.claims.role, None);
    }
}
