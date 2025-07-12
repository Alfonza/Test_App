from typing import Optional, List
from datetime import date, datetime
from fastapi import HTTPException
from sqlmodel import Field, SQLModel, Relationship, CheckConstraint,select
from sqlalchemy import func,exists
class SavedHotels(SQLModel,table=True):
    __tablename__= "saved_hotel"
    id: Optional[int] = Field(default=None,primary_key=True)
    customer_id: int  = Field(foreign_key="customer.id")
    hotel_id: Optional[int] = Field(foreign_key="hotel.id")

    customer: List["Customer"] = Relationship(back_populates="saved_hotel")
    hotel: List["Hotel"] = Relationship(back_populates="saved_hotel")

    @classmethod
    def get_hotel_items(cls,session,customer_id):

        statement = (
            select(
                *Hotel.__table__.c,
                exists().where((SavedHotels.hotel_id == cls.id) & (SavedHotels.customer_id == customer_id)).label("is_saved")
            ).join(cls, cls.hotel_id == Hotel.id).where(cls.customer_id == customer_id)
        )


        results = session.exec(statement).all()
        return results

    @classmethod
    def insert_row(cls,session,customer_id,hotel_id):
        row=cls(customer_id=customer_id,hotel_id=hotel_id)
        session.add(row)
        session.commit()
        session.refresh(row)
        return row
    
    @classmethod
    def delete_row(cls,session,item_id):
        obj = session.query(cls).filter(cls.id == item_id).first()
        if obj:
            session.delete(obj)
            session.commit()
        

class Hotel(SQLModel, table=True):
    __tablename__ = "hotel"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None, max_length=255)
    college_id: int = Field(foreign_key="college.id")
    num_images: int
    max_guests: int
    per_day_price: int
    city : str
    place : str
    rating : float
    description:str
    distance_from_college : float
    refundable_before_day: int 
    owner_phone_num: str = Field(sa_column_kwargs={"unique": True}, max_length=10)

    saved_hotel: List["SavedHotels"] = Relationship(back_populates="hotel")
    bookings: List["Booking"] = Relationship(back_populates="hotel")
    owner_bookings: List["OwnerBooking"] = Relationship(back_populates="hotel")
    deactivation_dates: List["DeactivationDate"] = Relationship(back_populates="hotel")

    @classmethod
    def filter_by_phone_num(cls,session,phone_num):
        result = session.exec(select(cls).where(cls.owner_phone_num == phone_num)).first()
        return result 

    @classmethod
    def is_id_exists(cls,session,hotel_id):
        result = session.exec(select(cls.id).where(cls.id == hotel_id)).first()
        return result is not None
    
    @classmethod
    def query_recommended(cls,session,customer_id,offset,limit):
        stmt = (
            select(
                *cls.__table__.c,
                exists().where((SavedHotels.hotel_id == cls.id) &  (SavedHotels.customer_id == customer_id)).label("is_saved")
            )
        )

        if limit is not None:
            stmt = stmt.limit(limit)

        results = session.exec(stmt).all()

        return results
    
    @classmethod
    def query_hotel(cls,session,college_id,start_date,end_date,num_guests,pricing_range_start,pricing_range_end,facilities,show_only_available,show_only_refundable,offset,limit,sort_by,customer_id):
        # TODO: update

        stmt = (
            select(
                *cls.__table__.c,
                exists().where((SavedHotels.hotel_id == cls.id) &  (SavedHotels.customer_id == customer_id)).label("is_saved")
            ).where(            
                cls.college_id == college_id,
                cls.per_day_price >= pricing_range_start,
                cls.per_day_price <= pricing_range_end
                )
        )

        if limit is not None:
            stmt = stmt.limit(limit)

        results = session.exec(stmt).all()

        return results
class Customer(SQLModel, table=True):
    __tablename__ = "customer"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None, max_length=255)
    phone_num: str = Field(sa_column_kwargs={"unique": True}, max_length=10, nullable=False)

    bookings: List["Booking"] = Relationship(back_populates="customer")

    saved_hotel: List["SavedHotels"] = Relationship(back_populates="customer")

class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    booking_id: Optional[int] = Field(default=None, primary_key=True)
    hotel_id: int = Field(foreign_key="hotel.id")
    customer_id: int = Field(foreign_key="customer.id")
    num_guests: int = Field(nullable=False)
    start_date: date = Field(nullable=False)
    end_date: date = Field(nullable=False)
    booked_date: date
    payment_mode : str
    payment_amount : int


    __table_args__ = (
        CheckConstraint("num_guests > 0", name="check_positive_guests"),
    )

    hotel: Optional["Hotel"] = Relationship(back_populates="bookings")
    customer: Optional["Customer"] = Relationship(back_populates="bookings")  

    @classmethod
    def filter_by_customer_id(cls,session,customer_id):

        statement = (
            select(cls,Hotel).join(Hotel,cls.hotel_id==Hotel.id).where(cls.customer_id==customer_id)
        )

        results = session.exec(statement).all()
        results = [row[0].model_dump() | row[1].model_dump() for row in results]
        
        return results

    @classmethod
    def filter_by_date(cls, session, hotel_id, target_date):
        statement = (
            select(cls,Customer).join(cls.customer)
        )
        results = session.exec(statement).all()
        return [
                {
                    "booking_id":booking.booking_id,
                    "customer_name": customer.name,
                    "customer_phone_num":customer.phone_num,
                    "num_guests":booking.num_guests,
                    "start_date":booking.start_date,
                    "end_date":booking.end_date
                }
                for booking,customer in results
            ]

    @classmethod
    def get_bookings_count_between_dates(cls, session, hotel_id, start_date, end_date):
        # TODO: handle overlapping
        return session.query(
            cls.start_date,
            func.count(cls.booking_id).label("booking_count")
        ).filter(
            cls.hotel_id == hotel_id,
            cls.start_date >= start_date,
            cls.start_date <= end_date
        ).group_by(cls.start_date).order_by(cls.start_date).all()
    
    @classmethod
    def filter_between_dates(cls, session, hotel_id, start_date, end_date):
      return session.query(cls).filter(
          cls.start_date <= end_date,
          cls.end_date >= start_date,
          cls.hotel_id == hotel_id
      ).all()

    @classmethod
    def get_per_day_price(cls, session, hotel_id: int) -> int:
      hotel = session.query(cls).filter(cls.hotel_id == hotel_id).first()
      if not hotel:
          raise HTTPException(status_code=404, detail="Hotel not found")
      return hotel.per_day_price
  

