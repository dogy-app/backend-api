package database

import (
	"context"
	"log"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/dogy-app/backend-api/config"
)

var Pool *pgxpool.Pool

func ConnectDB() {
	config, err := pgxpool.ParseConfig(config.Env.DatabaseURI)
	if err != nil {
		log.Fatal(err)
	}

	config.MaxConns = 10
	config.MinConns = 2
	config.MaxConnIdleTime = 5 * time.Minute

	pool, err := pgxpool.NewWithConfig(context.Background(), config)
	if err != nil {
		log.Fatal(err)
	}
	Pool = pool
	log.Println("", Pool.Stat().IdleConns(), "database connection(s) established.")
}

func CloseDB() {
	if Pool != nil {
		Pool.Close()
		log.Println("Closed database connection pool.")
	}
}
