
from fastapi.testclient import TestClient
import sys
print(sys.path)
from main import app
from utils import create_access_token
from db_connect import engine,get_session
from db_models import Customer,Hotel
from sqlalchemy.orm import Session
import pytest

@pytest.fixture()
def test_get_session():
    with Session(engine) as session:
        # Start a transaction
        connection = session.connection()
        trans = connection.begin()
        try:
            yield session
        finally:
            trans.rollback()

# app.dependency_overrides[get_session] = test_get_session

client = TestClient(app)

# test customer login 
token = create_access_token({"user_type":"customer","customer_id":1})

headers = {
    "Authorization": f"Bearer {token}"
}

def test_get_city_list():

    response = client.get("/customer/colleges",headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 10

def test_query_search():
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


def test_list_saved_hotels():
    response = client.get("/customer/save",headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_recommended():
    response = client.get("/customer/recommended",headers = headers)
    assert response.status_code == 200
    assert len(response.json()) != 0

def test_get_booking():
    response = client.get("/customer/booking",headers= headers)
    assert response.status_code == 200
    assert len(response.json()) ==1

def test_create_new_save():
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

def test_past_orders():
    response = client.post("/customer/bookings",headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

