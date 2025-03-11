from fastapi import FastAPI
from backend.app.routes.users import user_router



def create_application():
    application = FastAPI()
    application.include_router(user_router)
    return application

app = create_application()

@app.get("/")
def index():
    return {"message": "UniHostel is up and running."}