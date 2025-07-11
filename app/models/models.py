from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from pydantic import BaseModel,validator
from typing import List, Optional,Any
from datetime import date

class BookingBase(BaseModel):
    num_guests: int
    start_date: date
    end_date: date

class BookingCreate(BookingBase):
    customer_id: int

# class BookingResponse(BookingBase):
#     booking_id: int
#     hotel_id: int

#     class Config:
#         orm_mode = True
class ResponseBody(BookingBase):
    status_code: Any
    data: Any

    # class Config:
    #     orm_mode = True

class HotelBase(BaseModel):
    hotel_name: str

class HotelCreate(HotelBase):
    owner_id: int
class HiddenDateBase(BaseModel):
    start_date: date
    end_date: date
class BookingRequest(BaseModel):
    start_date: str  # iso-date-format
    end_date: str    # iso-date-format
    phone_num: str   # 10 digit phone number
    name: str        # Customer name
    num_guests: int  # Number of guests

class OTPRequest(BaseModel):
    phone_num: constr(regex=r'^\d{10}$')  # Only 10 digits allowed

    @validator('phone_num')
    def validate_phone_number(cls, v):
        # Check if the phone number is exactly 10 digits (done by constr already)
        if v == "0000000000":
            raise ValueError(status_code=403, detail="Phone number is invalid (e.g., '0000000000').")
        return v
    

# class HotelResponse(HotelBase):
#     id: int

#     class Config:
#         orm_mode = True


class Hotel(Base):
    __tablename__ = 'hotel'
    id = Column(Integer, primary_key=True, index=True)
    hotel_name = Column(String, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey('owner.id'))

    owner = relationship("Owner", back_populates="hotels")
    bookings = relationship("Booking", back_populates="hotel")


class Owner(Base):
    __tablename__ = 'owner'
    id = Column(Integer, primary_key=True, index=True)
    owner_phone_num = Column(Integer, unique=True, index=True)
    owner_name = Column(String)

    hotels = relationship("Hotel", back_populates="owner")


class Booking(Base):
    __tablename__ = 'bookings'
    booking_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    hotel_id = Column(Integer, ForeignKey('hotel.id'))
    num_guests = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)

    customer = relationship("Customer", back_populates="bookings")
    hotel = relationship("Hotel", back_populates="bookings")

class DeactivateHotel(Base):
    __tablename__ = 'deactivate_hotel'
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey('hotel.id'))
    start_date = Column(Date)
    end_date = Column(Date)
    creation_date = Column(Date)

    hotel = relationship("Hotel", back_populates="bookings")


class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone_num = Column(Integer, unique=True, index=True)

    bookings = relationship("Booking", back_populates="customer")
