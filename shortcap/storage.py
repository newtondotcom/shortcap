import logging
import os
import requests
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

logger = logging.getLogger("shortcap.storage")

class StorageError(Exception):
    """Custom exception class for handling errors during emojis operations"""
    pass

# Global variables to store the API key and the list of S3 configurations
API_KEY = os.environ.get("API_KEY")
API_URL = os.environ.get("API_URL")
s3s = []


def get_list():
    """Retrieve the list of S3 configurations from the external API."""
    global s3s
    headers = {"Authorization": "Bearer " + API_KEY}
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()  # Check if the request was successful
        s3s = response.json()
        print("S3 list updated")
    except requests.RequestException as e:
        logger.error(f"Error fetching S3 list: {str(e)}")
        raise StorageError(f"Error fetching S3 list: {str(e)}")

def get_s3(name: str) -> dict:
    """Retrieve the details of an S3 bucket by its name."""
    for s3 in s3s:
        if s3["name"] == name:
            return s3
    logger.error(f"S3 configuration for '{name}' not found")
    raise StorageError(f"S3 configuration for '{name}' not found")

# Initial call to retrieve the list of S3 configurations
get_list()

class S3:
    def __init__(self, s3name: str):
        bucket = get_s3(s3name)
        self.host = bucket["endpoint"].strip()
        self.port = bucket["port"]
        self.secure = bucket["ssl"]
        self.access_key = bucket["access_key"].strip()
        self.secret_key = bucket["secret_key"].strip()
        self.bucket_name = bucket["bucket"].strip()

        # Initialize Minio client
        self.client = Minio(
            self.host + ":" + str(self.port),
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
            region="us-east-1",
        )

    def check_file_exists(self, file_key: str) -> bool:
        """Check if a file exists in the S3 bucket."""
        try:
            self.client.stat_object(self.bucket_name, file_key)
            return True
        except S3Error as e:
            logger.error(f"Error checking if file exists: {str(e)}")
            return False

    def download_file(self, file_key: str, local_file_path: str):
        """Download a file from the S3 bucket."""
        try:
            # Ensure the local directory exists
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            # Download object to local file
            self.client.fget_object(self.bucket_name, file_key, local_file_path)
            print(f"File downloaded successfully to {local_file_path}")
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            raise StorageError(f"Error downloading file: {str(e)}")

    def upload_file(self, file_key: str) -> str:
        """Upload a file to the S3 bucket."""
        try:
            local_file_path = file_key
            # Upload local file to the bucket without storing in a temp folder
            # Remove the 'temp/' prefix from the file_key
            file_key = file_key.replace("temp/", "")
            # Upload local file to the bucket
            self.client.fput_object(self.bucket_name, file_key, local_file_path)
            file_url = f"{self.host}/{self.bucket_name}/{file_key}"
            print(f"File {file_key} uploaded successfully to S3")
            return file_url
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise StorageError(f"Error uploading file: {str(e)}")

    def remove_file(self, file_key: str):
        """Remove a file from the S3 bucket."""
        try:
            # Remove object from the bucket
            self.client.remove_object(self.bucket_name, file_key)
            print(f"File '{file_key}' deleted from bucket '{self.bucket_name}'")
        except S3Error as e:
            logger.error(f"An error occurred: {str(e)}")
            raise StorageError(f"An error occurred: {str(e)}")