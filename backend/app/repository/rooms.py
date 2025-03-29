from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


from backend.app.models.hostels import Room

class RoomsRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_room(self, room: Room):
        try:
            self.session.add(room)
            self.session.commit()
            self.session.refresh(room)
        except IntegrityError:
            self.session.rollback()
            raise

    def update_room(self, room: Room):
        try:
            self.session.merge(room)
            self.session.commit()
            self.session.refresh(room)
        except IntegrityError:
            self.session.rollback()
            raise

    def delete_room(self, room: Room):
        self.session.delete(room)
        self.session.commit()

    def get_all_rooms_by_hostel_id(self, hostel_id: int):
       return self.session.query(Room).filter(Room.hostel_id == hostel_id).all()

    def get_room_by_room_number(self, room_number: str):
        return self.session.query(Room).filter(Room.room_number == room_number).first()

    def get_room_by_room_number_and_hostel_id(self, room_number:str, hostel_id:int):
        return self.session.query(Room).filter(
            Room.hostel_id == hostel_id,
            Room.room_number == room_number
        ).first()

    def get_room_occupancy_count(self, room_id: int):

        room = self.session.query(Room).filter(Room.id == room_id).first()

        # Fetch the first result from the query (or None if not found)
        if room:
            return room.occupancy
        else:
            return None

    def get_room_capacity_count(self, room_id: int):

        room = self.session.query(Room).filter(Room.id == room_id).first()
        if room:
            return room.capacity
        else:
            return None

    def increment_room_occupancy(self, room_id: int):
        # Fetch the room
        room = self.session.query(Room).filter(Room.id == room_id).first()

        if room:
            room.occupancy += 1  # Increment occupancy
            self.session.commit()
            self.session.refresh(room)

    def get_room_by_id(self, room_id: int):

        # Fetch the room
        return self.session.query(Room).filter(Room.id == room_id).first()
