from pydantic import BaseModel, HttpUrl

class Images(BaseModel):
    images: HttpUrl
