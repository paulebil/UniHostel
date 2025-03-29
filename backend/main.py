from fastapi import FastAPI
from backend.app.routes.users import user_router, auth_router, guest_router, admin_router
from backend.app.routes.hostels import hostel_router, hostel_user_router
from backend.app.routes.rooms import room_router, room_user_router
from backend.app.routes.booking import booking_user_router, booking_router


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

    return application

app = create_application()

@app.get("/")
def index():
    return {"message": "UniHostel is up and running."}