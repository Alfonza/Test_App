from sqlalchemy.orm import Session
from sqlmodel import SQLModel
import sys
import os
from faker import Faker
import random
import json

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from db_models import City, College,Hotel,Customer,Booking,OwnerBooking,DeactivationDate,SavedHotels
from db_connect import engine,create_db_and_tables       # Your SQLAlchemy engine

fake = Faker()

SQLModel.metadata.drop_all(engine)
create_db_and_tables()
with open("fake_data.json",'r')  as json_file:
    fake_data=json.load(json_file)

with Session(engine) as session:
    # Clean the tables

    # session.query(SavedHotels).delete()
    # session.query(DeactivationDate).delete()
    # session.query(Booking).delete()
    # session.query(OwnerBooking).delete()
    # session.query(Hotel).delete()
    # session.query(College).delete()
    # session.query(City).delete()
    # session.query(Customer).delete()
    # session.commit()

    # Insert Cities
    cities= fake_data["cities"]
    cities = [City(**city_dict) for city_dict in cities]

    session.add_all(cities)
    session.commit()  # Commit to assign IDs

    # Insert Colleges using city IDs
    colleges = fake_data["colleges"]
    colleges = [College(**college_dict) for college_dict in colleges] 

    session.add_all(colleges)
    session.commit()
    all_hotels= [Hotel(**hotel_json) for hotel_json in fake_data["hotels"]]
    session.add_all(all_hotels)
    session.commit()

    first_hotel = all_hotels[0]
    owner_booked_first = OwnerBooking(hotel_id=first_hotel.id,start_date="2025-06-05",end_date="2025-06-08",phone_num="1112223334",name="raju",num_guests=2)
    owner_booked_second= OwnerBooking(hotel_id=first_hotel.id,start_date="2025-06-05",end_date="2025-06-08",phone_num="1112223334",name="raju",num_guests=2)
    owner_booked_third= OwnerBooking(hotel_id=first_hotel.id,start_date="2025-06-05",end_date="2025-06-08",phone_num="1112223334",name="raju",num_guests=2)
    session.add_all([owner_booked_first,owner_booked_second,owner_booked_third])
    session.commit()

    customer_one = Customer(id=1,name="rajeev",phone_num="8889991110",gender="m",email_id="abc@gmail.com")
    session.add_all([customer_one])
    session.commit()

    customer_booked_first = Booking(hotel_id=first_hotel.id,customer_id=customer_one.id,num_guests=2,start_date="2025-06-05",end_date="2025-6-09",booked_date="2025-05-25",payment_mode="cash",payment_amount=1000)
    session.add_all([customer_booked_first])
    session.commit()

    saved_hotels=[]
    for i in range(3):
        saved_hotels.append(SavedHotels(customer_id=customer_one.id,hotel_id=all_hotels[i].id))

    session.add_all(saved_hotels)
    session.commit()




