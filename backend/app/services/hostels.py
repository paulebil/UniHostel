from fastapi import HTTPException, status, UploadFile
from fastapi.responses import JSONResponse

from backend.app.models.hostels import Hostel
from backend.app.models.users import User,UserRole
from backend.app.repository.hostels import HostelRepository
from backend.app.schemas.hostels import *
from backend.app.responses.hostels import *

from backend.app.core.config import get_settings
from uuid import uuid4
from backend.app.utils.s3minio.minio_client import upload_image_file_to_minio, generate_presigned_url
from backend.app.models.images import ImageMetaData
from backend.app.repository.images import ImageMetaDataRepository

settings = get_settings()


class HostelService:
    def __init__(self, hostel_repository: HostelRepository, image_repository: ImageMetaDataRepository):
        self.hostel_repository = hostel_repository
        self.image_repository = image_repository

# working +
    async def create_hostel(self, images: List[UploadFile], data: HostelCreateSchema, current_user: User):
        # check if user is a hostel owner
        # Authorization check
        if not current_user.role == UserRole.HOSTEL_OWNER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not authorized to create a room")


        # check if Hostel with this name exists
        hostel_exists = self.hostel_repository.get_hostel_by_name(data.name)
        if hostel_exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A hostel with this name already exist.")
        # create hostel
        hostel = Hostel(
            name=data.name,
            description=data.description,
            location=data.location,
            average_price=data.average_price,
            user_id=current_user.id,
            available_rooms=data.available_rooms,
            rules_and_regulations=data.rules_and_regulations,
            amenities=data.amenities,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        hostel = self.hostel_repository.create_hostel(hostel)


        bucket_name = settings.MINIO_IMAGE_BUCKET_NAME
        uploaded = []
        if not images:
            raise HTTPException(status_code=400, detail="No files uploaded.")

        for file in images:
            object_name = f"H{hostel.id}/{uuid4().hex}_{file.filename}"

            meta = await upload_image_file_to_minio(bucket_name, object_name, file)

            image = ImageMetaData(
                file_name=meta["file_name"],
                bucket_name=meta["bucket_name"],
                object_name=meta["object_name"],
                etag=meta["etag"],
                version_id=meta.get("version_id"),
                hostel_id=hostel.id
            )

            self.image_repository.create_image_metadata(image)

            uploaded.append({
                "id": image.id,
                "file_name": image.file_name
            })

        image_count = len(uploaded)

        return JSONResponse(content= {"message": "Upload successful","files": image_count},
                            status_code=status.HTTP_200_OK)

    async def update_hostel(self, data: HostelUpdateSchema, current_user: User):
        # check if user is a hostel owner
        if not current_user.hostel_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User is not authorized to update a hostel.")

        # get the hostel by owner id
        hostel = self.hostel_repository.get_hostel_by_owner_id(current_user.id)

        if not hostel:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,  detail="Hostel by this owner does not exists.")

        # Update hostel
        if data.name:
            hostel.name = data.name
        if data.location:
            hostel.location = data.location
        if data.amenities:
            hostel.amenities = data.amenities
        if data.available_rooms is not None:  # Check if available_rooms is explicitly set
            hostel.available_rooms = data.available_rooms
        if data.average_price:
            hostel.average_price = data.average_price
        if data.description:
            hostel.description = data.description
        if data.image_url:
            hostel.image_url = data.image_url

        self.hostel_repository.update_hostel(hostel)

        return HostelResponse(
            id=hostel.id,
            name=hostel.name,
            image_url=hostel.image_url,
            description=hostel.description,
            location=hostel.location,
            average_price=hostel.average_price,
            available_rooms=hostel.available_rooms,
            amenities=hostel.amenities,
            rules_and_regulations=hostel.get_rules(),
            created_at=hostel.created_at,
            updated_at=hostel.updated_at,
        )

    async def delete_hostel(self, hostel_id: int, current_user: User):
        # check if user is a hostel owner
        if not current_user.hostel_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User is not authorized to delete a hostel.")
        # get the hostels by owner id
        hostel = self.hostel_repository.get_hostel_by_owner_id(current_user.id)
        if not hostel:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,  detail="Hostel by this owner does not exists.")

        hostel_to_delete = self.hostel_repository.get_hostel_by_id(hostel_id)
        if not hostel_to_delete:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hostel does not exists")

        self.hostel_repository.delete_hostel(hostel_to_delete)

        return JSONResponse("Hostel deleted successfully.")

# working +
    async def get_all_my_hostels(self, current_user: User) -> HostelListResponse:

        # Authorization check
        if not current_user.role == UserRole.HOSTEL_OWNER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not authorized to create a room")

        # get the hostels by owner id
        hostels = self.hostel_repository.get_all_hostels_by_one_owner(current_user.id)
        if not hostels:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,  detail="Hostel by this owner does not exists.")

        hostel_list = []

        for hostel in hostels:
            # Get all this room image metadata from images table
            images = self.image_repository.get_image_metadata_by_hostel_id(hostel.id)
            # if not images:
            #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel has no images")

            image_urls = []

            # Get presigned_url for all the images
            for image in images:
                url = generate_presigned_url(image.bucket_name, image.object_name)
                image_urls.append({"url": url})

            hostel_response = HostelResponse(
                id=hostel.id,
                name=hostel.name,
                image_url=image_urls,
                description=hostel.description,
                location=hostel.location,
                owner_id=hostel.user_id,
                average_price=hostel.average_price,
                available_rooms=hostel.available_rooms,
                amenities=hostel.amenities,
                rules_and_regulations=hostel.get_rules(),
                created_at=hostel.created_at,
                updated_at=hostel.updated_at,
            )

            hostel_list.append(hostel_response)

        # Return a single HostelListResponse with the list of HostelResponse
        return HostelListResponse(hostels=hostel_list)

