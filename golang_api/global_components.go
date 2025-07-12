package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"gopkg.in/yaml.v3"
)

var jwtSecret = []byte("secret")

type ConfigType struct {
	Database_details map[string]string
	Datetime         map[string]string
}

func getConfig() ConfigType {
	config_file, err := os.ReadFile("server_config.yaml")
	if err != nil {
		log.Fatal(err)
	}
	var config ConfigType
	err = yaml.Unmarshal(config_file, &config)
	if err != nil {
		log.Fatal(err)
	}
	return config
}
func convertToJsonResponse(w http.ResponseWriter, statusCode int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)

	// Encode response data into JSON and write to response
	if err := json.NewEncoder(w).Encode(data); err != nil {
		http.Error(w, "Failed to encode JSON", http.StatusInternalServerError)
	}
}

type JwtClaims struct {
	Hotel_id int `json:"hotel_id"`
	User_id  int `json:"user_id"`
	jwt.RegisteredClaims
}

func generateJWT(hotel_id int, user_id int) (string, error) {
	expiry_time := time.Now().Add(14 * 24 * time.Hour)
	claims := &JwtClaims{
		Hotel_id: hotel_id,
		User_id:  user_id,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(expiry_time),
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	return token.SignedString(jwtSecret)
}