class OwnerBooking(SQLModel, table=True):
    __tablename__ = "owner_bookings"

    item_id: Optional[int] = Field(default=None, primary_key=True)
    hotel_id: int = Field(foreign_key="hotel.id")
    start_date: date = Field(nullable=False)
    end_date: date = Field(nullable=False)
    phone_num: str = Field(max_length=10, nullable=False)
    name: str = Field(max_length=255, nullable=False)
    num_guests: int = Field(nullable=False)
    

    __table_args__ = (
        CheckConstraint("num_guests > 0", name="check_owner_positive_guests"),
        CheckConstraint("end_date >= start_date", name="check_owner_date_range"),
        CheckConstraint("phone_num ~ '^\d{10}$'", name="check_owner_valid_phone"),
    )

    hotel: Optional[Hotel] = Relationship(back_populates="owner_bookings")

    @classmethod
    def filter_by_date(cls, session, hotel_id, target_date):
        return session.query(cls).filter(
            cls.start_date <= target_date,
            cls.end_date >= target_date,
            cls.hotel_id == hotel_id
        ).all()

    @classmethod
    def filter_between_dates(cls, session, hotel_id, start_date, end_date):
      return session.query(cls).filter(
          cls.start_date <= end_date,
          cls.end_date >= start_date,
          cls.hotel_id == hotel_id
      ).all()

    @classmethod
    def insert_row(cls,session,start_date,end_date,phone_num,name,num_guests,hotel_id):
        new_entry = cls(
            hotel_id=hotel_id,
            start_date=start_date,
            end_date=end_date,
            phone_num=phone_num,
            name=name,
            num_guests=num_guests
        )
        session.add(new_entry)
        session.commit()
        session.refresh(new_entry) 
        return new_entry

    @classmethod
    def get_all_rows(cls,session,hotel_id):
        return session.query(cls).filter(
            cls.hotel_id == hotel_id
        ).all()

    @classmethod
    def delete_row(cls,session,hotel_id,item_id):
        obj = session.query(cls).filter(cls.hotel_id == hotel_id,cls.item_id == item_id).first()
        if obj:
            session.delete(obj)
            session.commit()


class City(SQLModel,table=True):
    __tablename__ = "city"
    id:Optional[int]=Field(default=None,primary_key=True)
    name: str = Field(default=None,nullable=False)
    latitude: float = Field(nullable=True)
    longitude : float = Field(nullable=True)

class College(SQLModel,table=True):
    __tablename__ = "college"
    id:Optional[int]=Field(default=None,primary_key=True)
    name:str = Field(default =None,nullable=False) 
    latitude: float = Field(nullable=True)
    longitude : float = Field(nullable=True)
    city_id:int = Field(foreign_key="city.id")

    @classmethod
    def get_all_list(cls,session):
        statement = (
            select(cls,City).join(City,cls.city_id == City.id)
        )
        results = session.exec(statement).all()
        return [
                {
                    "college_id":college.id,
                    "college_name": college.name,
                    "city_name": city.name,
                    "city_id": city.id
                }
                for college,city in results
            ]
    


class DeactivationDate(SQLModel, table=True):
    __tablename__ = "deactivation_dates"

    item_id: Optional[int] = Field(default=None, primary_key=True)
    hotel_id: int = Field(foreign_key="hotel.id")
    start_date: date = Field(nullable=False)
    end_date: date = Field(nullable=False)

    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="check_deactivation_date_range"),
    )

    hotel: Optional[Hotel] = Relationship(back_populates="deactivation_dates")

    @classmethod
    def insert_row(cls,session,hotel_id,start_date,end_date):
        new_entry = cls(
            hotel_id=hotel_id,
            start_date=start_date,
            end_date=end_date
        )

        
        session.add(new_entry)
        session.commit()
        session.refresh(new_entry) 
        return new_entry   

    @classmethod
    def get_all_rows_after_date(cls,session,hotel_id,date_val):
        return session.query(cls).filter(
            cls.hotel_id == hotel_id,
            cls.end_date>=date_val
        ).all()

    @classmethod
    def delete_hidden_entry(cls,session,hotel_id,item_id):
        obj = session.query(cls).filter(cls.hotel_id == hotel_id,cls.item_id == item_id).first()
        if obj:
            session.delete(obj)
            session.commit()
            print(f"Deleted: {obj}")
        else:
            print("No matching entry found")





class OTPRequest(SQLModel, table=True):
    __tablename__ = "otp_requests"

    phone_num: str = Field(default=None, primary_key=True, max_length=10)
    otp: Optional[str] = Field(default=None, max_length=6)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    retry_count: int = Field(default=0)
    last_attempt_at: Optional[datetime] = None
    is_valid: bool = Field(default=False)

    __table_args__ = (
        CheckConstraint("phone_num ~ '^\d{10}$'", name="check_otp_phone"),
    )
