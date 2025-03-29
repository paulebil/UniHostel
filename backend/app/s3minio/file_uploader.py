from minio import Minio
from minio.error import S3Error

def main():
    MINIO_ROOT_PASSWORD = "unihostel@admin"
    MINIO_ENDPOINT = "minio-service:9000"  # Update if needed
    MINIO_ROOT_USER = "unihostel"

    client = Minio(
        MINIO_ENDPOINT,
        MINIO_ROOT_USER,
        MINIO_ROOT_PASSWORD,
        secure=False,
    )

    source_file = "../utils/test-file.txt"  # Ensure the correct path
    bucket_name = "python-test-bucket"
    destination_file = "my-test-file.txt"

    # Make the bucket if it doesn't exist
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")

    # Upload the file to MinIO
    client.fput_object(bucket_name, destination_file, source_file)
    print(source_file, "successfully uploaded as object", destination_file, "to bucket", bucket_name)

if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("Error occurred.", exc)
