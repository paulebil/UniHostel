from backend.app.models.users import HostelOwner
from backend.app.repository.custodian import HostelOwnerRepository
from backend.app.repository.users import UserRepository
from backend.app.schemas.custodian import *
from backend.app.responses.custodian import *

from fastapi import HTTPException


class HostelOwnerService:
    def __init__(self, hostel_owner_repository: HostelOwnerRepository, user_repository: UserRepository):
        self.hostel_owner_repository = hostel_owner_repository
        self.user_repository = user_repository

    async def create_hostel_owner(self, data: HostelOwnerCreate) -> HostelOwnerResponse:
        owner_exists = self.hostel_owner_repository.get_hostel_owner_by_user_email(data.email)
        if owner_exists:
            raise HTTPException(status_code=400, detail="Email already exists.")
        owner_mobile = self.hostel_owner_repository.get_hostel_owner_by_mobile(data.mobile)
        if owner_mobile:
            raise HTTPException(status_code=400, detail="Mobile number already exists")

        owner = HostelOwner(
            business_name=data.business_name
        )

        self.hostel_owner_repository.create_hostel_owner(owner)

        corresponding_user = self.user_repository.get_user_by_email(data.email)

        hostel_owner_response = HostelOwnerResponse(
            id=corresponding_user.id,
            email=corresponding_user.email,
            mobile=corresponding_user.mobile,
            name=corresponding_user.name,
            business_name=owner.business_name,
            is_active=corresponding_user.is_active,
            verified_at=corresponding_user.verified_at,
            updated_at=corresponding_user.updated_at
        )

        return hostel_owner_response

    async def update_hostel_owner(self, data: HostelOwnerUpdate) -> HostelOwnerResponse:
        # Retrieve the user
        user = self.user_repository.get_user_by_email(data.email)
        if not user:
            raise HTTPException(status_code=400, detail="User with this email does not exists.")

        # Retrieve the owner  linked to the user
        owner = self.hostel_owner_repository.get_hostel_owner_by_user_id(user.id)
        if not owner:
            raise HTTPException(status_code=400, detail="Hostel Owner record not found.")

        # Ensure the provided mobile number matches the user
        if user.mobile != data.mobile:
            raise HTTPException(status_code=400, detail="Mobile number does not match the user record.")

        # Update owner details
        owner.business_name = data.business_name

        # Save the updated hostel owner record
        self.hostel_owner_repository.update_hostel_owner(owner)

        # Refresh user details after update
        user = self.user_repository.get_user_by_email(data.email)

        # Return updated response
        return HostelOwnerResponse(
            id=user.id,
            email=user.email,
            mobile=user.mobile,
            name=user.name,
            business_name=owner.business_name,
            is_active=user.is_active,
            verified_at=user.verified_at,
            updated_at=user.updated_at
        )

    async def delete_hostel_owner(self, email: str):
        # Retrieve the user by email
        user = self.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=400, detail="Hostel owner detail with this email not found.")

        # Retrieve the hostel owner record linked to this user
        owner = self.hostel_owner_repository.get_hostel_owner_by_user_id(user.id)
        if not owner:
            raise HTTPException(status_code=400, detail="Hostel owner information with this email not found.")

        # Delete the student record
        self.hostel_owner_repository.delete_hostel_owner(owner)

        return {"message": "Hostel owner record deleted successfully."}

    async def get_hostel_owner_information(self ,email: str) -> HostelOwnerResponse:
        user_info = self.user_repository.get_user_by_email(email)
        if not user_info:
            raise HTTPException(status_code=400, detail="User Info with this email not found.")

        owner_info = self.hostel_owner_repository.get_hostel_owner_by_user_id(user_info.id)
        if not owner_info:
            raise HTTPException(status_code=400, detail="Hostel Info with this email not found.")

        return HostelOwnerResponse(
            id=user_info.id,
            email=user_info.email,
            mobile=user_info.mobile,
            name=user_info.name,
            business_name=owner_info.business_name,
            is_active=user_info.is_active,
            verified_at=user_info.verified_at,
            updated_at=user_info.updated_at
        )
