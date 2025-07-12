package main

type generateOTPRequest struct {
	Phone_num int64 `json:"phone_num"`
}

type validateOTPRequest struct {
	Phone_num int64 `json:"phone_num"`
	Otp       int   `json:"otp"`
}
