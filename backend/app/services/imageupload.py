from fastapi import UploadFile, HTTPException
from backend.app.models.images import ImageMetaData
from backend.app.repository.images import ImageMetaDataRepository
from typing import List
from uuid import uuid4
from backend.app.utils.s3minio.minio_client import upload_image_file_to_minio
from backend.app.core.config import get_settings

settings = get_settings()


class ImageMetaDataService:
    def __init__(self, image_repo: ImageMetaDataRepository):
        self.image_repository = image_repo

    async def upload_image_to_minio(self, files: List[UploadFile], draft_id: str):

        bucket_name = settings.MINIO_IMAGE_BUCKET_NAME
        uploaded = []
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded.")

        if not draft_id.strip():
            raise HTTPException(status_code=400, detail="Missing draft ID.")
        for file in files:
            object_name = f"{draft_id}/{uuid4().hex}_{file.filename}"

            meta = await upload_image_file_to_minio(bucket_name, object_name, file)

            image = ImageMetaData(
                file_name=meta["file_name"],
                bucket_name=meta["bucket_name"],
                object_name=meta["object_name"],
                etag=meta["etag"],
                version_id=meta.get("version_id"),
                draft_id=draft_id  # ← stored for later association
            )

            self.image_repository.create_image_metadata(image)

            uploaded.append({
                "id": image.id,
                "file_name": image.file_name
            })

        image_count = len(uploaded)
        return {
            "message": "Upload successful",
            "files": image_count
        }
