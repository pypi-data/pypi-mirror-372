import requests
from layernext.datalake.storage_client import StorageClient


class GCSClient(StorageClient):
    def upload_chunk(
        self, url, chunk_id, chunk_data, content_type, content_range, read_bytes
    ):

        if read_bytes == 0:
            return {"isSuccess": True, "e_tag": "", "part_id": str(chunk_id)}

        headers = {
            "Content-Type": content_type,
            "Content-Range": content_range,
            "Content-Length": f"{read_bytes}",
        }

        res = requests.put(url, data=chunk_data, headers=headers)
        if res.status_code != 200 and res.status_code != 201 and res.status_code != 308:
            print("Error in uploading file to S3: Status code: " + str(res.status_code))
            print(res.text)
            return {"isSuccess": False}

        return {"isSuccess": True, "e_tag": "", "part_id": str(chunk_id)}
