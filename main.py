from fastapi import FastAPI
# from middlewares import JWTAuthMiddleware
from pydantic_models import OTPRequest,ValidateOTPRequest
from fastapi import FastAPI, HTTPException
from pydantic import constr
from datetime import datetime
from utils import create_access_token
from hotels_router import hotel_router
from db_connect import create_db_and_tables,SessionDep
from customer_router import customer_router
from db_models import Hotel
app = FastAPI()

app.include_router(hotel_router)
app.include_router(customer_router)
create_db_and_tables()
# app.add_middleware(JWTAuthMiddleware)


@app.get("/health")
def get_health():
    return {"status":"running","version":"6.15"}


@app.post("/generate_otp")
def generate_otp(request: OTPRequest):
    phone = request.phone_num

    now = datetime.utcnow()

    # TODO : OTP sending
        # 503: OTP generation failed due to internal error
        # 429: maximum retry limit exceeded. please retry after [time_seconds] delay
        # 403: phone number is exactly 10 digits. but is not valid. Example: 0000000000
        # convert to async


    return {"detail": "OTP generated successfully"}

@app.post("/validate_otp")
def validate_otp(request:ValidateOTPRequest,session:SessionDep):

    row = Hotel.filter_by_phone_num(session,request.phone_num)

    if  row is None:
        raise HTTPException(403,"authentication failed")

    # TODO:
        # 503: OTP service down
        # 429: OTP verification limit exceeded specified threshold limits. cannot continue anymore
        # Convert to async
    
    token = create_access_token({"user_type":"owner","hotel_id":row.id})
    return {"access_token":token}

@app.post("/validate_customer")
def validate_customer():

    token = create_access_token({"user_type":"customer","customer_id":1})
    return {"access_token":token}