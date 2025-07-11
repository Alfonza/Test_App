from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func,and_,or_
from app.models.db_models import Booking, HiddenDate
# from app.models.pydantic_models import 
from app.models.models import Hotel, Booking, HiddenDate,DeactivateHotel,BookingCreate, HiddenDateBase

class HotelRepository:
    # Create a booking
    @staticmethod
    async def create_booking(db: Session, booking: BookingCreate):
        db_booking = Booking(
            customer_id=booking.customer_id,
            hotel_id=booking.hotel_id,
            num_guests=booking.num_guests,
            start_date=booking.start_date,
            end_date=booking.end_date,
        )
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking

    # Get bookings for a specific date
    @staticmethod
    async def get_booking_by_date(db: Session, hotel_id: int, date: str):
        # Implement logic to fetch bookings for a specific date
        bookings = db.query(Booking).filter(Booking.hotel_id == hotel_id, 
                                         Booking.start_date <= date, 
                                         Booking.end_date >= date).all()
        if not bookings:
            return []

        # Map the bookings to the response structure
        return [{
            "name": booking.customer.name,
            "phone_num": booking.customer.phone_num,
            "num_guests": booking.num_guests
        } for booking in bookings]
    @staticmethod
    async def get_booking_by_year(db:Session,year,hotel_id:int):
        if year < 1000 or year > 9999:
            raise ValueError("Invalid year format")
        # Get the first and last date of the year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)

        # Query the bookings and group by date
        bookings_per_day = db.query(
            func.date(Booking.start_date).label('booking_date'),
            func.count(Booking.booking_id).label('booking_count')
        ).filter(
            Booking.hotel_id == hotel_id,
            Booking.start_date >= start_date,
            Booking.end_date <= end_date
        ).group_by('booking_date').all()

        # Format the result to match the expected response structure
        bookings_dict = {str(booking.booking_date): booking.booking_count for booking in bookings_per_day}

        # Return the formatted dictionary
        return bookings_dict
    # Create a hidden date
    @staticmethod
    async def create_hidden_date(db: Session, hotel_id: int, hidden_date: HiddenDateBase):
        try:
            conflict_exists = db.query(DeactivateHotel).filter(
            Booking.hotel_id == hotel_id,
            and_(
                and_(DeactivateHotel.start_date <= hidden_date.end_date, DeactivateHotel.end_date >= hidden_date.start_date)
            )
        ).first()

            if conflict_exists:
                raise ValueError("Booking conflict: There are existing bookings during the specified dates.")
            db_hidden_date = DeactivateHotel(
                hotel_id=hotel_id,
                start_date=hidden_date.start_date,
                end_date=hidden_date.end_date,
                creation_date=datetime.now()
            )
            db.add(db_hidden_date)
            db.commit()
            db.refresh(db_hidden_date)
            return {"item_id":db_hidden_date.id}
        except Exception as e:
            db.rollback()
            raise e


    # Get all hidden dates for a hotel
    @staticmethod
    async def get_all_hidden_dates(db: Session, hotel_id: int):
        booking_datas=db.query(DeactivateHotel).filter(DeactivateHotel.hotel_id == hotel_id).all()


        return [{"start_date":booking_data.start_date,"end_date":booking_data.end_date} for booking_data in booking_datas]

    # Delete a hidden date
    @staticmethod
    async def delete_hidden_date(db: Session, hotel_id: int, item_id: int):
        hidden_date = db.query(DeactivateHotel).filter(DeactivateHotel.id == item_id, DeactivateHotel.hotel_id == hotel_id).first()
        if hidden_date:
            db.delete(hidden_date)
            db.commit()
            return True
        return False
    @staticmethod
    async def check_hotel_access(db:Session,hotel_id:int):
        
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        return hotel
    
    @staticmethod
    async def create_owner_booking(db: Session, hotel_id: int,booking_data: dict):
        try:
            hotel = await HotelRepository.check_hotel_access(db, hotel_id)
            if hotel is None:
                raise ValueError("Hotel not found.")
            
            available_rooms = hotel.rooms_available  # Assuming you have a `rooms_available` field
            if booking_data.num_guests > available_rooms:
                raise ValueError("num_guests is higher than actual available rooms")
            new_booking = Booking(
                hotel_id=hotel_id,
                num_guests=booking_data.num_guests,
                start_date=booking_data.start_date,
                end_date=booking_data.end_date,
                customer_name=booking_data.customer_name,  # Assuming there’s a customer_name field in Booking model
                phone_num=booking_data.phone_num  # Assuming you have a phone_num field in Booking model
                )
            db.add(new_booking)
            db.commit()
            db.refresh(new_booking)
            return {"item_id": new_booking.booking_id}
        except Exception as e:
            db.rollback()
            raise e
    @staticmethod
    async def get_bookings_by_hotel(db: Session, hotel_id: int):
        # Query to get all bookings for the specified hotel_id
        bookings = db.query(Booking).filter(Booking.hotel_id == hotel_id).all()

        booking_list = [
        {key: value for key, value in booking.__dict__.items() if not key.startswith('_')}
        for booking in bookings
    ]
        # If no bookings are found, return an empty list
        return booking_list    
    @staticmethod
    async def delete_booking(db: Session, hotel_id: int, item_id: int):
        try:
            # Try to find the booking by hotel_id and item_id (booking_id)
            booking = db.query(Booking).filter(Booking.hotel_id == hotel_id, Booking.booking_id == item_id).first()

            # If the booking doesn't exist, raise a 404 error
            if not booking:
                return False

            # Delete the booking from the database
            db.delete(booking)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e