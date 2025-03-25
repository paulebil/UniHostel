from fastapi import FastAPI
from backend.app.routes.users import user_router, auth_router, guest_router, admin_router
from backend.app.routes.hostels import hostel_router


def create_application():
    application = FastAPI()
    application.include_router(user_router)
    application.include_router(guest_router)
    application.include_router(auth_router)
    application.include_router(admin_router)

    application.include_router(hostel_router)
    return application

app = create_application()

@app.get("/")
def index():
    return {"message": "UniHostel is up and running."}