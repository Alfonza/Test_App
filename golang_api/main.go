package main

import (
	"net/http"

	"github.com/go-chi/chi/v5"
)

func main() {
	r := chi.NewRouter()
	init_logger()

	r.Use(loggingMiddleware)
	r.Route("/hotels/", func(r chi.Router) {
		r.Use(jwtAuthMiddleware)
		r.Get("/bookings/{date}", getBookingListByDate)
		r.Get("/calender/{year}", getAnnualBookingSummary)
		r.Get("/deactivation_dates", getDeactivationList)
		r.Post("/deactivation_dates", postDeactivation)
		r.Delete("/deactivation_dates/{id}", deleteDeactivation)
		r.Get("/owner_bookings", getOwnerBookings)
		r.Post("/owner_bookings", postOwnerBooking)
		r.Delete("/owner_bookings/{id}", deleteOwnerBooking)
	})
	r.Post("/generate_otp", generate_otp)
	r.Post("/validate_otp", validate_otp)
	connect_database()
	defer closeDatabase() // Ensure DB connection is closed when program exits
	http.ListenAndServe(":3000", r)
}
