import os
import sys
import threading
import time
import copy
from multiprocessing.pool import ThreadPool

from layernext.datalake.constants import (
    MAX_UPLOAD_RETRY_COUNT,
    MediaType,
    FILE_UPLOAD_THREADS,
    SUB_FILE_LENGTH,
    MULTI_PART_UPLOAD_CHUNK_SIZE,
)
from layernext.datalake.storage_upload import StorageUpload

imageExtensionList = ["jpg", "jpeg", "png"]
videoExtensionList = ["mp4", "mkv"]


class FileUpload:
    def __init__(self, client: "DatalakeClient"):
        self._client = client
        self.folder_upload = True
        self.path = ""
        self.upload_type = MediaType.IMAGE.value
        self.payload = ""
        self.objectKeyList = []
        self.file_list = []
        self.uploadId = ""
        self.collectionName = ""
        self.collectionId = ""
        self.key_name_array = []
        # Set of failed upload files as key-value map of file name - path
        self.fail_upload_set = []
        self.folder_path = ""
        self.total_keys = 0
        self.progress = 0
        self.count = 0
        self.failed_upload_count = 0
        self.count_lock = threading.Lock()
        self.total_chunk_count = 0
        self.uploaded_chunk_count = 0

    """
    Split object key list
    """

    def split_object_key_list(self, input_list, sub_size):
        sub_list = [
            input_list[i : i + sub_size]
            for i in range(0, len(self.key_name_array), sub_size)
        ]
        return sub_list

    """'
    Check media type
    """

    def check_media_type(self, extension):
        # Convert extension to lower case for case insensitive comparison
        extension = extension.lower()
        if (
            self.upload_type == MediaType.IMAGE.value
            and extension in imageExtensionList
        ):
            return True
        elif (
            self.upload_type == MediaType.VIDEO.value
            and extension in videoExtensionList
        ):
            return True
        elif self.upload_type == MediaType.OTHER.value:
            return True
        else:
            return False

    """'
    Get media file list
    """

    def get_media_files_list(self):
        dir_list = []

        if self.folder_upload:
            dir_list = os.listdir(self.path)
            self.folder_path = self.path
        else:
            path_array = self.path.split("/")
            dir_list.append(path_array[-1])
            path_array.pop()

            index = 0
            for path_component in path_array:
                if index != 0:
                    self.folder_path += "/"

                self.folder_path += path_component

                index += 1

        # Filter according to upload type
        for file_name in dir_list:
            extension = file_name.split(".")[-1]

            if self.check_media_type(extension):
                # Get file size in bytes
                file_full_path = self.folder_path + "/" + file_name
                file_size = os.path.getsize(file_full_path)
                # Determine multi - part upload chunk count - take ceiling of file size / chunk size
                chunk_count = int(file_size / MULTI_PART_UPLOAD_CHUNK_SIZE) + 1
                self.total_chunk_count += chunk_count
                self.objectKeyList.append(file_name)
                self.file_list.append(file_name)
                self.key_name_array.append(
                    {
                        "key": file_name,
                        "path": file_full_path,
                        "part_count": chunk_count,
                        "size": file_size,
                        "is_all": True,
                        "part_numbers": [],
                        "uploaded_parts_arr": [],
                        "file_id": None,
                        "file_key": None,
                    }
                )
                # print("File name: " + file_name + " File size: " + str(file_size) + " Chunk count: " + str(chunk_count))
        self.total_keys = len(self.key_name_array)

    """
    Write progress
    """

    def write_progress(self, count=True, uploaded_file_count=1, uploaded_chunk_count=1):
        if count:
            self.count_lock.acquire()
            try:
                self.count += uploaded_file_count
                self.uploaded_chunk_count += uploaded_chunk_count
                self.progress = 100 * (
                    self.uploaded_chunk_count / self.total_chunk_count
                )
                sys.stdout.write(
                    "\r"
                    + "upload files: "
                    + str(self.count)
                    + f"/{self.total_keys}"
                    + "     "
                    + "progress: "
                    + str(round(self.progress, 2))
                    + " %"
                )
                sys.stdout.flush()
            finally:
                self.count_lock.release()
        else:
            sys.stdout.write(
                "\r"
                + "upload files: "
                + str(self.count)
                + "     "
                + "progress: "
                + str(round(self.progress, 2))
                + " %"
            )
            sys.stdout.flush()

    """'
    Add upload failed files into an array
    """

    def add_fail_files(
        self, file, part_number=None, uploaded_parts_arr=[], part_number_array=[]
    ):
        self.count_lock.acquire()
        try:

            index = next(
                (
                    index
                    for (index, _file) in enumerate(self.fail_upload_set)
                    if _file["key"] == file["key"]
                ),
                None,
            )

            if index != None:
                if part_number != None:
                    self.fail_upload_set[index]["part_numbers"].append(part_number)
                elif part_number_array != None:
                    if len(part_number_array) > 0:
                        self.fail_upload_set[index]["part_numbers"] = part_number_array
                if uploaded_parts_arr != None:
                    for uploaded_part in uploaded_parts_arr:
                        index_upload = next(
                            (
                                index
                                for (index, _uploaded_part) in enumerate(
                                    uploaded_parts_arr
                                )
                                if _uploaded_part["PartNumber"]
                                == uploaded_part["PartNumber"]
                            ),
                            None,
                        )
                        if index_upload == None:
                            self.fail_upload_set[index]["uploaded_parts_arr"].append(
                                uploaded_part
                            )

            else:
                # file_name = object_key.split("/")[-1]
                file["part_numbers"] = []
                if part_number != None:
                    file["part_numbers"].append(part_number)
                elif part_number_array != None:
                    if len(part_number_array) > 0:
                        file["part_numbers"] = part_number_array

                if uploaded_parts_arr != None:
                    file["uploaded_parts_arr"] = uploaded_parts_arr
                self.fail_upload_set.append(file)
            # Set failed count from the key count of fail_upload_set
            self.failed_upload_count = len(self.fail_upload_set)
        finally:
            self.count_lock.release()

    """'
    Parallel upload
    """

    def parallel_upload(self, sublist):
        _upload = StorageUpload(
            self._client,
            self.storage_type,
            self.collectionName,
            self.uploadId,
            self.upload_type,
            self.write_progress,
            self.add_fail_files,
        )
        _upload.multi_part_upload(sublist)

    """'
    File upload initiate     
    """

    def file_upload_initiate(
        self,
        path,
        collection_type,
        collection_name,
        meta_data_object,
        meta_data_override,
        storage_prefix_path,
    ):

        self.write_progress(False)
        is_single_file_upload = False

        self.path = path
        self.payload = {
            "collectionType": collection_type,
            "collectionName": collection_name,
            "metaDataObject": meta_data_object,
            "isOverrideMetaData": meta_data_override,
            "storagePrefixPath": storage_prefix_path,
        }
        self.upload_type = collection_type
        self.collectionName = collection_name

        if not os.path.exists(self.path):
            raise Exception("Path does not exists")
        elif os.path.isdir(path):
            self.folder_upload = True
        elif os.path.isfile(path):
            self.folder_upload = False
            is_single_file_upload = True

        """ Get media file list"""
        self.get_media_files_list()
        self.payload["objectKeyList"] = self.objectKeyList

        """Upload metadata in collection"""
        upload_metadata_response = (
            self._client.datalake_interface.upload_metadata_collection(self.payload)
        )

        if not upload_metadata_response["isSuccess"]:
            msg = upload_metadata_response["message"]
            raise Exception("Can not upload meta data | " + msg)

        self.storage_type = upload_metadata_response["storageType"]
        self.uploadId = upload_metadata_response["uploadId"]
        self.collectionId = upload_metadata_response["collectionId"]

        sub_list = self.split_object_key_list(self.key_name_array, SUB_FILE_LENGTH)

        process = ThreadPool(FILE_UPLOAD_THREADS)
        process.map(self.parallel_upload, sub_list)
        process.close()
        process.join()

        print(
            f"\n\nUpload failed count/total : {self.failed_upload_count}/{self.total_keys}"
        )
        retry_count = 0

        while self.failed_upload_count > 0 and retry_count < MAX_UPLOAD_RETRY_COUNT:
            print(f"Retrying {self.failed_upload_count} failed uploads.....")
            time.sleep(30)
            # Retry with half no of threads
            # Copy failed set to temp array and reset original
            temp_failed_arr = []
            for file in self.fail_upload_set:
                temp_failed_arr.append(file)
            # fail_sub_list = self.split_object_key_list(temp_failed_arr, SUB_FILE_LENGTH)
            self.fail_upload_set = []
            self.failed_upload_count = 0
            retry_count += 1
            print(
                "Retry count: "
                + str(retry_count)
                + " of "
                + str(MAX_UPLOAD_RETRY_COUNT)
            )
            self.parallel_upload(temp_failed_arr)
            time.sleep(1)

        print("Finished processing failed uploads")
        # if self.progress != 0:
        complete_res = self._client.datalake_interface.complete_collection_upload(
            self.uploadId, is_single_file_upload
        )
        if complete_res["isSuccess"]:
            print("\nComplete upload")
        else:
            print("\nError In complete upload")

        if len(self.fail_upload_set) != 0:
            print(
                f"\n\nupload failed files: {self.failed_upload_count}/{self.total_keys}"
            )
            for file_name in self.fail_upload_set:
                print(f'{file_name["key"]}')

        return_obj = {
            "is_success": complete_res["isSuccess"],
            "job_id": upload_metadata_response["jobId"],
            "collection_id": self.collectionId,
        }

        if is_single_file_upload:
            uploaded_file_list = complete_res["uploadedFileList"]
            return_obj["unique_name"] = (
                uploaded_file_list[0] if len(uploaded_file_list) > 0 else ""
            )

        return return_obj

    def get_upload_status(self, collection_name):
        if collection_name == None:
            print("Invalid collection name")
        else:
            progress_response = self._client.datalake_interface.get_upload_status(
                collection_name
            )
            return progress_response
