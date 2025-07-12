from fastapi import APIRouter,Depends
import string
from utils import decode_jwt
import random
from db_connect import SessionDep
from pydantic_models import postSaveRequest,postSaveResponse,getCityListResponse,querySearchRequest,querySearchResponse,postBookingRequest,verifyBookingRequest,getCustomerProfileResponse,putCustomerProfileRequest
from db_models import College,Hotel,SavedHotels,Booking,Customer
customer_router=APIRouter(prefix="/customer")

@customer_router.get("/colleges")
def get_colleges_by_city(session:SessionDep) -> list[getCityListResponse]:
    college_list = College.get_all_list(session)
    return college_list

@customer_router.get("/profile")
def get_customer_profile(session:SessionDep,user_details=Depends(decode_jwt)) -> getCustomerProfileResponse:
    customer_id = user_details["customer_id"]
    result =  Customer.read_row(session,customer_id)
    return result

@customer_router.put("/profile")
def put_customer_profile(session:SessionDep,request:putCustomerProfileRequest,user_details=Depends(decode_jwt)):
    customer_id = user_details["customer_id"]
    return Customer.update_row(session,customer_id,request.model_dump())

@customer_router.get("/colleges/{college_id}/hotels")
def search_for_hotels(
    college_id:int,
    session:SessionDep,
    query_params:querySearchRequest=Depends(),
    user_details=Depends(decode_jwt)
) -> list[querySearchResponse]:

    customer_id = user_details["customer_id"]

    rows = Hotel.query_hotel(
            session,
            college_id,
            query_params.start_date,
            query_params.end_date,
            query_params.num_guests,
            query_params.pricing_range_start,
            query_params.pricing_range_end,
            query_params.facilities,
            query_params.show_only_available,
            query_params.show_only_refundable,
            query_params.offset,
            query_params.limit,
            query_params.sort_by,
            customer_id
        )

    return rows


@customer_router.get("/save")
def get_save(
        session:SessionDep,
        user_details=Depends(decode_jwt)
    ) -> list[querySearchResponse]:
    customer_id = user_details["customer_id"]
    rows = SavedHotels.get_hotel_items(session,customer_id)
    return rows

@customer_router.post("/save")
def post_save(
    request:postSaveRequest,
    session:SessionDep,
    user_details=Depends(decode_jwt)
) -> postSaveResponse:

    customer_id = user_details["customer_id"]
    hotel_id = request.hotel_id

    row = SavedHotels.insert_row(session,customer_id,hotel_id)
    return {"item_id":row.id}


@customer_router.delete("/save/{item_id}")
def delete_save(
    item_id:int,
    session:SessionDep,
    user_details=Depends(decode_jwt)
):
    SavedHotels.delete_row(session,item_id)

@customer_router.get("/recommended")
def get_recommended_hotels(session:SessionDep,user_details=Depends(decode_jwt)) -> list[querySearchResponse]:
    customer_id = user_details["customer_id"]
    result = Hotel.query_recommended(session,customer_id,offset=0,limit=5)
    return result

data_store ={}
@customer_router.post("/initiate_booking")
def post_booking(request:postBookingRequest,session:SessionDep,user_details=Depends(decode_jwt)):
    # TODO : verify availability
    # TODO : store booking data in temperory
    # TODO : generate token and send back
    token_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    data_store[token_str] = request.dict()
    return {"token":token_str}


@customer_router.post("/booking_confirm")
def verify_booking(request:verifyBookingRequest,session:SessionDep,user_details=Depends(decode_jwt)):
    booking_data= data_store[request.token]

    return {"booking_id":1}

@customer_router.get("/booking")
def get_bookings(session:SessionDep,user_details=Depends(decode_jwt)):
    customer_id = user_details["customer_id"]
    return Booking.filter_by_customer_id(session,customer_id)


    