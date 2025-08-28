import traceback

from layernext.datalake.constants import MULTI_PART_UPLOAD_CHUNK_SIZE

import requests


class StorageInterface:

    def __init__(self, storage_type, url_list):
        self.e_tag = ""
        # Create client based on storage type
        if storage_type == "aws_s3":
            from layernext.datalake.aws_s3_client import AWSS3Client

            self.storage_client = AWSS3Client()
        elif storage_type == "gcs":
            from layernext.datalake.gcs_client import GCSClient

            self.storage_client = GCSClient()
        elif storage_type == "azure_blob":
            from layernext.datalake.azure_client import AzureClient

            self.storage_client = AzureClient(url_list)
        else:
            raise Exception("Invalid storage type: " + storage_type)

    """'
    Upload file to the storage bucket (common code for AWS/Google/Azure)
    """

    def upload_to_storage(
        self,
        url,
        path,
        content_type,
        chunk_id,
        file_size,
        start_byte=0,
        read_bytes=MULTI_PART_UPLOAD_CHUNK_SIZE,
    ):
        try:
            with open(path, "rb") as object_file:
                # Read chunk of file from start_byte
                object_file.seek(start_byte)
                file_data = object_file.read(read_bytes)
                # print('Uploading ' + str(read_bytes) + ' bytes from ' + str(start_byte))
                content_range = (
                    f"bytes {start_byte}-{start_byte+read_bytes-1}/{file_size}"
                )
                # url, chunk_id, chunk_data, content_type, content_range, read_bytes
                return self.storage_client.upload_chunk(
                    url, chunk_id, file_data, content_type, content_range, read_bytes
                )

        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error occurred in upload")
            return {"isSuccess": False}
        # Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error occurred in upload")
            return {"isSuccess": False}
        # Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error occurred in upload")
            return {"isSuccess": False}
        # Handle other errors
        except requests.exceptions.RequestException as e:
            print("An exception occurred in upload")
            traceback.print_exc()
            return {"isSuccess": False}

        except Exception as e1:
            print("An exception occurred in upload")
            traceback.print_exc()
            return {"isSuccess": False}
