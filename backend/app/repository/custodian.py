from sqlalchemy.orm import Session
from backend.app.models.users import User, HostelOwner
from sqlalchemy.exc import IntegrityError


class HostelOwnerRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_hostel_owner(self, owner: HostelOwner) -> None:
        try:
            self.session.add(owner)
            self.session.commit()
            self.session.refresh(owner)
        except IntegrityError:
            self.session.rollback()
            raise

    def update_hostel_owner(self, owner: HostelOwner)-> None:
        try:
            self.session.merge(owner)
            self.session.commit()
            self.session.refresh(owner)
        except IntegrityError:
            self.session.rollback()
            raise

    def delete_hostel_owner(self, owner: HostelOwner) -> None:
        self.session.delete(owner)
        self.session.commit()

    def get_hostel_owner_by_user_id(self, user_id: int) -> HostelOwner:
        owner = self.session.query(HostelOwner).filter(HostelOwner.user_id == user_id).first()
        return owner

    def get_hostel_owner_by_user_email(self, email: str) -> HostelOwner:
        return self.session.query(HostelOwner).join(User).filter(User.email == email).first()

    def get_hostel_owner_by_mobile(self, mobile: int) -> HostelOwner:
        return self.session.query(HostelOwner).join(User).filter(User.mobile == mobile).first()

    def get_all_hostel_owners(self):
        return self.session.query(HostelOwner).all()

