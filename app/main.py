from fastapi import FastAPI
from app.routes import router  # Import the router from routes.py

# Initialize the FastAPI app
app = FastAPI()

# Include the delivery router
app.include_router(router)
