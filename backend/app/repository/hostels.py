from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.models.hostels import Hostel



class HostelRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_hostel(self, hostel: Hostel):
        try:
            self.session.add(hostel)
            self.session.commit()
            self.session.refresh(hostel)
        except IntegrityError:
            self.session.rollback()
            raise


    def update_hostel(self, hostel: Hostel):
        try:
            self.session.merge(hostel)
            self.session.commit()
            self.session.refresh(hostel)
        except IntegrityError:
            self.session.rollback()
            raise

    def delete_hostel(self, hostel: Hostel):
        self.session.delete(hostel)
        self.session.commit()

    def get_all_hostels(self):
        return self.session.query(Hostel).all()

    def get_hostel_by_name(self, name: str) -> Hostel:
        return self.session.query(Hostel).filter(Hostel.name == name).first()

    def get_hostel_by_owner_id(self, id: int) -> Hostel:
        return self.session.query(Hostel).filter(Hostel.owner_id == id).first()
