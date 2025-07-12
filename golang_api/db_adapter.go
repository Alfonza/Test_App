package main

import (
	"context"
	"fmt"
	"os"
	"sync"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

var (
	db_conn *pgxpool.Pool
	once    sync.Once
)

// Function to connect to the database only once
func connect_database() {
	once.Do(func() {
		// Example configuration (Replace with actual config retrieval)

		db_details := config.Database_details
		Database_url := fmt.Sprintf("postgres://%s:%s@%s:%s/%s",
			db_details["username"], db_details["password"], db_details["host"],
			db_details["port"], db_details["database_name"])

		var err error
		db_conn, err = pgxpool.New(context.Background(), Database_url)
		if err != nil {
			LogErrorWithStack(err, "Unable to connect to database: \n")
			os.Exit(1)
		} else {
			dbHealthCheck()
			fmt.Println("Database connected successfully!")
		}
	})
}

func dbHealthCheck() error {
	// A simple query to verify the connection is alive
	// 'SELECT 1' is a lightweight query
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// Execute a simple query to check if the connection is alive
	err := db_conn.Ping(ctx)
	if err != nil {
		LogErrorWithStack(err, "database is not reachable")
		panic("database is not reachable")
	}

	// Optional: Run a basic query to verify that it's connected properly
	// This ensures that the connection works without errors
	var result string
	err = db_conn.QueryRow(ctx, "SELECT 'Connected'").Scan(&result)
	if err != nil {
		return fmt.Errorf("error running query: %v", err)
	}

	// If no error, return nil indicating successful connection
	fmt.Println(result) // Output: Connected
	return nil
}

func closeDatabase() {
	if db_conn != nil {
		db_conn.Close()
		fmt.Println("Database connection closed.")
	}
}

type AnnualBookingItem struct {
	Start_date time.Time `json:"start_date"`
	End_date   time.Time `json:"end_date"`
	Num_guests int       `json:"num_guests"`
}
type bookingsItem struct {
	AnnualBookingItem
	Booking_id    int64  `json:"booking_id"`
	Customer_name string `json:"customer_name"`
}

// Function to fetch bookings by date
func selectBookingsInYearByHotel(hotel_id int, year int) ([]AnnualBookingItem, error) {
	if db_conn == nil {
		return nil, fmt.Errorf("database connection lost")
	}

	rows, err := db_conn.Query(context.Background(),
		"SELECT date,Num_guests,Start_date,End_date FROM bookings b WHERE b.hotel_id = $1 AND (EXTRACT(YEAR FROM b.start_date) = $2 OR EXTRACT(YEAR FROM b.end_date) = $2", hotel_id, year)

	if err != nil {
		return nil, err
	}
	all_bookings_list := make([]AnnualBookingItem, 0)
	for rows.Next() {
		var booking AnnualBookingItem
		err := rows.Scan(&booking.Start_date, &booking.End_date, &booking.Num_guests)
		if err != nil {
			return nil, err
		}
		all_bookings_list = append(all_bookings_list, booking)
	}

	defer rows.Close()
	return all_bookings_list, nil
}
func selectBookingsByDate(hotel_id int, date string) ([]bookingsItem, error) {
	if db_conn == nil {
		return nil, fmt.Errorf("database connection lost")
	}
	logger.Info().("selectBookingsByDate")
	rows, err := db_conn.Query(context.Background(),
		"SELECT b.id, c.name, b.num_guests, b.start_date, b.end_date FROM bookings b JOIN customers c ON b.id = c.id WHERE b.start_date = $2 AND b.hotel_id = $1", hotel_id, date)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	bookingsList := make([]bookingsItem, 0)

	for rows.Next() {
		var booking bookingsItem
		err := rows.Scan(&booking.Booking_id, &booking.Customer_name, &booking.Num_guests, &booking.Start_date, &booking.End_date)
		if err != nil {
			return nil, err
		}
		bookingsList = append(bookingsList, booking)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return bookingsList, nil
}

type hidden_bookingsItem struct {
	Start_date time.Time `json:"start_date"`
	End_date   time.Time `json:"end_date"`
}
type owner_bookingsItem struct {
	Start_date    time.Time `json:"start_date"`
	End_date      time.Time `json:"end_date"`
	Booking_id    int       `json:"booking_id"`
	Customer_name string    `json:"customer_name"`
	Num_guests    int       `json:"num_guests"`
	Phone_number  string    `json:"phone_number"`
}

func calculateRemainingCapacities(hotel_id int, start_date time.Time, end_date time.Time) ([]int, error) {

	if db_conn == nil {
		return nil, fmt.Errorf("database connection lost")
	}

	rows, err := db_conn.Query(context.Background(),
		"SELECT h.capacity - COALESCE(SUM(b.num_guests), 0) AS remaining_capacity FROM hotels h LEFT JOIN bookings b ON h.hotel_id = b.hotel_id AND b.start_date <= $2 AND b.end_date >= $1 WHERE h.hotel_id = $3 GROUP BY h.capacity, b.start_date, b.end_date ORDER BY b.start_date", start_date, end_date, hotel_id) // TODO: understand the query
	if err != nil {
		return nil, err
	}

	defer rows.Close()

	remaining_capacities := make([]int, 0)
	for rows.Next() {
		var remaining_capacity int
		err := rows.Scan(&remaining_capacity)
		if err != nil {
			return nil, err
		}
		remaining_capacities = append(remaining_capacities, remaining_capacity)
	}
	if err = rows.Err(); err != nil {
		return nil, err
	}
	return remaining_capacities, nil
}

func insertBookingByOwner(hotel_id int, customer_name string, phone_num int64, start_date time.Time, end_date time.Time, num_guests int) error {
	if db_conn == nil {
		return fmt.Errorf("database connection lost")
	}
	_, err := db_conn.Exec(context.Background(),
		"INSERT INTO bookings (hotel_id, customer_id, start_date, end_date, num_guests, booked_by_owner) VALUES ($1, $2,$3, $4, $5, $6, true)", hotel_id, customer_name, phone_num, start_date, end_date, num_guests)
	return err
}
func selectOwnerBookings(hotel_id int) ([]owner_bookingsItem, error) {
	if db_conn == nil {
		return nil, fmt.Errorf("database connection lost")
	}
	rows, err := db_conn.Query(context.Background(),
		"SELECT b.start_date, b.end_date,b.booking_id, c.name ,b.num_guests,c.phone_num FROM bookings b, customers c JOIN b.customer_id = c.id WHERE b.hotel_id = $1 AND b.booked_by_owner = true AND b.end_date >= CURRENT_DATE ORDER BY start_date", hotel_id)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	all_bookings_list := make([]owner_bookingsItem, 0)
	for rows.Next() {
		var booking owner_bookingsItem
		err := rows.Scan(&booking.Start_date, &booking.End_date, &booking.Booking_id, &booking.Customer_name, &booking.Num_guests, &booking.Phone_number)
		if err != nil {
			return nil, err
		}
		all_bookings_list = append(all_bookings_list, booking)
	}
	if err = rows.Err(); err != nil {
		return nil, err
	}
	return all_bookings_list, nil
}

func bookingExistsBetweenDate(start_date string, end_date string) (bool, error) {
	if db_conn == nil {
		return false, fmt.Errorf("database connection lost")
	}
	var exists bool
	err := db_conn.QueryRow(context.Background(),
		"SELECT EXISTS (select 1 from bookings WHERE start_date <= $2 AND end_date >= $1)", start_date, end_date).Scan(&exists)
	if err != nil {
		return false, err
	}
	return exists, err

}
func deleteDeactivationById(entry_id int) error {
	if db_conn == nil {
		return fmt.Errorf("database connection lost")
	}
	_, err := db_conn.Exec(context.Background(),
		"DELETE FROM hotel_deactivations WHERE id = $1", entry_id)
	return err
}
func insertDeactivationEntry(hotel_id int, start_date string, end_date string) error {
	if db_conn == nil {
		return fmt.Errorf("database connection lost")
	}
	_, err := db_conn.Exec(context.Background(),
		"INSERT INTO hotel_deactivations (hotel_id, start_date, end_date) VALUES ($1, $2, $3)", hotel_id, start_date, end_date)
	return err
}

func deleteBookingById(booking_id int) error {
	if db_conn == nil {
		return fmt.Errorf("database connection lost")
	}
	_, err := db_conn.Exec(context.Background(), "DELETE FROM bookings WHERE id = $1", booking_id)
	return err
}
func selectDeactivationsByHotelId(hotel_id int) ([]hidden_bookingsItem, error) {
	if db_conn == nil {
		return nil, fmt.Errorf("database connection lost")
	}
	rows, err := db_conn.Query(context.Background(),
		"SELECT start_date, end_date FROM hotel_deactivations WHERE hotel_id = $1 AND end_date >= CURRENT_DATE ORDER BY start_date", hotel_id)
	if err != nil {
		return nil, err
	}
	hidden_bookingsList := make([]hidden_bookingsItem, 0)
	for rows.Next() {
		var hidden_booking hidden_bookingsItem
		err := rows.Scan(&hidden_booking.Start_date, &hidden_booking.End_date)
		if err != nil {
			return nil, err
		}
		hidden_bookingsList = append(hidden_bookingsList, hidden_booking)
	}
	defer rows.Close()
	return hidden_bookingsList, nil
}
