
from utils import create_access_token
from .common_components import client



token = create_access_token({"user_type":"customer","customer_id":1})

headers = {
    "Authorization": f"Bearer {token}"
}

def test_get_city_list(client):

    response = client.get("/customer/colleges",headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 10

def test_query_search(client):
    response = client.get("/customer/colleges",headers=headers)
    assert response.status_code == 200
    rows= response.json()
    college_id = rows[0]["college_id"]

    params = {
        "start_date":"2025-05-10",
        "end_date":"2025-05-25",
        "num_guests":1
    }

    response = client.get(f"/customer/colleges/{college_id}/hotels",params=params,headers=headers)
    assert response.status_code == 200
    assert len(response.json()) ==  3


def test_list_saved_hotels(client):
    response = client.get("/customer/save",headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_recommended(client):
    response = client.get("/customer/recommended",headers = headers)
    assert response.status_code == 200
    assert len(response.json()) != 0

def test_get_booking(client):
    response = client.get("/customer/booking",headers= headers)
    assert response.status_code == 200
    assert len(response.json()) ==1

def test_create_new_save(client):
    response = client.get("/customer/save",headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 3

    response = client.post("/customer/save",headers=headers,json={"customer_id":1,"hotel_id":1})
    assert response.status_code == 200
    assert "item_id" in response.json()
    item_id = response.json()["item_id"]

    response = client.delete(f"/customer/save/{item_id}",headers=headers)
    assert response.status_code == 200

    response = client.get("/customer/save",headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_past_orders(client):
    response = client.post("/customer/bookings",headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_customer_profile(client):
    response = client.get("/customer/profile",headers=headers)
    assert response.status_code == 200
    keys = response.json().keys()
    assert set(["name","phone_num","email_id","gender"]) == set(keys)

def test_update_customer_profile_success(client):
    params={
        "name":"def",
        "gender":"m",
        "phone_num":"8075652837"
    }
    response = client.put("/customer/profile",headers=headers,json=params)

    assert response.status_code == 200

    response = client.get("/customer/profile",headers=headers)
    assert response.status_code == 200
    response_json=response.json()
    del response_json["email_id"]
    assert response_json == params


def test_update_customer_profile_failed(client):

    params={}
    response = client.put("/customer/profile",headers=headers,params=params)
    assert response.status_code == 422

    params={
        "name":"",
    }
    response = client.put("/customer/profile",headers=headers,params=params)
    assert response.status_code == 422

    params={
        "gender":"a",
    }
    response = client.put("/customer/profile",headers=headers,params=params)
    assert response.status_code == 422

    params={
        "phone_num":"805652837"
    }
    response = client.put("/customer/profile",headers=headers,params=params)
    assert response.status_code == 422

    params={
        "abc":"def"
    }
    response = client.put("/customer/profile",headers=headers,params=params)
    assert response.status_code == 422