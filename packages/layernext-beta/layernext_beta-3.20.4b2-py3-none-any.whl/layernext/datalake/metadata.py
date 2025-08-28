import json
from typing import TYPE_CHECKING

from layernext.datalake.constants import MetadataUploadType
from .keys import (
    BUCKET_NAME,
    COLLECTION_ID,
    COLLECTION_NAME,
    FILES,
    IMAGES,
    IS_APPLY_TO_ALL_FILES,
    JOB_ID,
    METADATA,
    OBJECT_TYPE,
    TAGS,
)

if TYPE_CHECKING:
    from . import DatalakeClient


class Metadata:

    def __init__(self, client: "DatalakeClient"):
        self._client = client

    """"
    Uploads metadata to the datalake by passing a json file (load json file and pass it as a parameter)
    @param storage_base_path: collection name
    @param object_type: object type
    @param file_path: json file path
    @param is_meta_by_object_key: boolean value to specify if metadata should be uploaded by object key
    @param bucket_name: bucket name, this is optional and only required if is_meta_by_object_key is true and when uploading metadata with using storage path
    @param job_id: job id, this is optional and only required if is_meta_by_object_key is true and when uploading metadata with using job id
    """

    def upload_metadata_json(
        self,
        file_path: str = None,
        json_data: dict = None,
        bucket_name: str = None,
        job_id: str = None,
        collection_id: str = None,
    ):

        annotation_data = {}
        if file_path != None:
            # load json file
            file = open(file_path)
            annotation_data = json.load(file)
            file.close()
        elif json_data != None:
            annotation_data = json_data
        else:
            raise Exception("File path or json data should be provided")

        is_validate = True
        is_field_validate = True
        metaData_json_array = annotation_data[FILES]

        unique_tags = []
        unique_field_names = []

        if len(metaData_json_array) > 0:

            # iterate metadata json array and extract tags in metadata for each file without duplicates
            for meta_obj in metaData_json_array:
                if METADATA in meta_obj:
                    custom_metadata = meta_obj[METADATA]
                    if TAGS in custom_metadata:
                        tags = custom_metadata[TAGS]
                        # if tags is a array of strings, add it to unique tags
                        if isinstance(tags, list):
                            for tag in tags:
                                if tag not in unique_tags:
                                    unique_tags.append(tag)
                        else:
                            raise Exception("Tags should be an array of strings")

                    # get the keys in metadata object
                    unique_field_keys_set = set(custom_metadata.keys())
                    # remove tags from the set
                    unique_field_keys_set.discard(TAGS)
                    # convert set to list
                    unique_field_names = list(unique_field_keys_set)

            validation_list = []
            # validate tags using datalake api
            if len(unique_tags) > 0:
                validation_list = self._client.datalake_interface.validate_tags(
                    unique_tags
                )
                # if validation_obj is not None:
                #     is_validate = validation_obj["is_valid"]

                # if is_validate is False:
                #     raise Exception(validation_obj["message"])

                for validation_obj in validation_list:
                    newTag = validation_obj["newTag"]
                    oldTag = validation_obj["oldTag"]
                    for i in range(len(metaData_json_array)):
                        metaData_json_array[i]["metadata"]["Tags"] = [
                            oldTag if item == newTag else item
                            for item in metaData_json_array[i]["metadata"]["Tags"]
                        ]

            # validate metadata fields using datalake api
            if len(unique_field_names) > 0:
                meta_field_validation_list = (
                    self._client.datalake_interface.validate_meta_fields(
                        unique_field_names
                    )
                )
                # if meta_field_validation_obj is not None:
                #     is_field_validate = meta_field_validation_obj["is_valid"]
                for validation_obj in meta_field_validation_list:
                    newField = validation_obj["newField"]
                    oldField = validation_obj["oldField"]
                    for i in range(len(metaData_json_array)):
                        if newField in metaData_json_array[i]["metadata"]:
                            metaData_json_array[i]["metadata"][oldField] = (
                                metaData_json_array[i]["metadata"][newField]
                            )
                            del metaData_json_array[i]["metadata"][newField]

            # if is_field_validate is False:
            #     raise Exception(meta_field_validation_obj["message"])

            # execute by paging
            page_size = 1000
            page_i = 0

            # Split metaData_json_array into chunks
            for i in range(0, len(metaData_json_array), page_size):
                json_page = metaData_json_array[i : i + page_size]

                # handle paging
                payload = {
                    METADATA: json_page,
                    BUCKET_NAME: bucket_name,
                    JOB_ID: job_id,
                    COLLECTION_ID: collection_id,
                }
                meta_data_updates = self._client.datalake_interface.upload_metadata(
                    payload, MetadataUploadType.BY_JSON
                )
                # ---

                # Process meta_data_updates
                page_i += 1
                print("Uploading metadata page: ", page_i)
                print(meta_data_updates.get("message"))

            print("Metadata upload process ended")

            return

    """
    Uploads metadata to the datalake by passing a metadata object
    """

    def upload_metadata_object(
        self,
        collection_name: str,
        object_type: str,
        metadata_object: dict,
        is_apply_to_all_files: bool,
    ):
        payload = {
            COLLECTION_NAME: collection_name,
            OBJECT_TYPE: object_type,
            METADATA: metadata_object,
            IS_APPLY_TO_ALL_FILES: is_apply_to_all_files,
        }

        meta_data_updates = self._client.datalake_interface.upload_metadata(
            payload, MetadataUploadType.BY_META_OBJECT
        )
        return meta_data_updates
