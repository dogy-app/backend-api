use crate::{Error, Result};
use dotenv::dotenv;
use std::env;
use std::sync::OnceLock;
use tracing::warn;

pub fn load_config() -> &'static Config {
    dotenv().ok();
    static INSTANCE: OnceLock<Config> = OnceLock::new();

    INSTANCE.get_or_init(|| {
        Config::from_env().unwrap_or_else(|e| panic!("FATAL: Failed loading env variable. {:?}", e))
    })
}

#[allow(non_snake_case)]
pub struct Config {
    pub DATABASE_URL: String,
    pub LANGGRAPH_ASSISTANT_ENDPOINT: String,
    pub CLERK_RSA_MODULUS: String,
    pub CLERK_RSA_EXPONENT: String,
    pub PORT: String,
}

impl Config {
    fn from_env() -> Result<Config> {
        Ok(Config {
            DATABASE_URL: get_env("DATABASE_URL")?,
            LANGGRAPH_ASSISTANT_ENDPOINT: get_env("LANGGRAPH_ASSISTANT_ENDPOINT")?,
            CLERK_RSA_MODULUS: get_env("CLERK_RSA_MODULUS")?,
            CLERK_RSA_EXPONENT: get_env("CLERK_RSA_EXPONENT")?,
            PORT: get_env_opt("PORT", "8080"),
        })
    }
}

fn get_env(key: &'static str) -> Result<String> {
    env::var(key).map_err(|_| Error::ConfigMissingEnv(key))
}

fn get_env_opt(key: &str, default: &str) -> String {
    warn!(
        "Failed loading env variable: {}. Using fallback value: {}",
        key, default
    );
    env::var(key).unwrap_or_else(|_| default.to_string())
}
