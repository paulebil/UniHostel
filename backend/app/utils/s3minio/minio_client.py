from minio import Minio
from backend.app.core.config import get_settings
import io

settings = get_settings()

client = Minio(settings.MINIO_ENDPOINT,
               settings.MINIO_ROOT_USER,
               settings.MINIO_ROOT_PASSWORD,
               secure=False)

def ensure_bucket_exists(bucket_name: str):
    if not  client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Created bucket: {bucket_name}")

def get_presigned_url(bucket_name: str, object_name: str, expires):

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

def stream_file_to_minio(bucket_name: str, object_name: str, file_name: str):

    ensure_bucket_exists(bucket_name)

    result = client.put_object(bucket_name, object_name, io.FileIO(file_name), -1, part_size=1024*1024*5)

    print(f"File '{object_name}' streamed as '{file_name}' to bucket '{bucket_name}' ")
    return result
