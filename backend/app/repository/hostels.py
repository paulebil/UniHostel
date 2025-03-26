from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from typing import List, Dict
import logging

from backend.app.models.hostels import Hostel

logger = logging.getLogger(__name__)


class HostelRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_hostel(self, hostel: Hostel):
        """
        Creates a new hostel in the database.

        Args:
            hostel (Hostel): The hostel object to create.

        Raises:
            IntegrityError: If there is a violation of database constraints.
        """
        try:
            self.session.add(hostel)
            self.session.commit()
            self.session.refresh(hostel)
            logger.info(f"Hostel created successfully: {hostel.name}")
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Failed to create hostel: {str(e)}")
            raise

    def update_hostel(self, hostel: Hostel):
        """
        Updates an existing hostel in the database.

        Args:
            hostel (Hostel): The hostel object to update.

        Raises:
            IntegrityError: If there is a violation of database constraints.
        """
        try:
            self.session.merge(hostel)
            self.session.commit()
            self.session.refresh(hostel)
            logger.info(f"Hostel updated successfully: {hostel.name}")
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Failed to update hostel: {str(e)}")
            raise

    def delete_hostel(self, hostel: Hostel):
        """
        Deletes a hostel from the database (soft deletion).

        Args:
            hostel (Hostel): The hostel object to delete.
        """
        hostel.deleted_at = func.now()  # Soft delete
        self.session.commit()
        logger.info(f"Hostel marked as deleted: {hostel.name}")

    def get_all_hostels(self, page: int = 1, per_page: int = 10):
        """
        Retrieves all hostels with pagination.

        Args:
            page (int): The page number (default: 1).
            per_page (int): The number of items per page (default: 10).

        Returns:
            List[Hostel]: A list of hostel objects.
        """
        return self.session.query(Hostel).offset((page - 1) * per_page).limit(per_page).all()

    def get_hostel_by_name(self, name: str) -> Hostel:
        """
        Retrieves a hostel by its name.

        Args:
            name (str): The name of the hostel.

        Returns:
            Hostel: The hostel object if found, otherwise None.
        """
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")
        return self.session.query(Hostel).filter(Hostel.name == name).first()

    def get_hostel_by_owner_id(self, owner_id: int):
        """
        Retrieves the first hostel owned by a specific owner.

        Args:
            owner_id (int): The ID of the owner.

        Returns:
            Hostel: The hostel object if found, otherwise None.
        """
        if not isinstance(owner_id, int):
            raise ValueError("Owner ID must be an integer")
        return self.session.query(Hostel).filter(Hostel.owner_id == owner_id).first()

    def get_all_hostels_by_one_owner(self, owner_id: int, page: int = 1, per_page: int = 10):
        """
        Retrieves all hostels owned by a specific owner with pagination.

        Args:
            owner_id (int): The ID of the owner.
            page (int): The page number (default: 1).
            per_page (int): The number of items per page (default: 10).

        Returns:
            List[Hostel]: A list of hostel objects.
        """
        if not isinstance(owner_id, int):
            raise ValueError("Owner ID must be an integer")
        return self.session.query(Hostel).filter(Hostel.owner_id == owner_id).offset((page - 1) * per_page).limit(per_page).all()

    def get_hostel_by_id(self, hostel_id: int) -> Hostel:
        """
        Retrieves a hostel by its ID.

        Args:
            hostel_id (int): The ID of the hostel.

        Returns:
            Hostel: The hostel object if found, otherwise None.
        """
        if not isinstance(hostel_id, int):
            raise ValueError("Hostel ID must be an integer")
        return self.session.query(Hostel).filter(Hostel.id == hostel_id).first()

    def search_hostels(self, query) -> List[Dict]:
        """
        Searches for hostels using full-text search with highlighted descriptions.

        Args:
            query (str): The search query.

        Returns:
            List[Dict]: A list of dictionaries containing hostel objects and highlighted descriptions.
        """

        ts_query = func.plainto_tsquery("english", query)  # Converts input into a tsquery

        results = (
            self.session.query(
                Hostel,
                func.coalesce(
                    func.ts_headline("english", Hostel.description, ts_query, 'StartSel=<b>,StopSel=</b>'),
                    Hostel.description  # Fallback to original description
                ).label("highlighted_description")
            ).filter(
                Hostel.search_vector.op("@@")(ts_query)
            ).order_by(
                func.ts_rank_cd(Hostel.search_vector, ts_query).desc()
            ).all()
        )

        return [{"hostel": hostel, "highlighted_description": highlight} for hostel, highlight in results]