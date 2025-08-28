# abstract class to represent a the client in upload data to storage
class StorageClient:
    def upload_chunk(
        self, url, chunk_id, chunk_data, content_type, content_range, read_bytes
    ):
        return {"isSuccess": True, "part_id": str(chunk_id)}
