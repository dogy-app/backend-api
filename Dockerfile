# Create a minimal final image
FROM debian:bookworm-slim

# Install runtime dependencies (OpenSSL and CA certificates)
RUN apt-get update && apt-get install -y libssl3 ca-certificates && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /usr/local/application

# Copy the built binary from the builder stage
COPY target/release/dogy-backend-api /usr/local/bin/dogy-backend-api

# Set permissions
RUN chmod +x /usr/local/bin/dogy-backend-api

# Expose Port
EXPOSE 8080

# Define the entry point
ENTRYPOINT ["dogy-backend-api"]
