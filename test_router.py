from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from utils import create_access_token



client = TestClient(app)

generate_otp_url = "/generate_otp"
VALIDATE_OTP_URL = "/validate_otp"
RETRY_OTP_LIMIT = 3

class DummyOTPStore:
    def __init__(self):
        self.store = {}

    def set(self, key, value, ttl):
        self.store[key] = value

    def get(self, key):
        return self.store.get(key)

    def delete(self, key):
        self.store.pop(key, None)



@patch("utils.verify_otp")
@patch("utils.generate_otp_message")
def test_owner_flow(mock_generate_otp_message,mock_verify_otp):
    # health check 
    mock_verify_otp.side_effect = lambda phone,otp: phone == "8075652837" and otp == "123456"
    mock_generate_otp_message.side_effect = lambda phone: phone == "8075652837"
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "running"

    # generate otp fail cases
    response = client.post(generate_otp_url,json={"phone_num":"1231313123132131334234"})
    assert response.status_code==422
    response = client.post(generate_otp_url,json={"phone_num":"23423423"})
    assert response.status_code==422
    response = client.post(generate_otp_url,json={"phone_num":"123456789a"})
    assert response.status_code==422

    # regenerate otp time gap

    #generate otp success
    response = client.post(generate_otp_url,json={"phone_num":"8075652837"})
    assert response.status_code==200

    # validate otp wrong otp failed
    response = client.post(VALIDATE_OTP_URL,json={"phone_num":"8075652837","otp":123})
    assert response.status_code==422

    # validat otp too many attempts
    # response = client.post(VALIDATE_OTP_URL,json={"phone_num":"8075652837"})
    # for i in range(4):
    #     response = client.post(VALIDATE_OTP_URL,json={"phone_num":"8075652837","otp":555555})
    # print(response.json())
    # assert response.status_code==429

    # validate otp success
    response = client.post(VALIDATE_OTP_URL,json={"phone_num":"8075652837","otp":123456})
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # get booking details of a date: wrong format, wrong data type,
    response = client.get("/hotels/bookings/12313",headers=headers)
    assert response.status_code == 422



    # get booking details of a date: success
    response = client.get("/hotels/bookings/2025-06-05",headers=headers)
    print(response.json())
    assert response.status_code == 200 
    assert len(response.json()) == 4

    # get full list of bookings in a year : failed to wrong format
    response = client.get("/hotels/calender/20213",headers=headers)
    assert response.status_code == 422

    # get full list of bookings in a year : successful format 
    response = client.get("/hotels/calender/2025",headers=headers)
    assert response.status_code == 200  


    # create new owner booking
    response = client.post("/hotels/owner_bookings",headers=headers,json={"start_date":"2028-04-01","end_date":"2028-04-10","phone_num":"8075652837","name":"ram","num_guests":2})
    assert response.status_code == 200
    item_id = response.json()["item_id"]

    # list owner bookings
    response = client.get("/hotels/owner_bookings",headers=headers)
    assert response.status_code == 200
    assert len(response.json())==4

    # delete owner booking
    response = client.delete(f"/hotels/owner_bookings/{item_id}",headers=headers)
    assert response.status_code == 200
    

    # hide hotel add a new entry
    response = client.post("/hotels/hidden_dates",json={"start_date":"2028-05-02","end_date":"2028-05-03"},headers=headers)
    assert response.status_code == 200
    item_id_one = response.json()["item_id"]
    response = client.post("/hotels/hidden_dates",json={"start_date":"2028-05-21","end_date":"2028-05-25"},headers=headers)
    assert response.status_code == 200
    item_id_two = response.json()["item_id"]

    # TODO: test duplicate hidden entry, test date conflict with booking

    # get list of hotel bookings
    response = client.get("/hotels/hidden_dates/",headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # hide hotel delete an entry
    response = client.delete(f"/hotels/hidden_dates/{item_id_one}",headers=headers)
    assert response.status_code == 200
    response = client.delete(f"/hotels/hidden_dates/{item_id_two}",headers=headers)
    assert response.status_code == 200
    response = client.get("/hotels/hidden_dates/",headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 0

    # get monthly report 



# customer view single hotel
# saved
# past orders
# profile editing
# recommended hotels
#  