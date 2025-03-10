from fastapi import FastAPI


app = FastAPI()

@app.get("/")
def index():
    return {"message": "UniHostel is up and running."}