import calendar
from typing import Dict
from fastapi import APIRouter,Depends,HTTPException
from datetime import datetime,date, timedelta

from sqlalchemy import func, select
from db_connect import SessionDep
from db_models import Booking,DeactivationDate, Hotel,OwnerBooking
from pydantic_models import DeactivateHotels,OwnerBookingToCustomer,postOwnerBookingRequest,bookingsByDateResponse,bookingCountByYearResponse,getHiddenDatesResponse
from utils import decode_jwt,convert_to_date_obj

hotel_router = APIRouter(
    prefix="/hotels"
)

@hotel_router.get("/bookings/{date_val}") 
def get_bookings_by_date(date_val:date,session:SessionDep,user_details=Depends(decode_jwt)) -> list[bookingsByDateResponse]:
    hotel_id = user_details["hotel_id"]
    customer_bookings = Booking.filter_by_date(session,hotel_id,date_val)

    owner_bookings = OwnerBooking.filter_by_date(session,hotel_id,date_val)

    for booking in owner_bookings:
        booking = booking.dict()
        booking["customer_phone_num"] = booking["phone_num"]
        booking["customer_name"] = booking["name"]
        booking["booking_id"] = booking["item_id"]
        customer_bookings.append(booking)
    return customer_bookings

@hotel_router.get("/calender/{year}")
def get_bookings_in_a_year(year:int,session:SessionDep,user_details=Depends(decode_jwt)) -> list[bookingCountByYearResponse] :
    hotel_id = user_details["hotel_id"]
    try:
        start_date = datetime(year=year,month=1,day=1)
        end_date = datetime(year=year,month=12,day=31)
    except:
        raise HTTPException(422,detail="invalid year")
    booking_counts = Booking.get_bookings_count_between_dates(session,hotel_id,start_date,end_date)

    booking_data = [{"date":row.start_date,"booking_count":row.booking_count} for row in booking_counts]
    return booking_data


@hotel_router.post("/hidden_dates")
def hide_hotels_in_specific_date(request:DeactivateHotels,session:SessionDep,user_details=Depends(decode_jwt)):

    # TODO: 
        # 409: cannot create row due to booking conflict. booking conflict means there is already bookings occured during specified dates
        # 409: duplicate entry

    hotel_id= user_details["hotel_id"]
    row = DeactivationDate.insert_row(session,hotel_id=hotel_id,start_date=request.start_date,end_date=request.end_date)
    return {"item_id":row.item_id}

@hotel_router.get("/hidden_dates")
def get_hidden_dates(session:SessionDep,user_details=Depends(decode_jwt))->list[getHiddenDatesResponse]:
    hotel_id = user_details["hotel_id"]
    date = datetime.now()
    rows = DeactivationDate.get_all_rows_after_date(session,hotel_id,date)
    return rows

@hotel_router.delete('/hidden_dates/{item_id}')
def delete_hidden_entry(item_id,session:SessionDep,user_details=Depends(decode_jwt)):
    hotel_id = user_details["hotel_id"]
    DeactivationDate.delete_hidden_entry(session,hotel_id,item_id)

@hotel_router.post('/owner_bookings')
def owner_booking_to_customer(request:OwnerBookingToCustomer,session:SessionDep,user_details=Depends(decode_jwt)):
    start_date=request.start_date
    end_date=request.end_date
    phone_num=request.phone_num
    name=request.name
    num_guests=request.num_guests
    hotel_id = user_details["hotel_id"]
    row = OwnerBooking.insert_row(session,start_date,end_date,phone_num,name,num_guests,hotel_id)
    return {"item_id":row.item_id}

@hotel_router.get('/owner_bookings')
def getting_all_owner_booking(session:SessionDep,user_details=Depends(decode_jwt)):
    hotel_id = user_details["hotel_id"]
    rows = OwnerBooking.get_all_rows(session,hotel_id)
    return rows

@hotel_router.post("/owner_bookings")
def post_owner_bookings(request:postOwnerBookingRequest,session:SessionDep,user_details = Depends(decode_jwt)):
    start_date = convert_to_date_obj(request.start_date)
    end_date = convert_to_date_obj(request.end_date)
    phone_num = request.phone_num
    customer_name = request.customer_name
    num_guests = request.num_guests
    hotel_id = user_details["hotel_id"]
    row=OwnerBooking.insert_row(session,start_date,end_date,phone_num,customer_name,num_guests,hotel_id)

    # TODO:
        # 409: num_guests is higher than actual available free rooms

    return {"item_id":row.item_id}

@hotel_router.delete('/owner_bookings/{item_id}')
def delete_owner_bookings(item_id:int,session:SessionDep,user_details=Depends(decode_jwt)):
    hotel_id = user_details["hotel_id"]
    OwnerBooking.delete_row(session,hotel_id,item_id)
    
@hotel_router.get("/monthly_report/{year_month}")
def get_monthly_booking_report(year_month: str, session: SessionDep, user_details=Depends(decode_jwt)) -> dict:
    hotel_id = user_details["hotel_id"]
    try:

        year, month = map(int, year_month.split("-"))
        start_date = datetime(year=year, month=month, day=1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year=year, month=month, day=last_day)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM")

    customer_bookings = Booking.filter_between_dates(session, hotel_id, start_date, end_date)
    owner_bookings = OwnerBooking.filter_between_dates(session, hotel_id, start_date, end_date)

    total_bookings = len(customer_bookings) + len(owner_bookings)

    # Get hotel info to compute earnings
    hotel = session.get(Hotel, hotel_id)
    total_earnings = total_bookings * hotel.per_day_price if hotel else 0

    return {
        "month": f"{year}-{month:02d}",
        "total_bookings": total_bookings,
        "total_earnings": total_earnings
    }


