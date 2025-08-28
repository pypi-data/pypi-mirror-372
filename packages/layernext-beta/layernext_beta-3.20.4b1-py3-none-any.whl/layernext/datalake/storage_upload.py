from layernext.datalake.constants import MULTI_PART_UPLOAD_CHUNK_SIZE, MediaType
from layernext.datalake.storage_interface import StorageInterface


class StorageUpload:

    def __init__(
        self,
        client,
        storage_type,
        collection_name,
        upload_id,
        upload_type,
        test_write_progress,
        add_fail_files,
    ):
        self._client = client
        self.collectionName = collection_name
        self.uploadId = upload_id
        self.write_progress = test_write_progress
        self.add_fail_files = add_fail_files
        self.file_id = ""
        self.file_key = ""
        self.storage_type = storage_type
        self.upload_type = upload_type

    """"
    Initialize multipart upload
    """

    def initialize_multipart_upload(self, file_name: str):
        payload = {
            "fileName": file_name,
            "collectionName": self.collectionName,
            "uploadId": self.uploadId,
        }
        multipart_init_res = self._client.datalake_interface.get_file_id_and_key(
            payload
        )
        return multipart_init_res

    """"
    Multipart upload
    """

    def multi_part_upload(self, sub_list):

        for file in sub_list:
            uploaded_parts_arr = []
            for uploaded_part in file["uploaded_parts_arr"]:
                uploaded_parts_arr.append(uploaded_part)

            if file["file_id"] == None:
                """Get file id and key"""
                multipart_init_res = self.initialize_multipart_upload(file["key"])

                if multipart_init_res.get("uploadRemovedFile", False):
                    print(
                        f"\nFile {file['key']} previously removed from this collection and already attached to another collection(s)"
                    )
                    continue

                if multipart_init_res["isSuccess"]:
                    self.file_id = multipart_init_res["fileId"]
                    self.file_key = multipart_init_res["fileKey"]
                    # If isExisting is present and is true, then skip all operations to file because its already uploaded to datalake
                    if (
                        "isExisting" in multipart_init_res
                        and multipart_init_res["isExisting"]
                    ):
                        self.write_progress(uploaded_chunk_count=file["part_count"])
                        print(
                            f"\nFile {self.file_key} already exists in datalake. Skipping upload"
                        )
                        continue
                else:
                    file["is_all"] = True
                    self.add_fail_files(
                        file, None, uploaded_parts_arr, file["part_numbers"]
                    )
                    continue
            else:
                self.file_id = file["file_id"]
                self.file_key = file["file_key"]

            # Set content type based on upload type
            content_type = "application/octet-stream"
            if self.upload_type == MediaType.IMAGE.value:
                content_type = "image/jpeg"
            elif self.upload_type == MediaType.VIDEO.value:
                content_type = "video/mp4"

            pre_signed_url_pay_load = {
                "fileId": self.file_id,
                "fileKey": self.file_key,
                "parts": file["part_count"],
                "contentType": content_type,
            }
            # print('Uploading file: ' + self.file_key + ' with ' + str(file["part_count"]) + ' parts')

            """"Get pre signed url"""
            pre_signed_url_response = (
                self._client.datalake_interface.get_pre_signed_url(
                    pre_signed_url_pay_load
                )
            )
            url_array = []
            if pre_signed_url_response["isSuccess"]:
                if file["is_all"]:
                    if len(file["part_numbers"]) == 0:
                        url_array = pre_signed_url_response["parts"]
                    else:
                        for part_num in file["part_numbers"]:
                            index = next(
                                (
                                    index
                                    for (index, part) in enumerate(
                                        pre_signed_url_response["parts"]
                                    )
                                    if part["PartNumber"] == part_num
                                ),
                                None,
                            )
                            url_array.append(pre_signed_url_response["parts"][index])
            else:
                file["is_all"] = True
                file["file_id"] = self.file_id
                file["file_key"] = self.file_key
                self.add_fail_files(
                    file, None, uploaded_parts_arr, file["part_numbers"]
                )
                continue

            is_upload_success = True
            storage_interface = StorageInterface(self.storage_type, url_array)
            # uploaded_parts_arr = []
            # if file["is_all"] == True:
            finalize_url = ""
            for part in url_array:

                upload_s3_response = {"isSuccess": False}
                finalize_url = part["signedUrl"]

                # if one chunk failed skip the proceeding chunks of this file and add to failed list
                if is_upload_success == True:

                    """ "Upload s3 file"""
                    next_byte = MULTI_PART_UPLOAD_CHUNK_SIZE * (part["PartNumber"] - 1)
                    # Count of bytes to read for each chunk, in case of last part, read only remaining bytes
                    chunk_id = part["PartNumber"] - 1
                    max_read_count = (
                        MULTI_PART_UPLOAD_CHUNK_SIZE
                        if chunk_id < file["part_count"] - 1
                        else file["size"] - next_byte
                    )
                    # url, path, content_type, chunk_id, file_size, start_byte, read_bytes
                    upload_s3_response = storage_interface.upload_to_storage(
                        part["signedUrl"],
                        file["path"],
                        content_type,
                        chunk_id,
                        file["size"],
                        next_byte,
                        max_read_count,
                    )

                if not upload_s3_response["isSuccess"]:
                    file["is_all"] = True
                    file["file_id"] = self.file_id
                    file["file_key"] = self.file_key
                    self.add_fail_files(
                        file, part["PartNumber"], uploaded_parts_arr, None
                    )

                    # if one chunk fail to upload set is_upload_success flag False
                    is_upload_success = False
                    # break
                    # print(f'part number: {part["PartNumber"]} failed')
                else:
                    # print(f'part number: {part["PartNumber"]} success')
                    uploaded_parts_arr.append(
                        {
                            "PartNumber": part["PartNumber"],
                            "ETag": upload_s3_response["e_tag"],
                        }
                    )

                    # Write progress only if its not last part
                    if part["PartNumber"] < file["part_count"]:
                        self.write_progress(uploaded_file_count=0)

            if not is_upload_success:
                # self.add_fail_files(file["key"])
                # #print('Failed to upload file: ' + file["key"])
                continue

            """"Finalize multipart upload"""
            finalize_payload = {
                "fileId": self.file_id,
                "fileKey": self.file_key,
                "parts": uploaded_parts_arr,
                "uploadId": self.uploadId,
                "finalizeUrl": finalize_url,
            }

            finalize_re = self._client.datalake_interface.finalize_upload(
                finalize_payload
            )

            if finalize_re["isSuccess"]:
                self.write_progress()
                # print(f'\nFile {self.file_key} successfully uploaded to datalake')
            else:
                # print('Failed to finalize upload file: ' + file["key"])
                file["is_all"] = False
                file["file_id"] = self.file_id
                file["file_key"] = self.file_key
                self.add_fail_files(
                    file, None, uploaded_parts_arr, file["part_numbers"]
                )
