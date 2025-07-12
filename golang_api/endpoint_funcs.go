// file that defines every endpoints

package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/go-chi/chi/v5"
)

var config = getConfig()

func isValidDate(date string, date_format string) bool {

	_, err := time.Parse(date_format, date)
	return err == nil
}

func getBookingListByDate(w http.ResponseWriter, r *http.Request) {
	hotel_id := r.Context().Value(claimsContextKey).(int)
	date := chi.URLParam(r, "date")
	date_format := config.Datetime["dateformat"]
	if !isValidDate(date, date_format) {
		raiseBadRequest(w, "date not valid or date format not matching "+date_format)
		return
	}
	rows, err := selectBookingsByDate(hotel_id, date)
	if err != nil {
		LogErrorWithStack(err, "Error while getting bookings by date")
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
	} else {
		w.Header().Set("Content-Type", "application/json")
		fmt.Printf("%+v\n", rows)
		json.NewEncoder(w).Encode(rows)
	}
}

func generate_otp(w http.ResponseWriter, r *http.Request) {
	// TODO: code for generating OTP
	var req generateOTPRequest
	err := json.NewDecoder(r.Body).Decode(&req) // err not handled
	if err != nil {
		raiseBadRequest(w, "Invalid request body")
		return
	}
	if req.Phone_num == 9876543210 {
		return
	} else {
		raiseErrorResponse(w, http.StatusConflict, BUSINESS_LOGIC_ERROR, "Phone number not registered")
		return
	}
}

type createDeactivationRequestModel struct {
	Start_date string `json:"start_date"`
	End_date   string `json:"end_date"`
}