# working +
    async def get_all_hostels(self) -> HostelListResponse:


        hostels =  self.hostel_repository.get_all_hostels()

        hostel_list = []

        for hostel in hostels:
            # Get all this room image metadata from images table
            images = self.image_repository.get_image_metadata_by_hostel_id(hostel.id)
            # if not images:
            #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel has no images")

            image_urls = []

            # Get presigned_url for all the images
            for image in images:
                url = generate_presigned_url(image.bucket_name, image.object_name)
                image_urls.append({"url": url})

            hostel_response = HostelResponse(
                id=hostel.id,
                name=hostel.name,
                image_url=image_urls,
                description=hostel.description,
                location=hostel.location,
                owner_id=hostel.user_id,
                average_price=hostel.average_price,
                available_rooms=hostel.available_rooms,
                amenities=hostel.amenities,
                rules_and_regulations=hostel.get_rules(),
                created_at=hostel.created_at,
                updated_at=hostel.updated_at,
            )

            hostel_list.append(hostel_response)

        # Return a single HostelListResponse with the list of HostelResponse
        return HostelListResponse(hostels=hostel_list)

    async def search_hostels(self, search_data: HostelSearchSchema) -> HostelSearchResponse:
        results = self.hostel_repository.search_hostels(search_data.query)
        if not results:
            raise HTTPException(status_code=400, detail="No hostels found for this query")

        hostels_data = [
            HostelResponse(
                id=hostel_data["hostel"].id,  #  Extract the actual Hostel object
                name=hostel_data["hostel"].name,
                image_url=hostel_data["hostel"].image_url,
                description=hostel_data["highlighted_description"],  #  Use highlighted description
                location=hostel_data["hostel"].location,
                owner_id=hostel_data["hostel"].owner_id,
                average_price=hostel_data["hostel"].average_price,
                available_rooms=hostel_data["hostel"].available_rooms,
                amenities=hostel_data["hostel"].amenities,
                rules_and_regulations=hostel_data["hostel"].get_rules(),
                created_at=hostel_data["hostel"].created_at,
                updated_at=hostel_data["hostel"].updated_at
            ) for hostel_data in results  #  correctly iterating over dicts
        ]

        #  TODO: ADD PAGINATION
        return HostelSearchResponse(results=hostels_data)

# working +
    async def get_hostel_detail(self, hostel_id: int, current_user: User):
        # Authorization check
        if not current_user.role == UserRole.HOSTEL_OWNER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not authorized to create a room")

        # Fetch the hostel details by hostel_id
        hostel = self.hostel_repository.get_hostel_by_id(hostel_id)
        if not hostel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel not found.")

        # Ensure the user is the owner of the hostel
        if hostel.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this hostel.")

        # Get all this room image metadata from images table
        images = self.image_repository.get_image_metadata_by_hostel_id(hostel.id)
        if not images:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel has no images")

        image_urls = []

        # Get presigned_url for all the images
        for image in images:
            url = generate_presigned_url(image.bucket_name, image.object_name)
            image_urls.append({"url": url})

        # Return the hostel details in the response
        return HostelResponse(
            id=hostel.id,
            name=hostel.name,
            image_url=image_urls,
            description=hostel.description,
            location=hostel.location,
            owner_id=hostel.user_id,
            average_price=hostel.average_price,
            available_rooms=hostel.available_rooms,
            amenities=hostel.amenities,
            rules_and_regulations=hostel.get_rules(),
            created_at=hostel.created_at,
            updated_at=hostel.updated_at,
        )

# working +
    async def get_hostel_detail_user(self, hostel_id: int):

        # Fetch the hostel details by hostel_id
        hostel = self.hostel_repository.get_hostel_by_id(hostel_id)
        if not hostel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel not found.")

        # Get all this hostel image metadata from images table
        images = self.image_repository.get_image_metadata_by_hostel_id(hostel.id)
        if not images:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel has no images")

        image_urls = []

        # Get presigned_url for all the images
        for image in images:
            url = generate_presigned_url(image.bucket_name, image.object_name)
            image_urls.append({"url": url})

        # Return the hostel details in the response
        return HostelResponse(
            id=hostel.id,
            name=hostel.name,
            image_url=image_urls,
            description=hostel.description,
            location=hostel.location,
            owner_id=hostel.user_id,
            average_price=hostel.average_price,
            available_rooms=hostel.available_rooms,
            amenities=hostel.amenities,
            rules_and_regulations=hostel.get_rules(),
            created_at=hostel.created_at,
            updated_at=hostel.updated_at,
        )

