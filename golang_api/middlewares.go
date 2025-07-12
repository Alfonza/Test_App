package main

import (
	"context"
	"net/http"
	"runtime/debug"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type contextKey string

const claimsContextKey = contextKey("claims")

func jwtAuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		authHeader := r.Header.Get("Authorization")
		if authHeader == "" {
			http.Error(w, "missing authorization header", http.StatusUnauthorized)
			return
		}
		token_string := strings.TrimPrefix(authHeader, "Bearer ")
		claims := &JwtClaims{}
		token, err := jwt.ParseWithClaims(token_string, claims, func(token *jwt.Token) (interface{}, error) {
			return jwtSecret, nil
		})
		if err != nil || !token.Valid {
			http.Error(w, "invalid token", http.StatusUnauthorized)
			return
		}
		ctx := r.Context()
		ctx = context.WithValue(ctx, claimsContextKey, claims)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start_time := time.Now()

		defer func() {
			if err := recover(); err != nil {
				logger.Error().
					Str("method", r.Method).
					Str("path", r.URL.Path).
					Str("remote_addr", r.RemoteAddr).
					Str("user_agent", r.UserAgent()).
					Str("stack_trace", string(debug.Stack())). // Capturing full stack trace
					Time("timestamp", time.Now()).
					Msgf("Server error: %v", err)
			}
		}()

		next.ServeHTTP(w, r)

		logger.Info().
			Str("method", r.Method).
			Str("path", r.URL.Path).
			Str("remote_addr", r.RemoteAddr).
			Str("user_agent", r.UserAgent()).
			Str("duration", time.Since(start_time).String()).
			Msg("Request handled")
	})
}
