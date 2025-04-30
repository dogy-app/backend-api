<!-- @format -->

# Dogy Backend

Backend API service for dogy app

### Steps to start

1. Install rust toolchain.
2. Create `.env` file add the keys from `.env.example`.
3. Build the project with `cargo build` or if you are in release mode, `cargo build --release`.
4. Run the API with `cargo run` to start dev server. Be sure you have a docker image with PostGIS and pg_uuidv7 extension.
   The auth token will come from the JWT template in clerk dev mode. This is different from the production mode.
