from pydantic import BaseModel, StringConstraints,Field,conint
from typing import Annotated,Union
from datetime import date

class OTPRequest(BaseModel):
    phone_num: Annotated[str,Field(pattern=r"^\d{10}$")]

class postOwnerBookingRequest(BaseModel):
    start_date: str
    end_date: str
    phone_num : str
    customer_name: str
    num_guests: int

class saveHotelRequest(BaseModel):
    hotel_id: int

class ValidateOTPRequest(BaseModel):

    phone_num: Annotated[str,Field(pattern=r"^\d{10}$")]
    otp: Annotated[int, Field(ge=100000, le=999999)]

class bookingsByDateResponse(BaseModel):
    start_date: date
    end_date:date
    num_guests:int
    customer_phone_num:str
    customer_name:str
    booking_id:int

class bookingCountByYearResponse(BaseModel):
    date: date
    booking_count : int
    
class getHiddenDatesResponse(BaseModel):
    item_id: int
    start_date: date
    end_date: date

class getCityListResponse(BaseModel):
    city_name:str
    college_name:str
    college_id:int
    city_id : int

class querySearchRequest(BaseModel):
    start_date:date
    end_date:date
    num_guests:int
    offset:int=0
    limit:int=10
    sort_by:Union[str,None]=None
    pricing_range_start:int=0
    pricing_range_end:int=1000000
    show_only_available:bool=False
    show_only_refundable:bool=False
    facilities:list[str]=[]

class pastBookingResponse(BaseModel):
    booking_id:int
    start_date:date
    end_date:date
    num_guests : int
    payment_mode: str
    payment_id : str
    booking_date: date

    hotel_id: int 
    hotel_name: str
    num_images:int
    place:str
    city:str
    rating:float
    distance_from_college:float
    facilities:list[str]=["ac","refrigerator","balcony"]
    description:str
    per_day_price: int
    refundable_before_day: int
    is_available:bool=True
    is_saved:bool

class verifyBookingRequest(BaseModel):
    token:str
    transaction_id:str

class postBookingRequest(BaseModel):
    start_date:date
    end_date:date
    num_guests:int
    hotel_id:int
    
class querySearchResponse(BaseModel):
    hotel_id: int = Field(alias="id")
    name: str
    num_images:int
    place:str
    city:str
    college_id: int 
    rating:float
    distance_from_college:float
    facilities:list[str]=["ac","refrigerator","balcony"]
    description:str
    per_day_price: int
    refundable_before_day: int
    is_available:bool=True
    is_saved:bool

class getCustomerBookingResponse(BaseModel):
    order_id: int = Field(alias = "id")
    start_date : date
    end_date : date
    num_guests : int
    booked_date : date
    payment_mode : str
    payment_amount : int
class postSaveRequest(BaseModel):
    hotel_id:int

class postSaveResponse(BaseModel):
    item_id:int

class DeactivateHotels(BaseModel):
    start_date:date
    end_date:date

class getOwnerBookingResponse(BaseModel):
    item_id: int
    start_date: date 
    end_date: date 
    phone_num: str 
    name: str 
    num_guests: int 

class OwnerBookingToCustomer(BaseModel):
    start_date:date
    end_date:date
    phone_num: str 
    name: str
    num_guests: int

