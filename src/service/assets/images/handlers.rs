use std::sync::OnceLock;

use axum::{
    body::Bytes,
    extract::{Multipart, Query},
    Json,
};
use azure_storage::StorageCredentials;
use azure_storage_blobs::prelude::ClientBuilder;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use uuid::Uuid;

use crate::config::load_config;

/// Response body after successfully uploaded an image.
#[derive(Debug, Serialize)]
pub struct ImageUploadResponse {
    /// Azure blob URL after upload
    pub url: String,
    /// Human-readable image name
    pub image_name: String,
}

/// Query parameter for uploading image
#[derive(Debug, Deserialize)]
pub struct ImageUploadRequest {
    /// Optional custom blob name.
    pub name: Option<String>,
}

/// Query parameter for deleting image
#[derive(Debug, Deserialize)]
pub struct ImageDeleteRequest {
    /// The blob name of the blob that you want to delete.
    pub name: String,
}

/// Retrieves azure blob storage credentials and caches it.
///
/// Note that we need to return the storage credential instead of the [`ClientBuilder`]
/// as the request or more specifically the blob name and file content changes per request.
fn get_storage_credentials() -> &'static StorageCredentials {
    static STORAGE_CREDENTIALS_INSTANCE: OnceLock<StorageCredentials> = OnceLock::new();

    STORAGE_CREDENTIALS_INSTANCE.get_or_init(|| {
        let config = load_config();
        let account = &config.STORAGE_ACCOUNT;
        let access_key = &config.STORAGE_ACCESS_KEY;
        StorageCredentials::access_key(account, access_key.clone())
    })
}

async fn upload_blob(blob_name: String, data: &Bytes, content_type: String) -> String {
    let storage_credentials = get_storage_credentials();
    let config = load_config();
    let account = &config.STORAGE_ACCOUNT;
    let container = &config.STORAGE_CONTAINER;
    let _ = ClientBuilder::new(account, storage_credentials.to_owned())
        .blob_client(container, &blob_name)
        .put_block_blob(data.to_owned())
        .content_type(content_type)
        .await
        .unwrap();

    format!(
        "https://{}.blob.core.windows.net/{}/{}",
        account, container, blob_name
    )
}

async fn delete_blob(blob_name: &str) {
    let storage_credentials = get_storage_credentials();
    let config = load_config();
    let account = &config.STORAGE_ACCOUNT;
    let container = &config.STORAGE_CONTAINER;
    let _ = ClientBuilder::new(account, storage_credentials.to_owned())
        .blob_client(container, blob_name)
        .delete()
        .await
        .unwrap();
}

fn retrieve_base_name_from_file(custom_name: &Option<String>, filename: &str) -> String {
    match custom_name {
        Some(name) => name.replace(" ", "_"),
        None => filename.replace(" ", "_"),
    }
}

fn convert_to_blob_name(full_filename: &str, custom_name: &Option<String>) -> (String, String) {
    let splitted_filename = full_filename
        .split_once('.')
        .unwrap_or((full_filename, ".jpg"));

    let extension = splitted_filename.1;
    let id = Uuid::new_v4().to_string();
    let base_name = retrieve_base_name_from_file(custom_name, splitted_filename.0);

    (format!("{}_{}.{}", base_name, id, extension), base_name)
}

pub async fn upload_image(
    Query(img_req): Query<ImageUploadRequest>,
    mut multipart: Multipart,
) -> Json<ImageUploadResponse> {
    let mut blob_url = String::from("");
    let mut fallback_name = String::from("");

    // Iterate through all of the fields of FormData. However, we only really expect one field
    // which is the file itself.
    while let Some(field) = multipart.next_field().await.unwrap() {
        let filename = field.file_name().unwrap().to_string();
        let content_type = field.content_type().unwrap().to_string();
        let data = field.bytes().await.unwrap();
        let (blob_name, image_name) = convert_to_blob_name(&filename, &img_req.name);
        blob_url = upload_blob(blob_name, &data, content_type).await;
        fallback_name = image_name;

        dbg!(&filename);
    }

    Json(ImageUploadResponse {
        image_name: img_req.name.unwrap_or(fallback_name),
        url: blob_url,
    })
}

pub async fn delete_image(Query(img_req): Query<ImageDeleteRequest>) -> Json<Value> {
    delete_blob(&img_req.name).await;

    Json(json!({
        "message": format!("Blob `{}` deleted successfully.", img_req.name)
    }))
}
