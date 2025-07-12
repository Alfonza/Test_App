package main

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

type test struct {
	test_case_name string
	request_body   interface{}
	response_body  interface{}
	response_code  int
}

func testGenerateOTP(t *testing.T) {
	endpoint := "/generate_otp"
	request_method := "POST"
	tests := []test{
		{
			test_case_name: "Successful OTP generation",
			request_body:   `{"phone_num": "1234567890"}`,
			response_body:  "",
			response_code:  200,
		},
	}
	for _, test := range tests {
		t.Run(test.test_case_name, func(t *testing.T) {
			req, _ := http.NewRequest(request_method, endpoint, strings.NewReader(test.request_body))
			rr := httptest.NewRecorder()
			handler := http.HandlerFunc(generate_otp)
			handler.ServeHTTP(rr, req)
			assert.Equal(t, test.response_code, rr.Code)
			assert.Equal(t, test.response_body, rr.Body.String())
		},
		)
	}
}

func testValidateOTP(t *testing.T) {
	endpoint := "/validate_otp"
	request_method := "POST"
	tests := []test{
		{
			test_case_name: "Successful OTP validation",
			request_body:   `{"phone_num": "1234567890", "otp": "123456"}`,
			response_code:  200,
			response_body:  "{token: 123456}",
		},
		{
			test_case_name: "Invalid OTP",
			request_body:   `{"phone_num": "1234567890", "otp": "123456"}`,
			response_code:  401,
			response_body:  "",
		},
	}

	for _, test := range tests {
		t.Run(test.test_case_name, func(t *testing.T) {
			req, _ := http.NewRequest(request_method, endpoint, strings.NewReader(test.request_body))
			rr := httptest.NewRecorder()
			handler := http.HandlerFunc(validate_otp)
			handler.ServeHTTP(rr, req)
			assert.Equal(t, test.response_code, rr.Code)
			assert.Equal(t, test.response_body, rr.Body.String())
		})
	}
}
