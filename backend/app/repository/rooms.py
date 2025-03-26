from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


from backend.app.models.hostels import Rooms

class RoomsRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_room(self, room: Rooms):
        try:
            self.session.add(room)
            self.session.commit()
            self.session.refresh(room)
        except IntegrityError:
            self.session.rollback()
            raise

    def update_room(self, room: Rooms):
        try:
            self.session.merge(room)
            self.session.commit()
            self.session.refresh(room)
        except IntegrityError:
            self.session.rollback()
            raise

    def delete_room(self, room: Rooms):
        self.session.delete(room)
        self.session.commit()

    def get_all_rooms(self):
       return self.session.query(Rooms).all()

    def get_room_by_room_number(self, room_number: str):
        return self.session.query(Rooms).filter(Rooms.room_number == room_number).first()
