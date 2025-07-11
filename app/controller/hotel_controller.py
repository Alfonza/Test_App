import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List 
from database import get_db
from models.models import BookingCreate,HiddenDateBase,ResponseBody,BookingRequest,OTPRequest
from repositories.hotel_repo import create_booking, get_booking_by_date, get_all_hidden_dates, create_hidden_date, delete_hidden_date
from jwt_auth import get_current_user

from app.repositories.hotel_repository import HotelRepository

router = APIRouter()

# Helper function to check if the hotel belongs to the current user
async def check_hotel_access(hotel_id: int, token: str, db: Session):
    hotel_data=await HotelRepository.check_hotel_access(db,hotel_id)
    if hotel_data is None:
        raise HTTPException(status_code=404, detail="Hotel not found")
    if hotel_data.owner_id != token:
        raise HTTPException(status_code=403, detail="Not authorized to access this hotel")
    return hotel_data

# Endpoint: Create Booking
@router.post("/hotels/{hotel_id}/bookings", response_model=ResponseBody)
async def create_booking_view(hotel_id: int, booking: BookingCreate, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    try:
        await check_hotel_access(hotel_id, token, db)
        ResponseBody.data = await HotelRepository.create_booking(db, booking)
        ResponseBody.status =200
        return ResponseBody
    except Exception as e:
        ResponseBody.status = 400
        ResponseBody.message = str(e)
        return ResponseBody


# Endpoint: Get Booking List for a Specific Date
@router.get("/hotels/{hotel_id}/bookings/{date}", response_model=ResponseBody)
async def get_bookings_for_date(hotel_id: int, date: str, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    try:
        await check_hotel_access(hotel_id, token, db)
        bookings= await HotelRepository.get_booking_by_date(db, hotel_id, date)

        if not bookings:
            return ResponseBody(status_code=404, data={"message": "No bookings found for this date"})
        return ResponseBody(status_code=200, data=bookings)
    except ValueError as e:
        # Catch any exception related to invalid date format or other validation
        raise HTTPException(status_code=400, detail="The given date is not valid or not in YYYY-MM-DD format.")
    except Exception as e:
        # Catch unexpected errors
        raise HTTPException(status_code=500, detail="Internal server error")


# Endpoint: Get Calendar for a Specific Year
@router.get("/hotels/{hotel_id}/calendar/{year}")
async def get_calendar(hotel_id: int, year: int, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    try:
        await check_hotel_access(hotel_id, token, db)
        booking_year=await HotelRepository.get_booking_by_year(db, year)
        # Implement logic to fetch the calendar for the specified year
        if not booking_year:
                return ResponseBody(status_code=404, data={"message": "No bookings found for this year"})

            # Return the bookings for the year as a dictionary with iso-date-format
        return ResponseBody(status_code=200, data=booking_year)

    except ValueError as e:
        # Catch any exception related to invalid year format
        raise HTTPException(status_code=400, data=str(e))
    except Exception as e:
        # Catch unexpected errors
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint: Deactivate Dates
@router.post("/hotels/{hotel_id}/hidden_dates", response_model=ResponseBody)
async def deactivate_dates(hotel_id: int, hidden_date: HiddenDateBase, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    try:
        await check_hotel_access(hotel_id, token, db)
        # Implement logic to check for booking conflicts
        entry_id = await HotelRepository.create_hidden_date(db, hotel_id, hidden_date)

        return ResponseBody(status_code=200, data=entry_id)
    except ValueError as e:
        # Catch any exception related to invalid date format or other validation
        if str(e).startswith("Invalid year format"):
            return ResponseBody(status_code=400, data=str(e))
        elif str(e).startswith("Booking conflict"):
            return ResponseBody(status_code=422, data=str(e))

    except Exception as e:
        # Catch unexpected errors
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint: Get All Hidden Dates
@router.get("/hotels/{hotel_id}/hidden_dates", response_model=ResponseBody)
async def get_hidden_dates(hotel_id: int, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    try:
        await check_hotel_access(hotel_id, token, db)
        hidden_dates = await HotelRepository.get_all_hidden_dates(db, hotel_id)
        if not hidden_dates:
            return ResponseBody(status_code=404, data=str(e))
        return ResponseBody(status_code=200, data=hidden_dates)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")



# Endpoint: Delete Hidden Date
@router.delete("/hotels/{hotel_id}/hidden_dates/{item_id}")
async def delete_hidden_date_view(hotel_id: int, item_id: int, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    try:
        await check_hotel_access(hotel_id, token, db)
        result = await HotelRepository.delete_hidden_date(db, hotel_id, item_id)
        if not result:
            raise ResponseBody(status_code=404, detail="Hidden date not found")
        return ResponseBody(satus_code=200,data="Hidden date deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.post("/hotels/{hotel_id}/owner_bookings", response_model=ResponseBody)
async def create_owner_booking(
    hotel_id: int, 
    booking: BookingRequest, 
    db: Session = Depends(get_db),
    token: str = Depends(get_current_user)
):
    try:
        await check_hotel_access(hotel_id,token,db)
        db_booking_id = await HotelRepository.create_owner_booking(db,hotel_id, booking)
        return ResponseBody(status_code=200, data=db_booking_id)
    except ValueError as e:
        if str(e).startswith("Invalid year format"):
            return ResponseBody(status_code=400, data='start_date and end date not in iso format. phone number is not exactly 10 digits. number of guests is 0 or -ve')
        elif str(e).startswith("num_guests is higher than actual available rooms"):
            return ResponseBody(status_code=422, data=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/hotels/{hotel_id}/owner_bookings", response_model=ResponseBody)
async def get_owner_bookings(hotel_id: int, db: Session = Depends(get_db),token:str=Depends(get_current_user)):
    try:
        await check_hotel_access(hotel_id, token, db) 
        # Call the repository to get the bookings for the specified hotel
        booking_list =await HotelRepository.get_bookings_by_hotel(db, hotel_id)
        
        # If no bookings are found, raise a 404 error
        if not booking_list:
            return ResponseBody(status_code=404, data="No bookings found for this hotel.")
        return ResponseBody(status_code=200, data=booking_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.delete("/hotels/{hotel_id}/owner_bookings/{item_id}")
async def delete_owner_booking(hotel_id: int, item_id: int, db: Session = Depends(get_db)):
    try:
        # Call the repository to delete the booking for the specified hotel_id and item_id
        data = await HotelRepository.delete_booking(db, hotel_id, item_id)
        if not data:
            return ResponseBody(status=404, data="value not found")
            
        return ResponseBody(status_code=200, data="Booking deleted successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    


@router.post("/generate_otp", response_model=ResponseBody)
def generate_otp_endpoint(request:OTPRequest, db: Session = Depends(get_db)):
    # Check if the phone number is valid
    if len(request.phone_num) != 10 or not request.phone_num.isdigit():
        return ResponseBody(status_code=400, detail="Phone number is not exactly 10 digits.")
    
    if not is_phone_number_valid(request.phone_num):
        return ResponseBody(status_code=403, detail="Phone number is valid but not allowed (e.g., '0000000000').")
    
    # Check for maximum retries (e.g., 3 attempts within 60 seconds)
    retry_data = track_otp_request(db, request.phone_num)
    if retry_data["exceeded"]:
        retry_time = retry_data["next_retry_in_seconds"]
        raise HTTPException(status_code=429, detail=f"Maximum retry limit exceeded. Please retry after {retry_time} seconds.")
    
    # Generate OTP
    try:
        otp = generate_otp(request.phone_num)
    except Exception:
        raise HTTPException(status_code=503, detail="OTP generation failed due to internal error.")
    
    # Return success message
    return {"message": "OTP generated successfully"}
    
    

