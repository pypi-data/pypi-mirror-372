import requests
from layernext.datalake.storage_client import StorageClient


class AWSS3Client(StorageClient):
    def upload_chunk(
        self, url, chunk_id, chunk_data, content_type, content_range, read_bytes
    ):

        headers = {"Content-Type": content_type}
        res = requests.put(url, data=chunk_data, headers=headers)
        if res.status_code != 200:
            print("Error in uploading file to S3: Status code: " + str(res.status_code))
            print(res.text)
            return {"isSuccess": False}

        if "ETag" not in res.headers:
            print("Error in uploading file to S3: ETag not found in response header")
            print(res.text)
            return {"isSuccess": False}

        return {
            "isSuccess": True,
            "e_tag": res.headers["ETag"][1:-1],
            "part_id": str(chunk_id),
        }
