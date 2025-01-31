package main

import (
	"encoding/json"
	"fmt"
	"log"
	"log/slog"
	"net/http"

	"github.com/dogy-app/backend-api/internal/middleware"
)

type HelloWorldResponse struct {
	Message string `json:"message"`
}

func main() {
	fmt.Println("Starting server on :8080")

	rootRouter := http.NewServeMux()
	rootRouter.HandleFunc("GET /", func(w http.ResponseWriter, r *http.Request) {
		json.NewEncoder(w).Encode(HelloWorldResponse{Message: "Hello World!!"})
	})

	rootRouter.Handle("/", http.StripPrefix("", rootRouter))

	router := http.NewServeMux()
	stack := middleware.CreateStack(
		middleware.Logging,
		middleware.ValidateToken,
	)

	router.HandleFunc("GET /", func(w http.ResponseWriter, r *http.Request) {
		json.NewEncoder(w).Encode(HelloWorldResponse{Message: "Hello World!!"})
	})

	v1Router := http.NewServeMux()
	v1Router.Handle("/api/v1/", http.StripPrefix("/api/v1", router))

	userRouter := http.NewServeMux()
	userRouter.Handle("/users/", http.StripPrefix("/users", v1Router))

	server := http.Server{
		Addr:    ":8080",
		Handler: stack(rootRouter),
	}

	err := server.ListenAndServe()
	if err != nil {
		slog.Error("There was an issue starting the server: ")
		log.Fatal(err)
	}
}
