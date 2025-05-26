from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.app.repository.images import ImageMetaDataRepository
from backend.app.services.imageupload import ImageMetaDataService

from backend.app.database.database import get_session

image_router = APIRouter()


def get_image_metadata_service(session: Session = Depends(get_session)) -> ImageMetaDataService:
    image_metadata_repository = ImageMetaDataRepository(session)
    return ImageMetaDataService(image_metadata_repository)

@image_router.post("/api/upload")
async def upload_images(
    files: List[UploadFile] = File(...),
    draft_id: str = Form(...), image_service: ImageMetaDataService = Depends(get_image_metadata_service)):
    return await image_service.upload_image_to_minio(files, draft_id)