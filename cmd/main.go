package main

import (
	"log"

	"github.com/dogy-app/backend-api/cmd/api"
	"github.com/dogy-app/backend-api/config"
)

func main() {
	server := api.NewAPIServer(config.Env.Port)
	if err := server.Start(); err != nil {
		log.Fatal("Failed to start server: ", err)
	}
}
