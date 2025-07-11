from fastapi import FastAPI
from controller import hotel_controller
from database import engine
from database import Base

# Initialize FastAPI app
app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers (controllers)
app.include_router(hotel_controller.router)
