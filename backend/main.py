from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes.users import user_router, auth_router, guest_router, admin_router
from backend.app.routes.hostels import hostel_router, hostel_user_router
from backend.app.routes.rooms import room_router, room_user_router
from backend.app.routes.booking import booking_user_router, booking_router
from backend.app.routes.image_upload import image_router


def create_application():
    application = FastAPI()
    # Users
    application.include_router(user_router)
    application.include_router(guest_router)
    application.include_router(auth_router)
    application.include_router(admin_router)

    # Hostels
    application.include_router(hostel_router)
    application.include_router(hostel_user_router)

    # Rooms
    application.include_router(room_router)
    application.include_router(room_user_router)

    # Booking
    application.include_router(booking_user_router)
    application.include_router(booking_router)

    application.include_router(image_router)

    return application

app = create_application()

origins = [
    "http://localhost:3000",  # or your frontend's actual origin
    # "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],                # <-- VERY IMPORTANT
    allow_headers=["*"],                # <-- VERY IMPORTANT
)

@app.get("/")
def index():
    return {"message": "UniHostel is up and running."}