func deleteOwnerBooking(w http.ResponseWriter, r *http.Request) {
	booking_id, err := strconv.Atoi(chi.URLParam(r, "booking_id"))
	if err != nil {
		raiseBadRequest(w, "Invalid booking id")
		return
	}
	err = deleteBookingById(booking_id)
	if err != nil {
		LogErrorWithStack(err, "Error while deleting booking by id")
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
func postDeactivation(w http.ResponseWriter, r *http.Request) {
	var req createDeactivationRequestModel
	err := json.NewDecoder(r.Body).Decode(&req) // err not handled
	if err != nil {
		raiseBadRequest(w, "Invalid request body")
		return
	}
	hotel_id := r.Context().Value(claimsContextKey).(int)
	booking_exists, err := bookingExistsBetweenDate(req.Start_date, req.End_date)
	if err != nil {
		LogErrorWithStack(err, "Error while getting bookings by start and end date")
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
	if booking_exists {
		raiseErrorResponse(w, http.StatusConflict, BUSINESS_LOGIC_ERROR, "Booking already exists for the given date range")
		return
	}
	err = insertDeactivationEntry(hotel_id, req.Start_date, req.End_date)
	if err != nil {
		LogErrorWithStack(err, "Error while creating deactivation data ")
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
	} else {
		w.WriteHeader(http.StatusOK)
	}
}

type postOwnerBookingRequest struct {
	Start_date    time.Time `json:"start_date"`
	End_date      time.Time `json:"end_date"`
	Num_guests    int       `json:"num_guests"`
	Phone_num     *int64    `json:"phone_num"`
	Customer_name *string   `json:"customer_name"`
}

func postOwnerBooking(w http.ResponseWriter, r *http.Request) {
	var req postOwnerBookingRequest
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		raiseBadRequest(w, "Invalid request body")
		return
	}

	hotel_id := r.Context().Value(claimsContextKey).(int)
	remaining_capacities, err := calculateRemainingCapacities(hotel_id, req.Start_date, req.End_date)

	if err != nil {
		LogErrorWithStack(err, "Error while getting remaining capacity")
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	for i := 0; i < len(remaining_capacities); i++ {
		if req.Num_guests > remaining_capacities[i] {
			raiseErrorResponse(w, http.StatusConflict, BUSINESS_LOGIC_ERROR, "Not enough capacity")
			return
		}
	}

	err = insertBookingByOwner(hotel_id, *req.Customer_name, *req.Phone_num, req.Start_date, req.End_date, req.Num_guests)
	if err != nil {
		LogErrorWithStack(err, "Error while creating booking")
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
	} else {
		w.WriteHeader(http.StatusOK)
	}
}

func getOwnerBookings(w http.ResponseWriter, r *http.Request) {
	hotel_id := r.Context().Value(claimsContextKey).(int)
	owner_bookings, err := selectOwnerBookings(hotel_id)
	if err != nil {
		LogErrorWithStack(err, "Error while getting bookings by hotel id")
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
	convertToJsonResponse(w, http.StatusOK, owner_bookings)
}
func deleteDeactivation(w http.ResponseWriter, r *http.Request) {
	entry_id := chi.URLParam(r, "id")
	entry_id_int, err := strconv.Atoi(entry_id)
	if err != nil {
		raiseBadRequest(w, "Invalid entry id in url parameter")
		return
	}
	err = deleteDeactivationById(entry_id_int)
	if err != nil {
		LogErrorWithStack(err, "Error while deleting deactivation")
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
	} else {
		w.WriteHeader(http.StatusOK)
	}
}
func getDeactivationList(w http.ResponseWriter, r *http.Request) {
	hotel_id := r.Context().Value(claimsContextKey).(int)
	rows, err := selectDeactivationsByHotelId(hotel_id)
	if err != nil {
		LogErrorWithStack(err, "Error while getting deactivation data ")
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
	} else {
		convertToJsonResponse(w, http.StatusOK, rows)
		return
	}
}
func getAnnualBookingSummary(w http.ResponseWriter, r *http.Request) {
	year := chi.URLParam(r, "year")

	hotel_id := r.Context().Value(claimsContextKey).(int)

	if !isValidDate(year, "2006") {
		raiseBadRequest(w, "year not valid")
		return
	}
	year_int, _ := strconv.Atoi(year)

	rows, err := selectBookingsInYearByHotel(hotel_id, year_int)

	if err != nil {
		LogErrorWithStack(err, "Error while getting annual booking summary")
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
	} else {

		annualBookingSummary := make(map[string]int)

		for i := 0; i < len(rows); i++ {
			row := rows[i]
			start_date := row.Start_date
			end_date := row.End_date
			start_year := start_date.Year()
			var first_date time.Time
			var last_date time.Time
			if start_year != year_int {
				first_date, _ = time.Parse("2006-01-02", year+"-01-01")
			} else {
				first_date = start_date
			}
			if last_date.Year() != year_int {
				last_date, _ = time.Parse("2006-01-02", year+"-12-31")
			} else {
				last_date = end_date
			}
			for d := first_date; d.After(last_date) || d.Equal(last_date); d = d.AddDate(0, 0, 1) {
				key := d.Format("01-02")
				annualBookingSummary[key] = annualBookingSummary[key] + row.Num_guests
			}
		}
		convertToJsonResponse(w, http.StatusOK, annualBookingSummary)
		return
	}
}

func validate_otp(w http.ResponseWriter, r *http.Request) {
	var req validateOTPRequest
	err := json.NewDecoder(r.Body).Decode(&req) // err not handled properly
	if err != nil {
		raiseErrorResponse(w, http.StatusBadRequest, INVALID_FIELD, "invalid field")
		return
	}
	// TODO: validate otp and get customer_id
	owner_id := 11
	var hotel_id int = 16

	token, err := generateJWT(owner_id, hotel_id)
	if err != nil {
		raiseErrorResponse(w, http.StatusInternalServerError, UNKNOWN_ERROR, "Error generating token")
		return
	}
	final_response := validateOTPResponse{token}
	convertToJsonResponse(w, http.StatusOK, final_response)
}
