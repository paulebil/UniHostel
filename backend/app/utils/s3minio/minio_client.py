from minio import Minio
from backend.app.core.config import get_settings
import io
from datetime import timedelta
from io import BytesIO

settings = get_settings()

client = Minio(settings.MINIO_ENDPOINT,
               settings.MINIO_ROOT_USER,
               settings.MINIO_ROOT_PASSWORD,
               secure=False)

def ensure_bucket_exists(bucket_name: str):
    if not  client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Created bucket: {bucket_name}")

def get_presigned_url(bucket_name: str, object_name: str, expires: timedelta(minutes=5)):

    """Generated a presigned URL valid for `expires` seconds ."""
    url = client.presigned_get_object(bucket_name, object_name, expires=expires)

    return url


def upload_file_to_minio(bucket_name: str,object_name: str, file_name: str, content_type: str):

    ensure_bucket_exists(bucket_name)

    result = client.fput_object(bucket_name, object_name, file_name, content_type)

    print(f"File '{file_name}' uploaded as '{object_name}' to bucket '{bucket_name}' ")

    return  result


def download_file_from_minio(bucket_name: str, object_name: str, file_name: str, version_id: str):

    ensure_bucket_exists(bucket_name)

    result = client.fget_object(bucket_name,object_name , file_name, version_id=version_id)

    print(f"File '{object_name}' downloaded as '{file_name}' from bucket '{bucket_name}' ")

    return result


from minio.error import S3Error
from io import BytesIO


def download_receipt_file_from_minio(bucket_name: str, object_name: str) -> dict:
    try:
        # Ensure the bucket exists
        ensure_bucket_exists(bucket_name)

        # Get the object as a stream
        response = client.get_object(bucket_name, object_name)

        # Read the data into memory
        file_data = BytesIO(response.read())

        # Return the file as a dictionary
        return {
            "file": file_data,
            "filename": object_name,  # Customize the filename if needed
            "mime_type": "application",  # Adjust if you know it's a PDF or other specific type
            "mime_subtype": "pdf"
        }

    except S3Error as e:
        # Handle MinIO-specific errors (e.g., NoSuchKey)
        print(f"MinIO Error: {e}")
        return {
            "error": True,
            "message": f"Error downloading file from MinIO: {e}"
        }

    except Exception as e:
        # Handle other generic errors (e.g., connection issues)
        print(f"Unexpected Error: {e}")
        return {
            "error": True,
            "message": f"Unexpected error occurred: {e}"
        }


def stream_file_to_minio(bucket_name: str, object_name: str, file_name: str):

    ensure_bucket_exists(bucket_name)

    result = client.put_object(bucket_name, object_name, io.FileIO(file_name), -1, part_size=1024*1024*5)

    print(f"File '{object_name}' streamed as '{file_name}' to bucket '{bucket_name}' ")
    return result
