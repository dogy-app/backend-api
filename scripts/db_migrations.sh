#!/bin/sh

# Run migrations
. ../.env

load_env() {
local varname=$1
local message=$2
  if [ -z "$(eval echo $varname)" ]; then
    echo "$message"
    exit 1
  fi
}


load_env "\$DATABASE_URL" "DATABASE_URL is not set. This is required to connect to your database."
load_env "\$WEB_BACKEND_PUBLIC_PASSWORD" "WEB_BACKEND_PUBLIC_PASSWORD is not set. This is required to set the password for the role web_backend_public."

compile() {
    echo "Compiling migrations..."
    if [ -z "$2" ]; then
        echo "Please provide a file to compile migration."
        exit 1
    fi
    cp ../migrations/$2 ../migrations/$2.source
    local envvar=$(grep -o "\${[[:alnum:]_]*}" ../migrations/$2)
    sed -i "s/$envvar/$(eval echo $envvar)/g" ../migrations/$2
    echo "Done."
}

decompile() {
    echo "Decompiling migrations..."
    if [ -z "$2" ]; then
        echo "Please provide a file to decompile migration to its source file."
        exit 1
    fi
    mv ../migrations/$2.source ../migrations/$2
    echo "Done"
}

case "$1" in
    compile) compile "$@"
    ;;
    decompile) decompile "$@"
    ;;
    *) echo "Usage: $0 {compile|decompile}"
    ;;
esac

