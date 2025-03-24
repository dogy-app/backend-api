# Use a minimal base image for building
FROM rust:1.85 AS builder

# Set the working directory
WORKDIR /app

# Cache dependencies
COPY Cargo.toml Cargo.lock ./
COPY src/ ./src

# Pre-build dependencies (optimized caching)
RUN cargo build --release --bin dogy-backend-api

# Create a minimal final image
FROM debian:bookworm-slim

# Install runtime dependencies (OpenSSL and CA certificates)
RUN apt-get update && apt-get install -y libssl3 ca-certificates && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the built binary from the builder stage
COPY --from=builder /app/target/release/dogy-backend-api ./

# Set permissions
RUN chmod +x ./dogy-backend-api

# Define the entry point
ENTRYPOINT ["./dogy-backend-api"]
