from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.models.hostels import Hostel


class HostelRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_hostel(self, data):
        pass
