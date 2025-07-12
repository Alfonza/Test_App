
from faker import Faker
import random
import json

fake = Faker()

def get_fake_hotel(hotel_id):
    data={}
    data["name"]=fake.company()
    data["id"]=hotel_id
    data["college_id"]=random.randint(1,4)
    data["num_images"]=random.randint(1,5)
    data["max_guests"]=random.randint(1, 5)
    data["per_day_price"]=random.randint(500, 3000)
    data["city"]=random.randint(1,4)
    data["description"]=fake.paragraph()
    data["place"]=fake.street_name()
    data["rating"]=round(random.uniform(2.5, 5.0), 1)
    data["distance_from_college"]=round(random.uniform(0.5, 10.0), 2)
    data["refundable_before_day"]=random.randint(1, 7)
    data["owner_phone_num"]=fake.unique.msisdn()[3:13]  # 10 digit Indian numbe
    return data

def get_fake_city(city_id):
    data={}
    data["id"]=city_id
    data["name"]=fake.city()
    data["latitude"] = str(fake.latitude())
    data["longitude"] = str(fake.longitude())
    return data

def get_fake_college(college_id,college_name,city_id):
    data = {}
    data["id"]=college_id
    data["name"]=college_name
    data["latitude"] = str(fake.latitude())
    data["longitude"] = str(fake.longitude())
    data["city_id"] = city_id
    return data


if __name__ == "__main__":
    all_data={
        "hotels":[],
        "cities":[],
        "colleges":[]
    }
    num_cities=4
    for i in range(1,num_cities):
        all_data["cities"].append(get_fake_city(i))

    prefixes = ["University of", "College of", "Institute of", "Academy of", "School of"]
    fields = ["Technology", "Science", "Arts", "Business", "Engineering", "Medicine", "Management"]

    for i in range(1,11):
        field = random.choice(fields)
        prefix = random.choice(prefixes)
        college_name = f"{prefix} {field}"
        city_id = i%(num_cities-1)+1
        print(city_id)
        all_data["colleges"].append(get_fake_college(i,college_name,city_id))
    


    for i in range(1,11):
        all_data["hotels"].append(get_fake_hotel(i))
    all_data["hotels"][0]["owner_phone_num"] = "8075652837"



    with open("fake_data.json","w") as json_file:
        json.dump(all_data,json_file)