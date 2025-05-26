from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


from backend.app.models.images import ImageMetaData

class ImageMetaDataRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_image_metadata(self, image:ImageMetaData):
        try:
            self.session.add(image)
            self.session.commit()
            self.session.refresh(image)
        except IntegrityError:
            self.session.rollback()
            raise

    def update_image_metadata(self, image: ImageMetaData):
        try:
            self.session.merge(image)
            self.session.commit()
            self.session.refresh(image)
        except IntegrityError:
            self.session.rollback()
            raise

    def delete_image_metadata(self, image: ImageMetaData):
        self.session.delete(image)
        self.session.commit()


    def get_image_metadata_by_room_id(self, room_id: int):
        return self.session.query(ImageMetaData).filter(ImageMetaData.room_id == room_id).all()

    def get_image_metadata_by_hostel_id(self, hostel_id: int):
        return self.session.query(ImageMetaData).filter(ImageMetaData.hostel_id == hostel_id).all()