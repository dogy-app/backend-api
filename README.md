<!-- @format -->
<div align="center">
   <img src="https://github.com/user-attachments/assets/5c7273ec-a1be-4057-8ba5-ced93c88b2a0" alt="Logo" width=200 />

   <h1> Dogy Backend API </h1>


   **Backend REST API service for Dogy app written in Rust.**


   [![Release](https://github.com/dogy-app/backend-api/actions/workflows/release.yml/badge.svg)](https://github.com/dogy-app/backend-api/actions/workflows/release.yml)
   ![Rust version](https://img.shields.io/badge/cargo-v1.86.0-f64d00)
   [![Latest version](https://img.shields.io/badge/latest_version-v0.3.0-blue)](https://github.com/dogy-app/backend-api/releases/tag/v0.3.0)
   [![Code Documentation](https://img.shields.io/badge/code%20documentation-8A2BE2)](https://dogy-backend.pages.dev/dogy_backend_api)
   [![API Documentation](https://img.shields.io/badge/api%20documentation-pink)](https://dogy.apidocumentation.com/reference)

</div>

## Features
- User Authentication with Clerk (JWT)
- Uploading Assets (eg. pet images)
- Fetching/Saving User & Pet Data
- Management of AI Assistant Threads
- Daily Challenges
- Robust Error Handling
- Detailed Logs
- Type-safe Interaction with Database
- Database Migration with `sqlx`
- Automated CI/CD for Build & Release in Azure
- OpenAPI Documentation
- Code documentation with `docs.rs`

## Usage
This is a REST API so it should work for any programming language with an HTTP client. I recommend trying the endpoint first in Postman or Insomnia.
All the endpoints are documented using Scalar. You can find the [documentation](https://dogy.apidocumentation.com/reference) here.
Do note that most of the endpoints in this API can only be accessed with JWT token, not just for security, but in order to also retrieve the current user's data.
Some endpoints that dont require it are health checks so that Azure can ping it properly.

Due to the robust error handling in this API, all client errors must have a short self-explanatory error codes and a corresponding HTTP error code.

## Architecture
The architecture involved in this backend follows the best practices for security, scaling, and performance.
Here is the database schema with Postgresql Database with PostGIS and pg_uuidv7 extensions:
![db schema](https://github.com/user-attachments/assets/7b99cf94-6453-459c-9856-22464bf88ee7)
![db schema 2](https://github.com/user-attachments/assets/35b35fc5-8f20-4ff1-96a9-8ca56a2ed9a7)

In addition, all Azure services follow the [naming convention](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming) from Microsoft themselves. Here is how the cloud services is architectured:
![image](https://github.com/user-attachments/assets/197b6c49-e74b-4fb2-98fe-80e9dd9734b2)

## How to Contribute?
1. Install rust toolchain (`v1.86.0`).
2. Create `.env` file add the keys from `.env.example`.
3. Build the project with `cargo build` or if you are in release mode, `cargo build --release`.
4. Run the API with `cargo run` to start dev server. Be sure you have a docker image with PostGIS and pg_uuidv7 extension.
   The auth token will come from the JWT template in clerk dev mode. This is different from the production mode.

## Do you have a question?
If you have any question or inquiry, feel free to email me or open an issue here. I'll be sure to respond and provide insights given your question.
