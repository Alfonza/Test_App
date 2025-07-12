package main

import (
	"encoding/json"
	"net/http"
)

type errorResponse struct {
	Error_code string
	Error_msg  string
}

func raiseBadRequest(w http.ResponseWriter, displayString string) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.WriteHeader(http.StatusBadRequest)
	error_json := errorResponse{"INVALID_FIELD", displayString}
	json.NewEncoder(w).Encode(error_json)
}

func raiseErrorResponse(w http.ResponseWriter, status_code int, error_code string, error_message string) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.WriteHeader(status_code)
	error_body := errorResponse{error_code, error_message}
	json.NewEncoder(w).Encode(error_body)
}
