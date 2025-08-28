import requests
from layernext.datalake.storage_client import StorageClient
from azure.storage.blob import BlobClient
import base64


class AzureClient(StorageClient):
    def __init__(self, url_list) -> None:
        super().__init__()

        # create a blob client for the file, take first url out of list as all urls are same in azure
        first_url_obj = url_list[0]
        self.block_blob_client = BlobClient.from_blob_url(first_url_obj["signedUrl"])

    def upload_chunk(
        self, url, chunk_id, chunk_data, content_type, content_range, read_bytes
    ):

        # upload the block
        # block_id =f"{chunk_id:06d}"
        block_id = base64.b64encode(f"{chunk_id:06}".encode()).decode()

        try:
            self.block_blob_client.stage_block(block_id, chunk_data)
        except Exception as e:
            print("Exception in AzureClient during stage_block:", e)

        return {"isSuccess": True, "e_tag": "", "part_id": block_id}
