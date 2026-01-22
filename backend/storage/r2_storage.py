import boto3
import os
import json
import tempfile
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

class R2Storage:
    def __init__(self):
        self.account_id = os.getenv("CF_ACCOUNT_ID")
        self.access_key = os.getenv("CF_ACCESS_KEY")
        self.secret_key = os.getenv("CF_SECRET_ACCESS_KEY")
        self.bucket_name = os.getenv("BUCKET_NAME")
        self.public_url = os.getenv("PUB_DEV_URL")

        # Initialize the S3 client for Cloudflare R2
        self.s3_client = boto3.client(
            's3',
            endpoint_url = os.getenv("S3_API"),
            aws_access_key_id = self.access_key,
            aws_secret_access_key = self.secret_key,
            region_name = 'auto'
        )
    
    def upload_file(self, file_path, object_key=None):
        """Upload a file to the R2 bucket

        :param file_path: File to upload
        :param object_key: S3 object name. If not specified then file_path is used
        :return: True if file was uploaded, else False
        """
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, object_key)
            return True
        except ClientError as e:
            print(f"Error uploading file: {e}")
            return False
    
    def upload_file_obj(self, file_obj, object_key):
        """
        Upload a file object to R2

        :param file_obj: File-like object to upload
        :param object_key: S3 object name
        :return: True if upload was successful, False otherwise
        """
        try:
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, object_key)
            return True
        except ClientError as e:
            print(f"Error uploading file object: {e}")
            return False
    
    def download_file(self, object_key, local_path):
        """Download a file from the R2 bucket

        :param object_key: S3 object name to download
        :param local_path: Local path to save the downloaded file
        :return: True if file was downloaded, else False
        """
        try:
            self.s3_client.download_file(self.bucket_name, object_key, local_path)
            return True
        except ClientError as e:
            print(f"Error downloading file: {e}")
            return False
    
    def download_to_temp(self, object_key, suffix=""):
        """ 
        Download file to temporary location and return path.

        :param object_key: S3 object name to download
        :param suffix: Suffix for the temporary file
        :return: Path to the temporary file if successful, None otherwise
        """
        try:
            temp_file = tempfile.NamedTemporaryFile(delete = False, suffix = suffix)
            self.s3_client.download_fileobj(self.bucket_name, object_key, temp_file)
            temp_file.close()
            return temp_file.name
        except ClientError as e:
            print(f"Error downloading file to temp: {e}")
            return None
    
    def upload_json(self, data, object_key):
        """
        Upload JSON data to R2

        :param data: Data to upload (will be converted to JSON)
        :param object_key: S3 object name
        :return: True if upload was successful, False otherwise
        """
        try:
            json_str = json.dumps(data, indent = 2)
            self.s3_client.put_object(
                Bucket = self.bucket_name,
                Key = object_key, Body = json_str.encode('utf-8'),
                ContentType = 'application/json'
            )
            return True
        except ClientError as e:
            print(f"Error uploading JSON data: {e}")
            return False
    
    def download_json(self, object_key):
        """
        Download JSON data from R2

        :param object_key: S3 object name
        :return: Parsed JSON data if successful, None otherwise
        """
        try:
            response = self.s3_client.get_object(Bucket = self.bucket_name, Key = object_key)
            data = response['Body'].read().decode('utf-8')
            return json.loads(data)
        except ClientError as e:
            print(f"Error downloading JSON data: {e}")
            return None
    
    def file_exists(self, object_key):
        """
        Check if a file exists in R2

        :param object_key: S3 object name
        :return: True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket = self.bucket_name, Key = object_key)
            return True
        except ClientError as e:
            print(f"Error checking file existence: {e}")
            return False
    
    def delete_file(self, object_key):
        """
        Delete a file from R2

        :param object_key: S3 object name
        :return: True if file was deleted, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket = self.bucket_name, Key = object_key)
            return True
        except ClientError as e:
            print(f"Error deleting file: {e}")
            return False
    
    def delete_folder(self, prefix):
        """
        Delete all files with a give prefix (folder) from R2

        :param prefix: Prefix of the folder to delete
        :return: True if folder was deleted, False otherwise
        """
        try:
            # Get all objects with the given prefix
            objects = self.s3_client.list_objects_v2(Bucket = self.bucket_name, Prefix = prefix)

            if 'Contents' not in objects:
                return True
            
            # Delete all objects
            delete_keys = [{'Key': obj['Key']} for obj in objects['Contents']]
            self.s3_client.delete_objects(
                Bucket = self.bucket_name,
                Delete = {'Objects': delete_keys}
            )
            return True
        except ClientError as e:
            print(f"Error deleting folder: {e}")
            return False
    
    def list_files(self, prefix=""):
        """
        List all files in R2 with a given prefix

        :param prefix: Prefix to filter files
        :return: List of file keys
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket = self.bucket_name, Prefix = prefix)

            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents']]
        except ClientError as e:
            print(f"Error listing files: {e}")
            return []
    
    def get_public_url(self, object_key):
        """
        Get the public URL for a file in R2

        :param object_key: S3 object name
        :return: Public URL of the file
        """
        return f"{self.public_url}/{object_key}"
    

# Singleton instance
r2_storage = R2Storage()
