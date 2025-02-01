package middleware

import (
	"context"
	"log/slog"
	"net/http"
	"time"

	"github.com/icefed/zlog"
)

const (
	maxLogLength = 200
)

func truncateString(s string, maxLength int) string {
	if len(s) <= maxLength {
		return s
	}
	return s[:maxLength]
}

type LogEntry struct {
	Timestamp  string `json:"timestamp"`
	Level      string `json:"level"`
	Method     string `json:"method"`
	Endpoint   string `json:"endpoint"`
	StatusCode int    `json:"status_code"`
	Request    string `json:"request"`
	Response   string `json:"response"`
}

type wrappedWriter struct {
	http.ResponseWriter
	statusCode int
}

func Logging(next http.Handler) http.Handler {
	logger := slog.New(zlog.NewJSONHandler(&zlog.Config{
		HandlerOptions: slog.HandlerOptions{
			Level: slog.LevelDebug,
		},
		Development: true,
	},
	))

	slog.SetDefault(logger)
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		wrapped := &wrappedWriter{
			ResponseWriter: w,
			statusCode:     http.StatusOK,
		}

		next.ServeHTTP(wrapped, r)
		slog.LogAttrs(
			context.Background(),
			slog.LevelInfo,
			"Request completed",
			slog.Int("status_code", wrapped.statusCode),
			slog.String("method", r.Method),
			slog.String("path", r.URL.Path),
			slog.String("time", time.Since(start).String()),
		)
	})
}
