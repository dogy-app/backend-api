use crate::{Error, Result};
use dotenv::dotenv;
use std::env;
use std::sync::OnceLock;
use tracing::warn;

pub fn load_config() -> &'static Config {
    #[cfg(not(test))]
    dotenv().ok();

    static INSTANCE: OnceLock<Config> = OnceLock::new();

    INSTANCE.get_or_init(|| {
        Config::from_env().unwrap_or_else(|e| panic!("FATAL: Failed loading env variable. {:?}", e))
    })
}

#[allow(non_snake_case)]
#[derive(Debug, Clone, PartialEq)]
pub struct Config {
    pub DATABASE_URL: String,
    pub LANGGRAPH_ASSISTANT_ENDPOINT: String,
    pub AZURE_OPENAI_ENDPOINT: String,
    pub AZURE_OPENAI_KEY: String,
    pub CLERK_RSA_MODULUS: String,
    pub CLERK_RSA_EXPONENT: String,
    pub STORAGE_ACCOUNT: String,
    pub STORAGE_ACCESS_KEY: String,
    pub STORAGE_CONTAINER: String,
    pub PORT: String,
}

impl Config {
    fn from_env() -> Result<Self> {
        Ok(Self {
            DATABASE_URL: get_env("DATABASE_URL")?,
            LANGGRAPH_ASSISTANT_ENDPOINT: get_env("LANGGRAPH_ASSISTANT_ENDPOINT")?,
            AZURE_OPENAI_ENDPOINT: get_env("AZURE_OPENAI_ENDPOINT")?,
            AZURE_OPENAI_KEY: get_env("AZURE_OPENAI_KEY")?,
            CLERK_RSA_MODULUS: get_env("CLERK_RSA_MODULUS")?,
            CLERK_RSA_EXPONENT: get_env("CLERK_RSA_EXPONENT")?,
            STORAGE_ACCOUNT: get_env("STORAGE_ACCOUNT")?,
            STORAGE_ACCESS_KEY: get_env("STORAGE_ACCESS_KEY")?,
            STORAGE_CONTAINER: get_env("STORAGE_CONTAINER")?,
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

#[cfg(test)]
mod test {
    use super::*;
    use std::env;

    #[test]
    fn test_get_env_ok() {
        // In Rust 2024 Edition, env::set_var is considered unsafe.
        unsafe {
            env::set_var("DATABASE_URL", "test_url");
        }
        let database_url = get_env("DATABASE_URL").unwrap();
        assert_eq!(database_url, "test_url".to_string());
    }

    #[test]
    fn test_get_env_config_missing_err() {
        let database_url = get_env("DATABASE_URL");
        assert!(
            matches!(database_url, Err(Error::ConfigMissingEnv("DATABASE_URL"))),
            "Expected ConfigMissingEnv error"
        );
    }

    #[test]
    fn test_get_env_opt_default() {
        let database_url = get_env_opt("DATABASE_URL", "test_url");
        assert_eq!(database_url, "test_url".to_string());
    }

    #[test]
    fn test_get_env_opt_override() {
        unsafe {
            env::set_var("DATABASE_URL", "override_test_url");
        }
        let database_url = get_env_opt("DATABASE_URL", "test_url");
        assert_eq!(database_url, "override_test_url".to_string());
    }

    #[test]
    fn test_config_from_env_ok() {
        unsafe {
            env::set_var("DATABASE_URL", "test_db_url");
            env::set_var("LANGGRAPH_ASSISTANT_ENDPOINT", "test_assistant_url");
            env::set_var("AZURE_OPENAI_ENDPOINT", "test_azure_openai_endpoint");
            env::set_var("AZURE_OPENAI_KEY", "test_azure_openai_key");
            env::set_var("CLERK_RSA_MODULUS", "test_modulus");
            env::set_var("CLERK_RSA_EXPONENT", "test_exponent");
            env::set_var("STORAGE_ACCOUNT", "test_storage_acc");
            env::set_var("STORAGE_ACCESS_KEY", "test_storage_key");
            env::set_var("STORAGE_CONTAINER", "test_storage_container");
            env::set_var("STORAGE_URL", "test_storage_url");
        }

        let config = Config::from_env().unwrap();
        assert_eq!(
            config,
            Config {
                PORT: "8080".to_string(),
                CLERK_RSA_EXPONENT: "test_exponent".to_string(),
                CLERK_RSA_MODULUS: "test_modulus".to_string(),
                LANGGRAPH_ASSISTANT_ENDPOINT: "test_assistant_url".to_string(),
                AZURE_OPENAI_ENDPOINT: "test_azure_openai_endpoint".to_string(),
                AZURE_OPENAI_KEY: "test_azure_openai_key".to_string(),
                DATABASE_URL: "test_db_url".to_string(),
                STORAGE_ACCOUNT: "test_storage_acc".to_string(),
                STORAGE_ACCESS_KEY: "test_storage_key".to_string(),
                STORAGE_CONTAINER: "test_storage_container".to_string(),
            }
        );
    }

    #[test]
    fn test_config_from_env_missing_db_url_err() {
        unsafe {
            env::set_var("LANGGRAPH_ASSISTANT_ENDPOINT", "test_assistant_url");
            env::set_var("CLERK_RSA_MODULUS", "test_modulus");
            env::set_var("CLERK_RSA_EXPONENT", "test_exponent");
        }

        let config = Config::from_env();
        assert!(
            matches!(config, Err(Error::ConfigMissingEnv("DATABASE_URL"))),
            "Expected ConfigMissingEnv error"
        );
    }

    #[test]
    fn test_load_config_ok() {
        unsafe {
            env::set_var("DATABASE_URL", "test_db_url");
            env::set_var("LANGGRAPH_ASSISTANT_ENDPOINT", "test_assistant_url");
            env::set_var("AZURE_OPENAI_ENDPOINT", "test_azure_openai_endpoint");
            env::set_var("AZURE_OPENAI_KEY", "test_azure_openai_key");
            env::set_var("CLERK_RSA_MODULUS", "test_modulus");
            env::set_var("CLERK_RSA_EXPONENT", "test_exponent");
            env::set_var("STORAGE_ACCOUNT", "test_storage_acc");
            env::set_var("STORAGE_ACCESS_KEY", "test_storage_key");
            env::set_var("STORAGE_CONTAINER", "test_storage_container");
        }

        let config = load_config();
        assert_eq!(
            config,
            &Config {
                PORT: "8080".to_string(),
                CLERK_RSA_EXPONENT: "test_exponent".to_string(),
                CLERK_RSA_MODULUS: "test_modulus".to_string(),
                LANGGRAPH_ASSISTANT_ENDPOINT: "test_assistant_url".to_string(),
                AZURE_OPENAI_ENDPOINT: "test_azure_openai_endpoint".to_string(),
                AZURE_OPENAI_KEY: "test_azure_openai_key".to_string(),
                DATABASE_URL: "test_db_url".to_string(),
                STORAGE_ACCOUNT: "test_storage_acc".to_string(),
                STORAGE_ACCESS_KEY: "test_storage_key".to_string(),
                STORAGE_CONTAINER: "test_storage_container".to_string(),
            }
        );
    }

    #[test]
    #[should_panic]
    fn test_load_config_panic() {
        unsafe {
            env::set_var("LANGGRAPH_ASSISTANT_ENDPOINT", "test_assistant_url");
            env::set_var("CLERK_RSA_MODULUS", "test_modulus");
            env::set_var("CLERK_RSA_EXPONENT", "test_exponent");
        }

        let _ = load_config();
    }
}
