import base64
import datetime
import os

from typing import List, Union, Dict
from layernext import datalake, dataset, studio, automatic_analysis
from layernext.datalake.constants import (
    AnnotationUploadType,
    ItemType,
    JobStatus,
    JobType,
    MediaType,
    ObjectType,
    SortField,
    SortFieldName,
    SortOrder,
    AnnotationShapeType,
)
from deprecated import deprecated
import uuid
from layernext.datalake.logger import get_debug_logger

# Create a package-level logger
logger = get_debug_logger(__name__)

__version__ = "3.20.4b1"


class LayerNextClient:
    """
    Python SDK of LayerNext
    """

    def __init__(self, api_key: str, secret: str, layernext_url: str) -> None:
        _string_key_secret = f"{api_key}:{secret}"
        _key_secret_bytes = _string_key_secret.encode("ascii")
        _encoded_key_secret_bytes = base64.b64encode(_key_secret_bytes)
        self.encoded_key_secret = _encoded_key_secret_bytes.decode("ascii")
        self.layernext_url = layernext_url
        # self.__check_sdk_version_compatibility()
        logger.info("Initialized LayerNextClient")

    def __check_sdk_version_compatibility(self):
        """
        Check if the SDK version is compatible with the datalake backend version
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        version_id = __version__.split("b")[0]

        _datalake_client.check_sdk_version_compatibility(version_id)

    """
    Annotation data upload from json file with new format and unique_name
    """

    def upload_annotations_by_unique_name(
        self,
        operation_unique_id: str,
        json_data_file_path: str,
        is_normalized: bool,
        is_model_run: bool,
    ):

        self.__upload_annotations(
            None,
            operation_unique_id,
            json_data_file_path,
            None,
            is_normalized,
            is_model_run,
            upload_type=AnnotationUploadType.BY_UNIQUE_NAME,
        )

    """
    Annotation data upload from json file with new format and bucket name
    """

    def upload_annotations_by_storage_path(
        self,
        operation_unique_id: str,
        json_data_file_path: str,
        is_normalized: bool,
        is_model_run: bool,
        bucket_name: str = None,
    ):

        self.__upload_annotations(
            None,
            operation_unique_id,
            json_data_file_path,
            None,
            is_normalized,
            is_model_run,
            bucket_name=bucket_name,
            upload_type=AnnotationUploadType.BY_STORAGE_PATH,
        )

    """
    Deprecated - annotation data upload from json file
    """

    @deprecated(
        reason="This method is now deprecated, so please switch to either 'upload_annotations_by_unique_name,' 'upload_annotations_by_storage_path,' 'upload_annotations_by_job_id,' or 'upload_annotations_for_collection' functions, as this will be removed in the future."
    )
    def upload_annoations_for_folder(
        self,
        collection_base_path: str,
        operation_unique_id: str,
        json_data_file_path: str,
        shape_type: str,
        is_normalized: bool,
        is_model_run: bool,
        destination_project_id: str = None,
    ):

        if collection_base_path is not None and collection_base_path != "":
            collection_id = self.get_collection_id_by_name(collection_base_path)
        else:
            collection_id = None

        self.__upload_annotations(
            collection_id,
            operation_unique_id,
            json_data_file_path,
            shape_type,
            is_normalized,
            is_model_run,
            None,
            upload_type=AnnotationUploadType.BY_FILE_NAME_OR_UNIQUE_NAME,
        )

        if destination_project_id is not None and destination_project_id != "":
            if is_model_run:
                print(
                    f"Attaching model run: {operation_unique_id} to annotation project: {destination_project_id}"
                )
                res = self.attach_model_run_to_project(
                    destination_project_id, [operation_unique_id]
                )
                print(res)
            else:
                print(
                    "Ground truth annotations cannot be attached to Annotation Studio projects as a model run."
                )

    """
    New annotation data upload from json file with new format and file name
    """

    def upload_annotations_for_collection(
        self,
        collection_name: str,
        operation_unique_id: str,
        json_data_file_path: str,
        is_normalized: bool,
        is_model_run: bool,
    ):

        if collection_name is not None and collection_name != "":
            collection_id = self.get_collection_id_by_name(collection_name)
        else:
            raise Exception("Collection name cannot be empty")

        self.__upload_annotations(
            collection_id,
            operation_unique_id,
            json_data_file_path,
            None,
            is_normalized,
            is_model_run,
            upload_type=AnnotationUploadType.BY_FILE_NAME,
        )

    """
    New annotation data upload from json file with new format and job id
    @param job_id: job id
    @param operation_unique_id: operation id
    @param json_data_file_path: json file path
    @param is_normalized: boolean
    @param is_model_run: boolean
    """

    def upload_annotations_by_job_id(
        self,
        job_id: str,
        operation_unique_id: str,
        json_data_file_path: str,
        is_normalized: bool,
        is_model_run: bool,
    ):

        self.__upload_annotations(
            job_id,
            operation_unique_id,
            json_data_file_path,
            None,
            is_normalized,
            is_model_run,
            upload_type=AnnotationUploadType.BY_JOB_ID,
        )

    """
    common function to upload annotations
    @param unique_id: if upload done by collection name, unique id represents collection id. if upload done by job id, unique id represents job id.
    @param operation_unique_id: operation id
    @param json_data_file_path: json file path
    @param shape_type: shape type
    @param is_normalized: boolean
    @param is_model_run: boolean
    @param destination_project_id: destination project id
    @param version: version (v1, v2) this is used to support backward compatibility
    @param bucket_name: bucket name
    @param upload_type: upload type (BY_FILE_NAME, BY_STORAGE_PATH, BY_UNIQUE_NAME, BY_FILE_NAME_OR_UNIQUE_NAME, BY_JOB_ID)
    """

    def __upload_annotations(
        self,
        unique_id: str,
        operation_unique_id: str,
        json_data_file_path: str,
        shape_type: str,
        # this is None for all new annotation upload function. This is used only in 'upload_annoations_for_folder' old annotation upload function
        is_normalized: bool,
        is_model_run: bool,
        version: str = "v2",
        bucket_name: str = None,
        upload_type: AnnotationUploadType = AnnotationUploadType.BY_FILE_NAME,
    ):
        """
        Upload annotation data from a json file
        """
        # init datalake client
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        # assert isinstance(item_type, str), "item_type must be a string"

        allowed_shape_types = [
            AnnotationShapeType.BOX_ANNOTATION.value,
            AnnotationShapeType.LINE_ANNOTATION.value,
            AnnotationShapeType.POLYGON_ANNOTATION.value,
            AnnotationShapeType.POINTS_ANNOTATION.value,
        ]

        if shape_type not in allowed_shape_types and shape_type is not None:
            raise Exception(
                "Invalid annotation shape type, available types are: "
                + str(allowed_shape_types)
            )

        if is_model_run:
            _datalake_client.upload_modelrun_from_json(
                unique_id,
                operation_unique_id,
                json_data_file_path,
                shape_type,
                is_normalized,
                version,
                bucket_name,
                upload_type,
            )
        else:
            _datalake_client.upload_groundtruth_from_json(
                unique_id,
                operation_unique_id,
                json_data_file_path,
                shape_type,
                is_normalized,
                version,
                bucket_name,
                upload_type,
            )

    """
    Download dataset
    """

    def download_dataset(
        self,
        version_id: str,
        export_type: str,
        custom_download_path: str = None,
        is_media_include=True,
    ):
        # init dataset client
        _dataset_client = dataset.DatasetClient(
            self.encoded_key_secret, self.layernext_url, custom_download_path
        )

        # start download
        _dataset_client.download_dataset(version_id, export_type, is_media_include)

    """"
    Images/video upload - deprecated
    """

    @deprecated(
        reason="This method is now deprecated, so please switch to 'upload_files_to_collection' function, as this will be removed in the future."
    )
    def file_upload(
        self,
        path: str,
        collection_type,
        collection_name,
        meta_data_object="",
        override=False,
    ):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        return _datalake_client.file_upload(
            path, collection_type, collection_name, meta_data_object, override, None
        )

    """"
    Images/video upload to a collection
    @param path: local folder path (absolute)
    @param content_type: 'image' or 'video'
    @param collection_name: Collection which files to be uploaded to.
    If existing one is given new files are added to that collection
    @param meta_data_object: Object to specify custom meta data fields and flags
    @param meta_data_override: override provided meta_data_object in case of the file exist already in datalake
    """

    def upload_files_to_collection(
        self,
        path: str,
        content_type: str,
        collection_name: str,
        meta_data_object={},
        meta_data_override=False,
        metadata_file_path=None,
        storage_prefix_path=None,
        annotation_data={
            "json_data_file_path": None,
            "operation_unique_id": None,
            "is_normalized": False,
            "is_model_run": False,
        },
    ):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        if collection_name == "":
            print(f'Invalid collection name "{collection_name}"')
            return {"is_success": False, "collection_id": None}
        if content_type.lower() == "image":
            collection_type = MediaType.IMAGE.value
        elif content_type.lower() == "video":
            collection_type = MediaType.VIDEO.value
        else:
            collection_type = MediaType.OTHER.value

        upload_details = _datalake_client.file_upload(
            path,
            collection_type,
            collection_name,
            meta_data_object,
            meta_data_override,
            storage_prefix_path,
        )

        # if json file path is provided and upload is successful, upload metadata for the files
        if metadata_file_path is not None and upload_details["is_success"] == True:
            print("Trying to upload metadata")
            job_id = upload_details["job_id"]
            self.wait_for_job_complete(job_id)
            self.upload_metadata_by_job_id(job_id, metadata_file_path)
            print("Metadata uploaded successfully")

        # if annotation data is provided and upload is successful, upload annotations for the files
        if (
            annotation_data is not None
            and annotation_data["json_data_file_path"] is not None
            and upload_details["is_success"] == True
        ):
            print("Trying to upload annotations")
            job_id = upload_details["job_id"]
            # if operation id is not provided, or is_model_run, is_normalized is not boolean, return error message and skip annotation upload
            if (
                annotation_data["operation_unique_id"] is None
                or not isinstance(annotation_data["is_normalized"], bool)
                or not isinstance(annotation_data["is_model_run"], bool)
                or annotation_data["operation_unique_id"] == ""
                or annotation_data["json_data_file_path"] == ""
            ):
                print(
                    "Invalid annotation data. Failed to upload annotations. Please provide valid annotation data according to the documentation"
                )
                return upload_details
            # if content type is not image, return error message and skip annotation upload
            if content_type.lower() != "image":
                print(
                    "Invalid content type. Cannot upload annotations for non-image files. Please provide image as the content type"
                )
                return upload_details
            self.wait_for_job_complete(job_id)
            self.upload_annotations_by_job_id(
                job_id,
                annotation_data["operation_unique_id"],
                annotation_data["json_data_file_path"],
                annotation_data["is_normalized"],
                annotation_data["is_model_run"],
            )
            print("Annotations uploaded successfully")

        return upload_details

    """
    This method is used to create a collection head with given name and content type
    """

    def create_or_update_collection(
        self,
        collection_name: str,
        content_type: str,
        custom_meta_object={},
    ):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        if collection_name == "":
            print(f'Invalid collection name "{collection_name}"')
            return {"is_success": False, "collection_id": None}
        if content_type.lower() == "image":
            collection_type = MediaType.IMAGE.value
        elif content_type.lower() == "video":
            collection_type = MediaType.VIDEO.value
        elif content_type.lower() == "other":
            collection_type = MediaType.OTHER.value
        else:
            print(f'Invalid content type "{content_type}"')
            return {"is_success": False, "collection_id": None}

        return _datalake_client.create_collection_head(
            collection_name, collection_type, custom_meta_object
        )

    """
    get item details
    @param unique_name: unique file name
    @param fields_filter: filter to get required meta data
    """

    def get_file_details(
        self, unique_name: str, chat_id: str, fields_filter: dict = None
    ):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        return _datalake_client.get_item_details(unique_name, fields_filter, chat_id)

    """
    get collection details
    @param collection_id: id of the collection
    @param fields_filter: filter to get required meta data
    """

    def get_collection_details(self, collection_id: str, fields_filter: dict = None):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        return _datalake_client.get_collection_details(collection_id, fields_filter)

    """
    Use to get system image, video, other count 
    """

    def get_system_stat_count(self):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        return _datalake_client.get_system_stat_count()

    """
    get collection id by name
    @param collection_name: name of the collection
    @param content_type: 'image', 'video' or 'other'
    """

    def get_collection_id_by_name(
        self, collection_name: str, content_type: str = "image"
    ):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        if content_type.lower() == "image":
            collection_type = MediaType.IMAGE.value
        elif content_type.lower() == "video":
            collection_type = MediaType.VIDEO.value
        elif content_type.lower() == "other":
            collection_type = MediaType.OTHER.value
        else:
            raise Exception("Invalid content type")

        return _datalake_client.get_collection_id_by_name(
            collection_name, collection_type
        )

    """
    get project name by id
    @param project_id: id of project
    """

    def get_annotation_project_name_by_id(
        self,
        project_id: str,
    ):
        _studio_client = studio.StudioClient(
            self.encoded_key_secret, self.layernext_url
        )

        return _studio_client.get_project_name_by_id(project_id)

    """"
    trash common logic for sdk
    @param collection_id: collection id
    @param query: query to filter the objects
    @param filter: filter to filter the objects
    @param object_type: 'image' or 'video'
    @param object_list: list of object ids
    @param is_all_selected: boolean
    """

    def __trash_objects(
        self,
        collection_id: str,
        query: str,
        filter,
        object_type: int,
        object_list,
        is_all_selected=True,
    ):

        filter = self.__create_filter(filter)

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        response = _datalake_client.get_selection_id(
            collection_id, query, filter, object_type, object_list, is_all_selected
        )

        print("selection id: ", response)
        get_selection_id_success = True
        if "isSuccess" in response:
            if response["isSuccess"] == False:
                get_selection_id_success = False
        if get_selection_id_success:
            selection_id = response["selectionTag"]
            return _datalake_client.trash_datalake_object(selection_id)
        else:
            print("trash_response: ", {"isSuccess": False})
            return {"isSuccess": False, "message": response["warningMsg"]}

    """"
    Images/video trash from datalake
    @param datalake_query: query to select objects
    @param datalake_filter: filter to select objects
    @param content_type: 'image' or 'video'
    """

    def trash_objects_from_datalake(
        self,
        datalake_query: str,
        datalake_filter={},
        content_type: str = "image",
    ):
        # print(f'create project using query, filter and collections - project name: {project_name}, ')

        # Prevent all objects case
        if datalake_query == "" and (datalake_filter == "" or datalake_filter == {}):
            print("At least either valid filter or query should be given")
            return {"is_success": False, "error": "Not enough selection parameters"}

        if content_type == "image":
            object_type = ObjectType.IMAGE.value
        elif content_type == "video":
            object_type = ObjectType.VIDEO.value
        else:
            print("No valid content type")
            return {
                "is_success": False,
                "error": "Should specify either image or video as content type",
            }
        try:

            response = self.__trash_objects(
                "", datalake_query, datalake_filter, object_type, []
            )
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {"is_success": False, "error": f"An exception occurred: {format(e)}"}

    """"
    Images/video trash from collection
    @param collection id: collection id
    @param query: query to select objects
    @param filter: filter to select objects
    """

    def trash_objects_from_collection(
        self,
        collection_id: str,
        query: str = "",
        filter={},
    ):

        if filter == None:
            filter = {}

        if collection_id == None or collection_id == "":
            print("collection id must be provided")
            return {"isSuccess": False, "error": "collection id must be provided"}
        object_type_object = self.__get_object_type_by_id(collection_id)
        object_type = None
        if "objectType" in object_type_object:
            object_type = object_type_object["objectType"]

        if object_type == None:
            print("object type cannot find for collection id")
            return {
                "isSuccess": False,
                "error": "object type cannot find for collection id",
            }

        try:
            # if query and filter are empty, collection will be trashed
            if (query == "" or query == None) and (filter == "" or filter == {}):
                response = self.__trash_objects(
                    "", query, filter, object_type, [collection_id], False
                )
            else:
                response = self.__trash_objects(
                    collection_id, query, filter, 0, [], True
                )

            print("trash_response: ", response.get("message"))
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {"isSuccess": False, "error": f"An exception occurred: {format(e)}"}

    """
    Deprecated
    Download collection annotations from datalake
    @param collection_id - id of collection
    @param operation_id - Optional: id of the model (same operation_id given in upload annotations) - default: None
    @param custom_download_path - Optional: custom download path for save downloaded files - default: None
    """

    @deprecated(
        reason="This method is now deprecated and please switch to 'download_collection' function as this will be removed in future"
    )
    def download_annotations(
        self,
        collection_id: str,
        operation_id,
        custom_download_path: str = None,
        is_media_include=True,
    ):

        print(
            'This method is now deprecated and please switch to "download_collection" function as this will be removed in future'
        )
        # init dataset client
        _dataset_client = dataset.DatasetClient(
            self.encoded_key_secret, self.layernext_url, custom_download_path
        )

        operation_id_list = []
        annotation_type = "all"
        if operation_id != None:
            operation_id_list.append(operation_id)
        else:
            annotation_type = "human"

        # start download
        _dataset_client.download_annotations(
            collection_id, annotation_type, operation_id_list, is_media_include
        )

    """
    Download collection annotations from datalake
    @param collection_id - id of collection
    @param annotation_type - Optional: annotation category, can be given ("machine", "human" or "all") - default: "all"
    @param operation_id_list - Optional: id list of the model or ground truth (same operation_id_list given in upload annotations) - default: []
    @param custom_download_path - Optional: custom download path for save downloaded files - default: None
    """

    def download_collection(
        self,
        collection_id: str,
        annotation_type="all",
        operation_id_list=[],
        custom_download_path: str = None,
        is_media_include=True,
    ):
        # init dataset client
        _dataset_client = dataset.DatasetClient(
            self.encoded_key_secret, self.layernext_url, custom_download_path
        )

        # start download
        _dataset_client.download_annotations(
            collection_id, annotation_type, operation_id_list, is_media_include
        )

    """
    Deprecated
    Use to upload annotations for a collection, when file upload to collection.
    @param collection_name: name of the collection
    @param file_path: file path of the folder which contains the files
    @param meta_data_object: meta data object
    @param json_data_file_path: json file path which contains the annotations
    @param is_normalized: boolean
    @param is_model_run: boolean
    """

    @deprecated(
        reason="This method is now deprecated and please switch to 'upload_files_to_collection' function as this will be removed in future"
    )
    def upload_data(
        self,
        collection_name: str,
        file_path: str,
        meta_data_object: dict,
        operation_unique_id: str,
        json_data_file_path: str,
        is_normalized: bool,
        is_model_run: bool,
    ):

        print(
            'This method is now deprecated and please switch to "upload_files_to_collection" function as this will be removed in future'
        )

        upload_details = None
        if file_path == None:
            print("File upload cannot be done")
        else:
            upload_details = self.file_upload(
                file_path, MediaType.IMAGE.value, collection_name, meta_data_object
            )

            if upload_details["is_success"] == False:
                print("Failed to upload files. File upload failed")
                raise Exception("Failed to upload files. File upload failed")

        if json_data_file_path == None:
            print("Failed to upload annotations. Json file path is required")
        else:
            job_id = upload_details["job_id"]
            res = self.wait_for_job_complete(job_id)

            if res["is_success"] == False:
                print("Failed to upload annotations. File upload failed")
                raise Exception("Failed to upload annotations. File upload failed")

            self.upload_annotations_by_job_id(
                job_id,
                operation_unique_id,
                json_data_file_path,
                is_normalized,
                is_model_run,
            )

        return upload_details

    """"
    get upload progress
    """

    def get_upload_status(self, collection_name):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        return _datalake_client.get_upload_status(collection_name)

    """
    remove annotations of collection model run
    """

    def remove_annotations(self, collection_id: str, model_run_id: str):
        print(
            f"remove annotations of collection: {collection_id}, operation id: {model_run_id}"
        )

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        return _datalake_client.remove_collection_annotations(
            collection_id, model_run_id
        )

    def get_valid_sort_fields(self) -> list:
        value_list: list = []
        for field in SortFieldName:
            value_list.append(field.value)
        return value_list

    """'
    Create sort filter
    @sort_obj: {field:"date_modified"/"date_created"/"name"/"size"/"video_index", order: "ASC/DESC"}
    @return: modified sort object(which will compatible withe node side request)
    """

    def __create_sort_filter(self, sort_obj: dict) -> dict:
        modified_sort: dict = {}
        valid_sort_order: list = [SortOrder.ASC.value, SortOrder.DESC.value]

        if "sort_order" in sort_obj:
            sort_order = sort_obj["sort_order"]
            if sort_order not in valid_sort_order:
                raise Exception(f"Invalid sort order. Provide ${valid_sort_order}")
            else:
                modified_sort["sortOrder"] = sort_order

        if "sort_by_field" in sort_obj:
            field = sort_obj["sort_by_field"]
            if field == SortFieldName.DATE_CREATED.value:
                modified_sort["sortByField"] = SortField.DATE_CREATED.value
            elif field == SortFieldName.DATE_MODIFIED.value:
                modified_sort["sortByField"] = SortField.DATE_MODIFIED.value
            elif field == SortFieldName.NAME.value:
                modified_sort["sortByField"] = SortField.NAME.value
            elif field == SortFieldName.SIZE.value:
                modified_sort["sortByField"] = SortField.SIZE.value
            elif field == SortFieldName.VIDEO_INDEX.value:
                modified_sort["sortByField"] = SortField.VIDEO_INDEX.value
            elif field == SortFieldName.TEXT_SCORE.value:
                modified_sort["sortByField"] = SortField.TEXT_SCORE.value
            else:
                valid_fields: list = self.get_valid_sort_fields()
                raise Exception(
                    f"Invalid sort field name.should provide ${valid_fields}"
                )

        return modified_sort

    """
    use to create appropriate filter object from user filter input
    """

    def __create_filter(self, filter):
        # { "annotation_types": ["human", "raw", "machine"], "from_date": "", "to_date": "" }
        return_filter = {
            "annotationTypes": [],
            "date": {},
            "tags": [],
            "labels": [],
            "metadata": {},
            "keywords": [],
            "categories": [],
        }
        if "annotation_types" in filter:
            if "human" in filter["annotation_types"]:
                return_filter["annotationTypes"].append(2)
            if "raw" in filter["annotation_types"]:
                return_filter["annotationTypes"].append(0)
            if "machine" in filter["annotation_types"]:
                return_filter["annotationTypes"].append(1)
        if "to_date" in filter:
            return_filter["date"]["toDate"] = filter["to_date"]
        if "from_date" in filter:
            return_filter["date"]["fromDate"] = filter["from_date"]
        if "keywords" in filter:
            return_filter["keywords"] = filter["keywords"]
        if "categories" in filter:
            return_filter["categories"] = filter["categories"]
        return return_filter

    """
    create annotation studio project using query, filter and collections
    """

    def __create_studio_project(
        self,
        project_name: str,
        collection_id: str,
        query: str,
        filter,
        object_type: int,
        object_list,
        fps,
        frames_per_task,
        assign_to_all,
        send_email,
        content_type,
        default_shape_type,
    ):
        # print(f'create project using query, filter and collections - project name: {project_name}, ')
        filter = self.__create_filter(filter)

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        _studio_client = studio.StudioClient(
            self.encoded_key_secret, self.layernext_url
        )

        response = _datalake_client.get_selection_id(
            collection_id, query, filter, object_type, object_list
        )
        print("selection id: ", response)
        get_selection_id_success = True
        if "isSuccess" in response:
            if response["isSuccess"] == False:
                get_selection_id_success = False
        if get_selection_id_success == True:
            project_response = _studio_client.create_project(
                project_name,
                response["selectionTag"],
                fps,
                frames_per_task,
                assign_to_all,
                send_email,
                default_shape_type,
                content_type,
            )
            return project_response
        else:
            print("project_response: ", {"isSuccess": False})
            return {"isSuccess": False}

    def __get_object_type_by_id(self, object_id: str):
        print(f"get object type by id: {object_id}")

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        response = _datalake_client.get_object_type_by_id(object_id)
        return response

    """
    create annotation studio project using query, filter and collections
    """

    def create_annotation_project_from_collection(
        self,
        project_name: str,
        collection_id: str,
        query: str = "",
        filter={},
        fps: int = 4,
        frames_per_task: int = 120,
        assign_to_all=False,
        send_email=False,
        default_shape_type="rectangle",
    ):
        # print(f'create project using query, filter and collections - project name: {project_name}, ')

        if collection_id == None or collection_id == "":
            print("collection id must be provided")
            return {"isSuccess": False, "error": "collection id must be provided"}
        object_type_object = self.__get_object_type_by_id(collection_id)
        object_type = None
        if "objectType" in object_type_object:
            object_type = object_type_object["objectType"]

        if object_type == None:
            print("object type cannot find for collection id")
            return {
                "isSuccess": False,
                "error": "object type cannot find for collection id",
            }
        content_type = None
        if (
            object_type == ObjectType.VIDEO.value
            or object_type == ObjectType.VIDEO_COLLECTION.value
        ):
            content_type = ObjectType.VIDEO.value
        elif (
            object_type == ObjectType.IMAGE.value
            or object_type == ObjectType.IMAGE_COLLECTION.value
        ):
            content_type = ObjectType.IMAGE.value
        else:
            print("object type is not supported")
            return {"isSuccess": False, "error": "object type is not supported"}

        # if((fps == None) and (object_type == ObjectType.VIDEO.value or object_type == ObjectType.VIDEO_COLLECTION.value)):
        #    print('fps must be provided')
        #    return {
        #        "isSuccess": False,
        #        "error": 'fps must be provided'
        #    }

        try:
            response = self.__create_studio_project(
                project_name,
                collection_id,
                query,
                filter,
                0,
                [],
                fps,
                frames_per_task,
                assign_to_all,
                send_email,
                content_type,
                default_shape_type,
            )
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {"isSuccess": False, "error": f"An exception occurred: {format(e)}"}

    """
    create annotation studio project using query, filter and collections
    """

    def create_annotation_project_from_datalake(
        self,
        project_name: str,
        datalake_query: str,
        datalake_filter={},
        content_type: str = "image",
        fps: int = 4,
        frames_per_task: int = 120,
        assign_to_all=False,
        send_email=False,
        default_shape_type="rectangle",
    ):
        # print(f'create project using query, filter and collections - project name: {project_name}, ')

        # Prevent all objects case
        if datalake_query == "" and (datalake_filter == "" or datalake_filter == {}):
            print("At least either valid filter or query should be given")
            return {"is_success": False, "error": "Not enough selection parameters"}

        # if(object_type == ObjectType.VIDEO or object_type == ObjectType.VIDEO_COLLECTION):
        #    return {
        #        "isSuccess": False,
        #        "error": 'fps must be provided'
        #    }
        if content_type == "image":
            object_type = ObjectType.IMAGE.value
        elif content_type == "video":
            object_type = ObjectType.VIDEO.value
        else:
            print("No valid content type")
            return {
                "is_success": False,
                "error": "Should specify either image or video as content type",
            }
        try:
            response = self.__create_studio_project(
                project_name,
                "",
                datalake_query,
                datalake_filter,
                object_type,
                [],
                fps,
                frames_per_task,
                assign_to_all,
                send_email,
                object_type,
                default_shape_type,
            )
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {"is_success": False, "error": f"An exception occurred: {format(e)}"}

    """
        Attach model runs to a project
        @param project_id: annotation project id
        @param operation_id_array: operation id array (opertion id must be string)
        @return: {is_success: True/False, message: ""}
        """

    def attach_model_run_to_project(
        self, project_id: str, operation_id_array: list
    ) -> dict:
        assert isinstance(project_id, str), "project_id must be a string"
        assert isinstance(
            operation_id_array, list
        ), "operation_id_array must be an array"

        are_all_non_empty_strings: bool = all(
            isinstance(element, str) and element != "" for element in operation_id_array
        )

        if project_id == "":
            return {"is_success": False, "message": "project_id must not empty"}
        if not are_all_non_empty_strings:
            return {
                "is_success": False,
                "message": "operation_id_array must be non empty string array",
            }

        if len(operation_id_array) == 0:
            return {
                "is_success": False,
                "message": "Operation id array must be no empty",
            }

        _studio_client = studio.StudioClient(
            self.encoded_key_secret, self.layernext_url
        )
        res = _studio_client.attach_model_run_to_project(project_id, operation_id_array)
        return res

    """
    update annotation project using query, filter and collections
    """

    def __update_objects_to_studio_project(
        self,
        project_id: str,
        collection_id: str,
        query: str,
        filter,
        object_type: int,
        object_list,
        fps,
        frames_per_task,
        assign_to_all,
        send_email,
        content_type,
        default_shape_type="rectangle",
    ):
        # print(f'create project using query, filter and collections - project id: {project_id}, ')
        filter = self.__create_filter(filter)

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        _studio_client = studio.StudioClient(
            self.encoded_key_secret, self.layernext_url
        )

        response = _datalake_client.get_selection_id(
            collection_id, query, filter, object_type, object_list
        )
        print("selection id: ", response)
        get_selection_id_success = True
        if "isSuccess" in response:
            if response["isSuccess"] == False:
                get_selection_id_success = False
        if get_selection_id_success == True:
            project_response = _studio_client.update_project(
                project_id,
                response["selectionTag"],
                fps,
                frames_per_task,
                assign_to_all,
                send_email,
                default_shape_type,
                content_type,
            )
            print("project_response: ", project_response)
            return project_response
        else:
            print("project_response: ", {"is_success": False})
            return {"is_success": False}

    """
    update annotation studio project using query, filter and collections
    """

    def add_files_to_annotation_project_from_collection(
        self,
        project_id: str,
        collection_id: str,
        query: str,
        filter,
        fps: int = 0,
        frames_per_task: int = 120,
        assign_to_all=False,
        send_email=False,
        default_shape_type="rectangle",
    ):
        # print(f'create project using query, filter and collections - project name: {project_id}, ')

        if collection_id == None or collection_id == "":
            return {"is_success": False, "error": "collection id must be provided"}

        object_type_object = self.__get_object_type_by_id(collection_id)
        object_type = None
        if "objectType" in object_type_object:
            object_type = object_type_object["objectType"]

        if object_type == None:
            print("object type cannot find for collection id")
            return {
                "is_success": False,
                "error": "object type cannot find for collection id",
            }
        content_type = None
        if (
            object_type == ObjectType.IMAGE_COLLECTION.value
            or object_type == ObjectType.IMAGE.value
        ):
            content_type = ObjectType.IMAGE.value
        elif (
            object_type == ObjectType.VIDEO_COLLECTION.value
            or object_type == ObjectType.VIDEO.value
        ):
            content_type = ObjectType.VIDEO.value
        else:
            print("No valid content type")
            return {
                "is_success": False,
                "error": "Should specify either image or video as content type",
            }
        # if(fps == None and (object_type == ObjectType.VIDEO.value or object_type == ObjectType.VIDEO_COLLECTION.value)):
        #    return {
        #        "isSuccess": False,
        #        "error": 'fps must be provided'
        #    }

        try:
            response = self.__update_objects_to_studio_project(
                project_id,
                collection_id,
                query,
                filter,
                0,
                [],
                fps,
                frames_per_task,
                assign_to_all,
                send_email,
                content_type,
                default_shape_type,
            )
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {"is_success": False, "error": f"An exception occurred: {format(e)}"}

    """
    update annotation studio project using query, filter and collections
    """

    def add_files_to_annotation_project_from_datalake(
        self,
        project_id: str,
        query: str,
        filter,
        content_type: str,
        fps: int = 0,
        frames_per_task: int = 120,
        assign_to_all=False,
        send_email=False,
        default_shape_type="rectangle",
    ):
        # print(f'create project using query, filter and collections - project name: {project_id}, ')

        if query == "" and (filter == "" or filter == {}):
            print("At least either valid filter or query should be given")
            return {"is_success": False, "error": "Not enough selection parameters"}

        if content_type == "image":
            object_type = ObjectType.IMAGE.value
        elif content_type == "video":
            object_type = ObjectType.VIDEO.value
        else:
            print("No valid content type")
            return {
                "is_success": False,
                "error": "Should specify either image or video as content type",
            }
        try:
            response = self.__update_objects_to_studio_project(
                project_id,
                "",
                query,
                filter,
                object_type,
                [],
                fps,
                frames_per_task,
                assign_to_all,
                send_email,
                object_type,
                default_shape_type,
            )
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {"is_success": False, "error": f"An exception occurred: {format(e)}"}

    """
    delete a annotation studio project by project id
    """

    def delete_annotation_project(self, project_id: str):
        if project_id == None or project_id == "":
            print("Project id not valid")
            return {"is_success": False, "error": f"Project id not available"}
        print(f"delete project - project id: {project_id}")
        _studio_client = studio.StudioClient(
            self.encoded_key_secret, self.layernext_url
        )
        try:
            response = _studio_client.delete_project(project_id)
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {"is_success": False, "error": f"An exception occurred: {format(e)}"}

    """
    update the labels of studio project
    """

    def __update_labels_to_studio_project(self, project_id: str, add_list, remove_list):
        # print(f'add labels to project - project id: {project_id}, add label list: {add_list}, remove label list: {remove_list}')

        _studio_client = studio.StudioClient(
            self.encoded_key_secret, self.layernext_url
        )

        response = _studio_client.update_labels_to_project(
            project_id, add_list, remove_list
        )

        return response

    """
    add the labels of studio project
    """

    def add_labels_to_studio_project(self, project_id: str, add_list):
        print(
            f"add labels to project - project id: {project_id}, label list: {add_list}"
        )
        try:
            response = self.__update_labels_to_studio_project(project_id, add_list, [])
            print("response: ", response)
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {"is_success": False, "error": f"An exception occurred: {format(e)}"}

    """
    remove the labels of studio project
    """

    def remove_labels_to_studio_project(self, project_id: str, remove_list):
        print(
            f"remove labels to project - project id: {project_id}, label list: {remove_list}"
        )

        try:
            response = self.__update_labels_to_studio_project(
                project_id, [], remove_list
            )
            print("response: ", response)
            return response
        except Exception as e:
            print("An exception occurred", format(e))
            return {"is_success": False, "error": f"An exception occurred: {format(e)}"}

    """
    Get list of studio project
    """

    def get_annotation_project_list(self):
        _studio_client = studio.StudioClient(
            self.encoded_key_secret, self.layernext_url
        )
        return _studio_client.studio_project_list()

    """
    create dataset from search objects
    create dataset from search objects
    @param dataset_name - name of the dataset
    @param collection_id - collection_id for search objects
    @param query - query for search objects
    @param filter - filter for filter objects - {
        "annotation_types": ["human", "raw", "machine"],
        "from_date": "", "to_date": ""
    }
    @param object_type - object_type for search objects
    @param object_list - object_list for search objects
    @param split_info - dataset split information - {
            "train": number,
            "test": number,
            "validation": number
        }
    @param labels - dataset selected labels
    @param export_types - dataset selected export types
    @operation_list - operation id list
    @augmentation_list - augmentation list
    """

    def __create_dataset(
        self,
        dataset_name: str,
        collection_id: str,
        query: str,
        filter,
        object_type,
        object_list,
        split_nfo,
        labels,
        export_types,
        operation_list,
        augmentation_list,
    ):
        print(f"create dataset - dataset name: {dataset_name}")

        if dataset_name == "" or dataset_name == None:
            print(f'Invalid dataset name "{dataset_name}"')
            return {"is_success": False, "error": "Invalid dataset name"}
        if object_type.lower() == "image":
            object_type = ObjectType.IMAGE.value
        elif object_type.lower() == "image_collection":
            object_type = ObjectType.IMAGE_COLLECTION.value
        elif object_type.lower() == "dataset":
            object_type = ObjectType.DATASET.value
        else:
            print("Invalid content type - should be either 'image'")
            return {"is_success": False, "collection_id": None}

        filter = self.__create_filter(filter)

        _dataset_client = dataset.DatasetClient(
            self.encoded_key_secret, self.layernext_url
        )

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        response = _datalake_client.get_selection_id(
            collection_id, query, filter, object_type, object_list
        )
        print("selection id: ", response)
        get_selection_id_success = True
        if "isSuccess" in response:
            if response["isSuccess"] == False:
                get_selection_id_success = False
        if get_selection_id_success == True:
            dataset_response = _dataset_client.create_dataset(
                dataset_name,
                response["selectionTag"],
                split_nfo,
                labels,
                export_types,
                operation_list,
                augmentation_list,
            )
            print("dataset_response: ", dataset_response)
            return dataset_response
        else:
            print("dataset_response: ", {"isSuccess": False})
            return {"isSuccess": False}

    """
    create dataset from search objects on collection
    @param dataset_name - name of the dataset
    @param collection_id - collection_id for search objects
    @param split_info - dataset split information - {
            "train": number,
            "test": number,
            "validation": number
        }
    @param labels - dataset selected labels
    @param export_types - dataset selected export types
    @param query - query for search objects
    @param filter - filter for filter objects - {
        "annotation_types": ["human", "raw", "machine"],
        "from_date": "", "to_date": ""
    }
    @operation_list - operation id list
    @augmentation_list - augmentation list
    """

    def create_dataset_from_collection(
        self,
        dataset_name: str,
        collection_id: str,
        split_info,
        labels=[],
        export_types=[],
        query: str = "",
        filter={},
        operation_list=None,
        augmentation_list=None,
    ):

        if collection_id == None:
            return {"isSuccess": False, "error": "collection id must be provided"}

        object_type_object = self.__get_object_type_by_id(collection_id)
        object_type = None
        if "objectType" in object_type_object:
            object_type = object_type_object["objectType"]

        if object_type == None:
            print("object type cannot find for collection id")
            return {
                "isSuccess": False,
                "error": "object type cannot find for collection id",
            }
        if object_type == ObjectType.IMAGE_COLLECTION.value:
            object_type = "image"
        else:
            return {
                "isSuccess": False,
                "error": "collection type is not acceptable for create dataset, only image collections are valid",
            }

        return self.__create_dataset(
            dataset_name,
            collection_id,
            query,
            filter,
            object_type,
            [],
            split_info,
            labels,
            export_types,
            operation_list,
            augmentation_list,
        )

    """
    create dataset from search objects on datalake
    @param dataset_name - name of the dataset
    @param split_info - dataset split information - {
            "train": number,
            "test": number,
            "validation": number
        }
    @param labels - dataset selected labels
    @param export_types - dataset selected export types
    @param content_type - content_type for search objects
    @param query - query for search objects
    @param filter - filter for filter objects - {
        "annotation_types": ["human", "raw", "machine"],
        "from_date": "", "to_date": ""
    }
    @operation_list - operation id list
    @augmentation_list - augmentation list
    """

    def create_dataset_from_datalake(
        self,
        dataset_name: str,
        split_info,
        labels=[],
        export_types=[],
        item_type="image",
        query: str = "",
        filter={},
        operation_list=None,
        augmentation_list=None,
    ):

        return self.__create_dataset(
            dataset_name,
            None,
            query,
            filter,
            item_type,
            [],
            split_info,
            labels,
            export_types,
            operation_list,
            augmentation_list,
        )

    """
    update dataset from search objects
    @param version_id - id of the base version
    @param collection_id - collection_id for search objects
    @param query - query for search objects
    @param filter - filter for filter objects - {
        "annotation_types": ["human", "raw", "machine"],
        "from_date": "", "to_date": ""
    }
    @param object_type - object_type for search objects
    @param object_list - object_list for search objects
    @param split_info - dataset split information - {
            "train": number,
            "test": number,
            "validation": number
        }
    @param labels - dataset selected labels
    @param export_types - dataset selected export types
    @param is_new_version_required - whether creating new version (True) or update existing version (False)
    @operation_list - operation id list
    @augmentation_list - augmentation list
    """

    def __update_dataset_version(
        self,
        version_id: str,
        collection_id: str,
        query: str,
        filter,
        object_type,
        object_list,
        split_info,
        labels,
        export_types,
        is_new_version_required,
        operation_list,
        augmentation_list,
    ):
        print(f"create dataset - dataset version id: {version_id}")

        if object_type.lower() == "image":
            object_type = ObjectType.IMAGE.value
        elif object_type.lower() == "image_collection":
            object_type = ObjectType.IMAGE_COLLECTION.value
        elif object_type.lower() == "dataset":
            object_type = ObjectType.DATASET.value
        else:
            print("Invalid content type - should be either 'image'")
            return {"is_success": False}

        filter = self.__create_filter(filter)

        _dataset_client = dataset.DatasetClient(
            self.encoded_key_secret, self.layernext_url
        )

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        response = _datalake_client.get_selection_id(
            collection_id, query, filter, object_type, object_list
        )
        print("selection id: ", response)
        get_selection_id_success = True
        if "isSuccess" in response:
            if response["isSuccess"] == False:
                get_selection_id_success = False
        if get_selection_id_success == True:
            dataset_response = _dataset_client.update_dataset_version(
                version_id,
                response["selectionTag"],
                split_info,
                labels,
                export_types,
                is_new_version_required,
                operation_list,
                augmentation_list,
            )
            print("dataset_response: ", dataset_response)
            return dataset_response
        else:
            print("dataset_response: ", {"isSuccess": False})
            return {"isSuccess": False}

    """
    update dataset from search objects on collection
    @param version_id - id of the base version
    @param collection_id - collection_id for search objects
    @param split_info - dataset split information - {
            "train": number,
            "test": number,
            "validation": number
        }
    @param labels - dataset selected labels
    @param export_types - dataset selected export types
    @param query - query for search objects
    @param filter - filter for filter objects - {
        "annotation_types": ["human", "raw", "machine"],
        "from_date": "", "to_date": ""
    }
    @param is_new_version_required - whether creating new version (True) or update existing version (False)
    @operation_list - operation id list
    @augmentation_list - augmentation list
    """

    def update_dataset_version_from_collection(
        self,
        version_id: str,
        collection_id: str,
        split_info,
        labels=[],
        export_types=[],
        query: str = "",
        filter={},
        is_new_version_required=False,
        operation_list=None,
        augmentation_list=None,
    ):

        if collection_id == None or collection_id == "":
            return {"isSuccess": False, "error": "collection id must be provided"}
        if version_id == None or version_id == "":
            return {"isSuccess": False, "error": "version id must be provided"}

        object_type_object = self.__get_object_type_by_id(collection_id)
        object_type = None
        if "objectType" in object_type_object:
            object_type = object_type_object["objectType"]

        if object_type == None:
            print("object type cannot find for collection id")
            return {
                "isSuccess": False,
                "error": "object type cannot find for collection id",
            }
        if object_type == ObjectType.IMAGE_COLLECTION.value:
            object_type = "image"
        else:
            return {
                "isSuccess": False,
                "error": "collection type is not acceptable for create dataset, only image collections are valid",
            }

        return self.__update_dataset_version(
            version_id,
            collection_id,
            query,
            filter,
            object_type,
            [],
            split_info,
            labels,
            export_types,
            is_new_version_required,
            operation_list,
            augmentation_list,
        )

    """
    update dataset from search objects on datalake
    @param version_id - id of the base version
    @param split_info - dataset split information - {
            "train": number,
            "test": number,
            "validation": number
        }
    @param labels - dataset selected labels
    @param export_types - dataset selected export types
    @param item_type - content_type for search objects
    @param query - query for search objects
    @param filter - filter for filter objects - {
        "annotation_types": ["human", "raw", "machine"],
        "from_date": "", "to_date": ""
    }
    @param is_new_version_required - whether creating new version (True) or update existing version (False)
    @operation_list - operation id list
    @augmentation_list - augmentation list
    """

    def update_dataset_version_from_datalake(
        self,
        version_id: str,
        split_info,
        labels=[],
        export_types=[],
        item_type: str = "image",
        query: str = "",
        filter={},
        is_new_version_required=False,
        operation_list=None,
        augmentation_list=None,
    ):

        if version_id == None or version_id == "":
            return {"isSuccess": False, "error": "version id must be provided"}
        return self.__update_dataset_version(
            version_id,
            None,
            query,
            filter,
            item_type,
            [],
            split_info,
            labels,
            export_types,
            is_new_version_required,
            operation_list,
            augmentation_list,
        )

    """
    delete dataset version
    @param version_id - id of the deleting version
    """

    def delete_dataset_version(self, version_id: str):
        print(f"delete dataset version - dataset version id: {version_id}")

        _dataset_client = dataset.DatasetClient(
            self.encoded_key_secret, self.layernext_url
        )
        response = _dataset_client.delete_dataset_version(version_id)
        print(response)
        return response

    """
    Get list of all system labels
    """

    def get_all_labels(self):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        return _datalake_client.get_system_labels()

    """
    Get list of system labels that attached to given group
    """

    def get_labels_in_group(self, group_id):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        return _datalake_client.get_system_labels(group_id)

    """
    Create system label
    """

    def create_system_label(self, label):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        return _datalake_client.create_system_label(label)

    """
    Create a group from labels (label keys)
    """

    def create_label_group(self, group_name, label_ids):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        return _datalake_client.create_label_group(group_name, label_ids)

    """
    Attach labels to a group
    """

    def attach_labels_to_group(self, group_id, label_ids):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        return _datalake_client.attach_labels_to_group(group_id, label_ids)

    """
    Detach labels from group
    """

    def detach_labels_from_group(self, group_id, label_ids):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        return _datalake_client.detach_labels_from_group(group_id, label_ids)

    """
    List All label groups
    """

    def get_all_label_groups(self):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        return _datalake_client.get_all_label_groups()

    """
    Attach label group to annotation project
    """

    def attach_label_group_to_annotation_project(self, project_id, group_id):
        _studio_client = studio.StudioClient(
            self.encoded_key_secret, self.layernext_url
        )
        return _studio_client.project_set_label_group(project_id, group_id)

    """
    Deprecated
    Download project annotations
    @param project_id - id of annotation project
    @param task_status_list - (Optional): To filter by task status - default: []
    @param is_annotated_only - (Optional): If True, then only the annotated images are downloaded - default: False
    @param custom_download_path - (Optional): To download data to required location instead of current directory - default: None
    """

    @deprecated(
        reason="This method is now deprecated and please switch to 'download_annotation_projects' function as this will be removed in future"
    )
    def download_project_annotations(
        self,
        project_id,
        task_status_list: list = [],
        is_annotated_only: bool = False,
        custom_download_path: str = None,
        is_media_include=True,
    ):

        print(
            'This method is now deprecated and please switch to "download_annotation_projects" function as this will be removed in future'
        )
        # init dataset client
        _dataset_client = dataset.DatasetClient(
            self.encoded_key_secret, self.layernext_url, custom_download_path
        )

        project_id_list = []
        project_id_list.append(project_id)
        # start download
        _dataset_client.download_annotations_for_project_v2(
            project_id_list, task_status_list, is_annotated_only, is_media_include
        )

    """
    Download multiple project annotations
    @param project_id_list - id list of annotation projects
    @param task_status_list - (Optional): To filter by task status - default: []
    @param is_annotated_only - (Optional): If True, then only the annotated images are downloaded - default: False
    @param custom_download_path - (Optional): To download data to required location instead of current directory - default: None
    """

    def download_annotation_projects(
        self,
        project_id_list,
        task_status_list: list = [],
        is_annotated_only: bool = False,
        custom_download_path: str = None,
        is_media_include=True,
    ):

        if task_status_list == None:
            task_status_list = []

        # init dataset client
        _dataset_client = dataset.DatasetClient(
            self.encoded_key_secret, self.layernext_url, custom_download_path
        )

        # start download
        _dataset_client.download_annotations_for_project_v2(
            project_id_list, task_status_list, is_annotated_only, is_media_include
        )

    """
    Wait until job complete
    @param job_id - id of the relevant job
    """

    def wait_for_job_complete(self, job_id: str):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        return _datalake_client.wait_for_job_complete(job_id)

    """
    Get downloadable url of a file in Data Lake
    @param file_key - File path in Data Lake
    """

    def get_downloadable_url(self, file_key: str):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        return _datalake_client.get_file_download_url(file_key)

    """
    Upload metadata data from a json file
    """

    def upload_metadata_for_files(
        self,
        collection_name: str,
        content_type: str,
        json_data_file_path: str,
    ):
        # init datalake client
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        if collection_name is not None and collection_name != "":
            collection_id = self.get_collection_id_by_name(
                collection_name, content_type
            )
        else:
            raise Exception("Collection name cannot be empty")

        _datalake_client.upload_metadata_from_json(collection_id, json_data_file_path)

    """
    Upload metadata from a json file with unique names
    @param: json_data_file_path - path of the json file in format - [{file:str, metadata:{Field:str, Tags:[str]}}]
    @item_type: "image", "video", "other"
    @query: datalake query
    """

    def upload_metadata_by_unique_name(
        self, json_data_file_path: str = None, json_data: dict = None
    ):
        # init datalake client
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        _datalake_client.upload_metadata_from_unique_name_json(
            json_data_file_path, json_data
        )

    """
    Upload metadata from a json file with storage path
    @param: json_data_file_path - path of the json file in format - [{file:str, metadata:{Field:str, Tags:[str]}}]
    @bucket_name: bucket name, if not given, default bucket will be used
    """

    def upload_metadata_by_storage_path(
        self, json_data_file_path: str, bucket_name: str = None
    ):
        # init datalake client
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        _datalake_client.upload_metadata_from_storage_path_json(
            json_data_file_path, bucket_name
        )

    """
    Upload metadata from a json file with job id
    @param: json_data_file_path - path of the json file in format - [{file:str, metadata:{Field:str, Tags:[str]}}]
    @job_id: job id, it is required
    """

    def upload_metadata_by_job_id(
        self,
        job_id: str,
        json_data_file_path: str,
    ):
        # init datalake client
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        _datalake_client.upload_metadata_from_job_id(job_id, json_data_file_path)

    """
    Upload metadata data from a metadata object
    """

    def upload_metadata_for_collection(
        self,
        collection_name: str,
        content_type: str,
        metadata_obj: dict,
        is_apply_to_all_files=True,
    ):

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        if content_type.lower() == "image":
            collection_type = MediaType.IMAGE.value
        elif content_type.lower() == "video":
            collection_type = MediaType.VIDEO.value
        elif content_type.lower() == "other":
            collection_type = MediaType.OTHER.value
        else:
            raise Exception("Invalid content type")

        _datalake_client.upload_metadata_from_metaObject(
            collection_name, collection_type, metadata_obj, is_apply_to_all_files
        )

    """
    Upload models for Datalake collection Autotagging
    @param input_model_path: path of the model folder which needed to be uploaded
    @param model_id        : id/name of the model which is registered in the datalake
    @param task            : automatic analysis task which should the registering model will be used to
    """

    def register_model(self, input_model_path, model_id, task):

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        _automatic_analysis_client = automatic_analysis.AutomaticAnalysisClient(
            self.encoded_key_secret, self.layernext_url
        )

        _automatic_analysis_client.register_model(
            input_model_path, model_id, _datalake_client, task
        )

    """
    autotagging a given collection and updating tags of the collection
    @param collection_id        : id of the image or video collection
    @param model_id             : id/name of the model which is registered in the datalake
    @param input_resolution     : resolution of the frames which should be considered at inference(image or video)
    @param confidence_threshold : confidence score to consider which objects/segments to consider for the proccedings
    """

    def auto_tag_collection(
        self,
        collection_id,
        model_id="default",
        input_resolution=(480, 480),
        confidence_threshold=0.5,
        query="",
        filters={},
        inference_platform="use_env",
    ):

        session_id = str(datetime.datetime.now().timestamp())
        job_name = f"Auto-tagging-generate-{model_id}"

        res_obj = self.create_or_update_job(
            session_id,
            job_name,
            JobType.GENERATE_AUTO_TAGGING.value,
            0,
            JobStatus.QUEUED.value,
        )

        if ("success" in res_obj and res_obj["success"] == True) and res_obj[
            "jobId"
        ] is not None:
            job_id = res_obj["jobId"]
        else:
            print("Error occurred while create job")
            raise Exception("Error occurred while create job")

        _automatic_analysis_client = automatic_analysis.AutomaticAnalysisClient(
            self.encoded_key_secret, self.layernext_url
        )
        res = _automatic_analysis_client.model_tag_collection(
            collection_id,
            model_id,
            input_resolution,
            confidence_threshold,
            session_id,
            job_id,
            job_name,
            query,
            filters,
            inference_platform,
        )

        return {"jobId": job_id}

    """
    autotagging a given item type files in whole metalake and updating tags of the collection
    @param item_type            : "image", "video", "other", "image_collection", "video_collection", "other_collection", "dataset"
    @param model_id             : id/name of the model which is registered in the datalake
    @param input_resolution     : resolution of the frames which should be considered at inference(image or video)
    @param confidence_threshold : confidence score to consider which objects/segments to consider for the proccedings
    """

    def generate_auto_tags_to_metalake(
        self,
        item_type,
        model_id="default",
        input_resolution=(300, 300),
        confidence_threshold=0.5,
        query="",
        filters={},
        inference_platform="use_env",
    ):

        session_id = str(datetime.datetime.now().timestamp())
        job_name = f"Auto-tagging-generate-{model_id}"

        res_obj = self.create_or_update_job(
            session_id,
            job_name,
            JobType.GENERATE_AUTO_TAGGING.value,
            0,
            JobStatus.QUEUED.value,
        )

        if ("success" in res_obj and res_obj["success"] == True) and res_obj[
            "jobId"
        ] is not None:
            job_id = res_obj["jobId"]
        else:
            print("Error occurred while create job")
            raise Exception("Error occurred while create job")

        _automatic_analysis_client = automatic_analysis.AutomaticAnalysisClient(
            self.encoded_key_secret, self.layernext_url
        )
        res = _automatic_analysis_client.model_tag_population(
            item_type,
            model_id,
            input_resolution,
            confidence_threshold,
            session_id,
            job_id,
            job_name,
            query,
            filters,
            inference_platform,
        )

        return {"jobId": job_id}

    """
    auto annotating a given frames of an annotation project
    @param project_id           : annotation project ID which needs to be annotated
    @param prompt               : input prompt describing which labels to annotate and their descriptions
    @param annotation_type      : bounding box annotation or polygon segment annotation
    @param model_id             : id/name of the model which is registered in the datalake
    @param confidence_threshold : confidence score to consider which objects/segments to consider for the proccedings
    @auto_annotation_operation  : Operation to do , sam-text, sam-img-encoding
    """

    def auto_annotate_project(
        self,
        project_id,
        # prompt=[],
        annotation_type="segment",
        model_id="default",
        # confidence_threshold=0.5,
        # auto_annotation_operation='sam-text'
        **kwargs,
    ):

        session_id = str(datetime.datetime.now().timestamp())
        job_name = f"Auto-annotation-generate-{model_id}"

        res_obj = self.create_or_update_job(
            session_id,
            job_name,
            JobType.GENERATE_AUTO_ANNOTATION.value,
            0,
            JobStatus.QUEUED.value,
        )

        if ("success" in res_obj and res_obj["success"] == True) and res_obj[
            "jobId"
        ] is not None:
            job_id = res_obj["jobId"]
        else:
            print("Error occurred while create job")
            raise Exception("Error occurred while create job")

        _automatic_analysis_client = automatic_analysis.AutomaticAnalysisClient(
            self.encoded_key_secret, self.layernext_url
        )
        # _automatic_analysis_client.model_annotate_collection(
        #     project_id, model_id, prompt, annotation_type, confidence_threshold, auto_annotation_operation)
        _automatic_analysis_client.model_annotate_collection(
            project_id, model_id, annotation_type, session_id, job_name, **kwargs
        )

        return {"jobId": job_id}

    def prompt_inference(self, name, shape, **kwargs):

        _automatic_analysis_client = automatic_analysis.AutomaticAnalysisClient(
            self.encoded_key_secret, self.layernext_url
        )

        _automatic_analysis_client.prompt_infer_image(name, shape, **kwargs)

    """
    generate embedding for a given collection (image) and upload the embeddings to the vector database
    @param collection_id: id of the image.
    @param model_id:id/name of the model which is registered in the datalake
    """

    def generate_embeddings_for_collection(
        self,
        collection_id,
        model_id="default",
        query="",
        filters={},
        inference_platform="use_env",
    ):

        session_id = str(datetime.datetime.now().timestamp())
        job_name = f"Embedding-generate-{model_id}"

        res_obj = self.create_or_update_job(
            session_id,
            job_name,
            JobType.GENERATE_EMBEDDING.value,
            0,
            JobStatus.QUEUED.value,
        )

        if ("success" in res_obj and res_obj["success"] == True) and res_obj[
            "jobId"
        ] is not None:
            job_id = res_obj["jobId"]
        else:
            print("Error occurred while create job")
            raise Exception("Error occurred while create job")

        _automatic_analysis_client = automatic_analysis.AutomaticAnalysisClient(
            self.encoded_key_secret, self.layernext_url
        )
        res = _automatic_analysis_client.embedding_model_inference_collection(
            collection_id,
            model_id,
            query,
            filters,
            session_id,
            job_id,
            job_name,
            inference_platform,
        )
        return {"jobId": job_id}

    def generate_embeddings_to_metalake(
        self,
        item_type="image",
        model_id="default",
        query="",
        filters={},
        inference_platform="use_env",
    ):

        session_id = str(datetime.datetime.now().timestamp())
        job_name = f"Embedding-generate-{model_id}"

        res_obj = self.create_or_update_job(
            session_id,
            job_name,
            JobType.GENERATE_EMBEDDING.value,
            0,
            JobStatus.QUEUED.value,
        )

        if ("success" in res_obj and res_obj["success"] == True) and res_obj[
            "jobId"
        ] is not None:
            job_id = res_obj["jobId"]
        else:
            print("Error occurred while create job")
            raise Exception("Error occurred while create job")

        _automatic_analysis_client = automatic_analysis.AutomaticAnalysisClient(
            self.encoded_key_secret, self.layernext_url
        )
        res = _automatic_analysis_client.model_embedding_population(
            item_type,
            model_id,
            query,
            filters,
            session_id,
            job_id,
            job_name,
            inference_platform,
        )

        return {"jobId": job_id}

    """
    get item list from data lake
    @item_type: "image", "video", "other", "image_collection", "video_collection", "other_collection", "dataset"
    @query: datalake query
    @filter: {date: {fromDate: "", toDate: ""}, "annotation_types": ["human", "raw", "machine"]}
    @page_index - index of the page
    @page_size - size of the page, maximum = 1000
    @sort_order: {sort_by_field:"date_modified"/"date_created"/"name"/"size"/"video_index"/"text_score", sort_order: "ASC/DESC"}
    """

    def get_item_list_from_datalake(
        self,
        item_type,
        query: str = "",
        filter={},
        page_index=0,
        page_size=20,
        sort_order: dict = {},
    ):

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        item_type_enum = 2
        if item_type == "image":
            item_type_enum = ObjectType.IMAGE.value
        elif item_type == "video":
            item_type_enum = ObjectType.VIDEO.value
        elif item_type == "other":
            item_type_enum = ObjectType.OTHER.value
        elif item_type == "image_collection":
            item_type_enum = ObjectType.IMAGE_COLLECTION.value
        elif item_type == "video_collection":
            item_type_enum = ObjectType.VIDEO_COLLECTION.value
        elif item_type == "other_collection":
            item_type_enum = ObjectType.OTHER_COLLECTION.value
        elif item_type == "dataset":
            item_type_enum = ObjectType.DATASET.value

        filter = self.__create_filter(filter)
        sort_filter = self.__create_sort_filter(sort_order)
        return _datalake_client.get_item_list_from_datalake(
            item_type_enum, query, filter, page_index, page_size, sort_filter
        )

    def get_item_list_from_datalake_llm(
        self,
        item_type,
        query: str = "",
        filter={},
        page_index=0,
        page_size=20,
        sort_order: dict = {},
        request_id=uuid.uuid4(),
        chat_id="",
    ):

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        item_type_enum = 2
        if item_type == "image":
            item_type_enum = ObjectType.IMAGE.value
        elif item_type == "video":
            item_type_enum = ObjectType.VIDEO.value
        elif item_type == "other":
            item_type_enum = ObjectType.OTHER.value
        elif item_type == "image_collection":
            item_type_enum = ObjectType.IMAGE_COLLECTION.value
        elif item_type == "video_collection":
            item_type_enum = ObjectType.VIDEO_COLLECTION.value
        elif item_type == "other_collection":
            item_type_enum = ObjectType.OTHER_COLLECTION.value
        elif item_type == "dataset":
            item_type_enum = ObjectType.DATASET.value

        filter = self.__create_filter(filter)
        sort_filter = self.__create_sort_filter(sort_order)
        return _datalake_client.get_item_list_from_datalake_llm(
            item_type_enum,
            query,
            filter,
            page_index,
            page_size,
            sort_filter,
            request_id,
            chat_id,
        )

    """
    get item count from metalake
    @item_type: "image", "video", "other", "image_collection", "video_collection", "other_collection", "dataset"
    @query: metalake query
    @filter: {date: {fromDate: "", toDate: ""}, "annotation_types": ["human", "raw", "machine"]}
    """

    def get_item_count_from_metalake(
        self,
        item_type,
        query: str = "",
        filter={},
    ):

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        item_type_enum = 2
        if item_type == "image":
            item_type_enum = ObjectType.IMAGE.value
        elif item_type == "video":
            item_type_enum = ObjectType.VIDEO.value
        elif item_type == "other":
            item_type_enum = ObjectType.OTHER.value
        elif item_type == "image_collection":
            item_type_enum = ObjectType.IMAGE_COLLECTION.value
        elif item_type == "video_collection":
            item_type_enum = ObjectType.VIDEO_COLLECTION.value
        elif item_type == "other_collection":
            item_type_enum = ObjectType.OTHER_COLLECTION.value
        elif item_type == "dataset":
            item_type_enum = ObjectType.DATASET.value

        filter = self.__create_filter(filter)
        return _datalake_client.get_item_count_from_metalake(
            item_type_enum,
            query,
            filter,
        )

    """
    download files from collection(videos, images, others)
    @param collection_id: collection id
    @param custom_download_path: absolute path files need to be downloaded
    @param page_index: index of the page
    @param page_size: size of the page, maximum = 1000
    @param query: datalake query
    @param metalake_filter: {date: {fromDate: "", toDate: ""}, "annotation_types": ["human", "raw", "machine"]}
    @sort_order: {sort_by_field:"date_modified"/"date_created"/"name"/"size"/"video_index", sort_order: "ASC/DESC"}
    @return: {is_success: True/False, message: ""}
    """

    def download_files_from_collection(
        self,
        collection_id: str,
        custom_download_path: str = "",
        page_index: int = 0,
        page_size: int = 20,
        query: str = "",
        metalake_filter: dict = {},
        sort_order: dict = {},
    ) -> dict:

        assert isinstance(collection_id, str), "collection_id must be a string"
        assert isinstance(
            custom_download_path, str
        ), "custom_download_path must be a string"
        assert isinstance(query, str), "query must be a string"
        assert isinstance(metalake_filter, dict), "data_filter must be a dictionary"
        assert isinstance(page_index, int), "page_index must be an integer"
        assert isinstance(page_size, int), "page_size must be an integer"

        if collection_id == "":
            return {"is_success": False, "message": "collection_id should not empty"}

        object_type_object = self.__get_object_type_by_id(collection_id)
        object_type = None
        if "objectType" in object_type_object:
            object_type = object_type_object["objectType"]

        if object_type == None:
            print("object type cannot find for collection id")
            return {
                "is_success": False,
                "message": "object type cannot find for collection id",
            }
        item_type_enum = 2
        if object_type == ObjectType.IMAGE_COLLECTION.value:
            item_type_enum = ObjectType.IMAGE.value
        elif object_type == ObjectType.VIDEO_COLLECTION.value:
            item_type_enum = ObjectType.VIDEO.value
        elif object_type == ObjectType.OTHER_COLLECTION.value:
            item_type_enum = ObjectType.OTHER.value
        elif object_type == ObjectType.DATASET.value:
            item_type_enum = ObjectType.IMAGE.value
        else:
            return {
                "is_success": False,
                "message": "collection type is not acceptable get item list",
            }

        metalake_filter = self.__create_filter(metalake_filter)
        # metalake_filter["contentType"] = item_type_enum
        sort_filter = self.__create_sort_filter(sort_order)

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        return _datalake_client.download_files_batch_wise(
            item_type_enum,
            query,
            metalake_filter,
            page_index,
            page_size,
            custom_download_path,
            {"collection_id": collection_id},
            sort_filter,
        )

    """
        Download files from metalake
       @param item_type: supported types are "image", "video", "other"
       @param custom_download_path: absolute path files need to be downloaded
       @param page_index: index of the page
       @param page_size: size of the page, maximum = 1000
       @param query: datalake query
       @param metalake_filter: {date: {fromDate: "", toDate: ""}, "annotation_types": ["human", "raw", "machine"]}
       @sort_order: {sort_by_field:"date_modified"/"date_created"/"name"/"size"/"video_index", sort_order: "ASC/DESC"}
       @return: {is_success: True/False, message: ""}
       """

    def download_files_from_metalake(
        self,
        item_type: str,
        custom_download_path: str = "",
        page_index: int = 0,
        page_size: int = 20,
        query: str = "",
        metalake_filter: dict = {},
        sort_order: dict = {},
    ) -> dict:

        assert isinstance(item_type, str), "item_type must be a string"
        assert isinstance(
            custom_download_path, str
        ), "custom_download_path must be a string"
        assert isinstance(query, str), "query must be a string"
        assert isinstance(metalake_filter, dict), "data_filter must be a dictionary"
        assert isinstance(page_index, int), "page_index must be an integer"
        assert isinstance(page_size, int), "page_size must be an integer"

        allowed_types = [
            ItemType.IMAGE.value,
            ItemType.VIDEO.value,
            ItemType.OTHER.value,
        ]

        if item_type not in allowed_types:
            raise Exception(
                "Invalid item type, available types are: " + str(allowed_types)
            )

        item_type_enum = 0
        if item_type == ItemType.IMAGE.value:
            item_type_enum = ObjectType.IMAGE.value
        elif item_type == ItemType.VIDEO.value:
            item_type_enum = ObjectType.VIDEO.value
        elif item_type == ItemType.OTHER.value:
            item_type_enum = ObjectType.OTHER.value

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        metalake_filter = self.__create_filter(metalake_filter)
        # metalake_filter["contentType"] = item_type_enum
        sort_filter = self.__create_sort_filter(sort_order)

        return _datalake_client.download_files_batch_wise(
            item_type_enum,
            query,
            metalake_filter,
            page_index,
            page_size,
            custom_download_path,
            {"item_type": item_type_enum},
            sort_filter,
            item_type,
        )

    """
    get item list from collection in datalake
    @collection_id: id of the collection
    @query: datalake query
    @filter: {date: {fromDate: "", toDate: ""},  "annotation_types": ["human", "raw", "machine"]}
    @page_index - index of the page
    @page_size - size of the page, maximum = 1000
    @sort_order: {sort_by_field:"date_modified"/"date_created"/"name"/"size"/"video_index", sort_order: "ASC/DESC"}
    """

    def get_item_list_from_collection(
        self,
        collection_id,
        query: str = "",
        filter={},
        page_index=0,
        page_size=20,
        sort_order: dict = {},
    ):

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        item_type_enum = 2
        if collection_id == None or collection_id == "":
            return {"isSuccess": False, "error": "collection id must be provided"}

        object_type_object = self.__get_object_type_by_id(collection_id)
        object_type = None
        if "objectType" in object_type_object:
            object_type = object_type_object["objectType"]

        if object_type == None:
            print("object type cannot find for collection id")
            return {
                "isSuccess": False,
                "error": "object type cannot find for collection id",
            }
        if object_type == ObjectType.IMAGE_COLLECTION.value:
            item_type_enum = ObjectType.IMAGE.value
        elif object_type == ObjectType.VIDEO_COLLECTION.value:
            item_type_enum = ObjectType.VIDEO.value
        elif object_type == ObjectType.OTHER_COLLECTION.value:
            item_type_enum = ObjectType.OTHER.value
        else:
            return {
                "isSuccess": False,
                "error": "collection type is not acceptable get item list",
            }

        filter = self.__create_filter(filter)
        # filter["contentType"] = item_type_enum
        sort_filter = self.__create_sort_filter(sort_order)

        return _datalake_client.get_item_list_from_collection(
            item_type_enum,
            collection_id,
            query,
            filter,
            page_index,
            page_size,
            sort_filter,
        )

    """
    get item count from collection in datalake
    @collection_id: id of the collection
    @query: datalake query
    @filter: {date: {fromDate: "", toDate: ""},  "annotation_types": ["human", "raw", "machine"]}
    """

    def get_item_count_from_collection(
        self,
        collection_id,
        query: str = "",
        filter={},
    ):

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        item_type_enum = 2
        if collection_id == None or collection_id == "":
            return {"isSuccess": False, "error": "collection id must be provided"}

        object_type_object = self.__get_object_type_by_id(collection_id)
        object_type = None
        if "objectType" in object_type_object:
            object_type = object_type_object["objectType"]

        if object_type == None:
            print("object type cannot find for collection id")
            return {
                "isSuccess": False,
                "error": "object type cannot find for collection id",
            }
        if object_type == ObjectType.IMAGE_COLLECTION.value:
            item_type_enum = ObjectType.IMAGE.value
        elif object_type == ObjectType.VIDEO_COLLECTION.value:
            item_type_enum = ObjectType.VIDEO.value
        elif object_type == ObjectType.OTHER_COLLECTION.value:
            item_type_enum = ObjectType.OTHER.value
        elif object_type == ObjectType.DATASET.value:
            item_type_enum = ObjectType.IMAGE.value
        else:
            return {
                "isSuccess": False,
                "error": "collection type is not acceptable get item list",
            }

        filter = self.__create_filter(filter)
        # filter["contentType"] = item_type_enum

        return _datalake_client.get_item_count_from_collection(
            item_type_enum,
            collection_id,
            query,
            filter,
        )

    """
    Use for insert embedding list to images
    @embedding_list - [
        {
            "uniqueName": "example_collection_example_image.jpg",
            "embeddings": [0.23,0.56,....]
        },
        {
            "uniqueName": "example_collection_example_image.jpg",
            "embeddings": [0.23,0.56,....]
        },.......
    ]
    uniqueName string length limit 256 characters
    embedding vector dimension limit 2048
    """

    def insert_image_embeddings_batch(
        self,
        embedding_list: List[Dict[str, List[float]]],
        model_name: str,
        vector_dimension: List[int],
        session_id: str = "",
    ):
        if embedding_list == None:
            return {"success": False, "message": "embedding_list is None"}
        if type(embedding_list) != list:
            return {"success": False, "message": "embedding_list is not a list"}
        if len(embedding_list) > 100:
            return {
                "success": False,
                "message": "embedding_list length is more than 100",
            }

        def is_embedding_dict(embedding_obj: dict) -> dict:
            return (
                isinstance(embedding_obj, dict)
                and "embeddings" in embedding_obj
                and isinstance(embedding_obj["embeddings"], list)
                and "uniqueName" in embedding_obj
                and isinstance(embedding_obj["uniqueName"], str)
            )

        if not all(is_embedding_dict(d) for d in embedding_list):
            return {"success": False, "message": "embedding_list doesn't follow format"}

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        return _datalake_client.insert_embeddings_batch(
            embedding_list, model_name, vector_dimension, session_id
        )

    """
    Use for insert embedding list to images
    @embedding_list - [
        {
            "uniqueName": "example_collection_example_image.jpg",
            "embeddings": [0.23,0.56,....]
        },
        {
            "uniqueName": "example_collection_example_image.jpg",
            "embeddings": [0.23,0.56,....]
        },.......
    ]
    uniqueName string length limit 256 characters
    embedding vector dimension limit 2048
    """

    def insert_image_embeddings(
        self,
        embedding_list: List[Dict[str, List[float]]],
        model_name: str,
        vector_dimension: List[int],
    ) -> dict:

        total_count = len(embedding_list)
        session_uuid = str(datetime.datetime.now().timestamp())
        job_name = f"Embedding-upload-{model_name}"
        if embedding_list == None:
            return {"success": False, "message": "embedding_list is None"}
        if type(embedding_list) != list:
            return {"success": False, "message": "embedding_list is not a list"}

        self.create_or_update_job(
            session_uuid,
            job_name,
            JobType.UPLOAD_EMBEDDING.value,
            0,
            JobStatus.QUEUED.value,
            {"modelName": model_name, "embeddingUploadTotalCount": total_count},
        )

        count = 0
        continues_count = 0
        object_key_list = []
        temp_embedding_list = []
        status = JobStatus.IN_PROGRESS.value
        inserted_count = 0
        message_list = []
        for embedding in embedding_list:
            continues_count += 1
            if count == len(embedding_list) - 1:

                temp_embedding_list.append(embedding)
                if "uniqueName" in embedding and isinstance(
                    embedding["uniqueName"], str
                ):
                    object_key_list.append(embedding["uniqueName"])
                else:
                    self.create_or_update_job(
                        session_uuid,
                        job_name,
                        JobType.UPLOAD_EMBEDDING.value,
                        0,
                        JobStatus.FAILED.value,
                        {"errorList": f"Invalid embedding object: {embedding}"},
                    )
                    return {"success": False}

                response = self.insert_image_embeddings_batch(
                    temp_embedding_list, model_name, vector_dimension
                )
                if response["message"] != "":
                    message_list.append(response["message"])
                if response["success"] == False:
                    self.create_or_update_job(
                        session_uuid,
                        job_name,
                        JobType.UPLOAD_EMBEDDING.value,
                        0,
                        JobStatus.FAILED.value,
                        {
                            "embeddingUploadFailedObjectKeys": object_key_list,
                            "errorList": "Error occur while uploading embeddings",
                        },
                    )
                    object_key_list = []
                    return response

                progress = (continues_count / total_count) * 100
                if progress == 100:
                    status = JobStatus.COMPLETED.value
                inserted_count += response["upsert_count"]
                self.create_or_update_job(
                    session_uuid,
                    job_name,
                    JobType.UPLOAD_EMBEDDING.value,
                    progress,
                    status,
                    {
                        "embeddingUploadTryObjectKeys": object_key_list,
                        "embeddingUploadSuccessCount": inserted_count,
                    },
                )
                object_key_list = []
                return {
                    "success": True,
                    "upsert_count": inserted_count,
                    "message": message_list,
                }
            elif count % 100 == 0 and count != 0:
                response = self.insert_image_embeddings_batch(
                    temp_embedding_list, model_name, vector_dimension
                )
                if response["message"] != "":
                    message_list.append(response["message"])
                if response["success"] == False:
                    self.create_or_update_job(
                        session_uuid,
                        job_name,
                        JobType.UPLOAD_EMBEDDING.value,
                        0,
                        JobStatus.FAILED.value,
                        {
                            "embeddingUploadFailedObjectKeys": object_key_list,
                            "errorList": "Error occur while uploading embeddings",
                        },
                    )
                    object_key_list = []
                    return response

                progress = (continues_count / total_count) * 100
                if progress == 100:
                    status = JobStatus.COMPLETED.value
                inserted_count += response["upsert_count"]
                self.create_or_update_job(
                    session_uuid,
                    job_name,
                    JobType.UPLOAD_EMBEDDING.value,
                    progress,
                    status,
                    {
                        "embeddingUploadTryObjectKeys": object_key_list,
                        "embeddingUploadSuccessCount": inserted_count,
                    },
                )
                object_key_list = []
                temp_embedding_list = []
            else:
                temp_embedding_list.append(embedding)
                if "uniqueName" in embedding and isinstance(
                    embedding["uniqueName"], str
                ):
                    object_key_list.append(embedding["uniqueName"])
                else:
                    self.create_or_update_job(
                        session_uuid,
                        job_name,
                        JobType.UPLOAD_EMBEDDING.value,
                        0,
                        JobStatus.FAILED.value,
                        {"errorList": f"Invalid embedding object: {embedding}"},
                    )
                    return {"success": False}
            count += 1

        progress = (continues_count / total_count) * 100
        if progress == 100:
            status = JobStatus.COMPLETED.value
        self.create_or_update_job(
            session_uuid,
            job_name,
            JobType.UPLOAD_EMBEDDING.value,
            progress,
            status,
            {
                "embeddingUploadTryObjectKeys": object_key_list,
                "embeddingUploadSuccessCount": inserted_count,
            },
        )
        object_key_list = []
        return {
            "success": True,
            "upsert_count": inserted_count,
            "message": message_list,
        }

    # def create_embedding_collection(self, model_name, vector_dimension, index_type = None):
    #     _datalake_client = datalake.DatalakeClient(
    #         self.encoded_key_secret, self.layernext_url)

    #     return _datalake_client.create_embedding_collection(model_name, vector_dimension, index_type)

    """
    Use for get the embedding vector
    @unique_name:  string - unique name of the required embeddings
    @model_name: string - model name of the required embeddings
    """

    def get_embedding_vector(
        self, unique_names: List[str], model_name: str
    ) -> Union[List[dict], dict]:

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        return _datalake_client.get_embedding_vector(unique_names, model_name)

    """ 
    Use to create or update job in metalake
    @session_id :  string - session id
    @job_name   :  string - job name 
    @job_type   :  enum   - type of job (enum)
    @progress   :  int    - progress of created or update job
    @status     :  enum   - complete, in_progress.. (enum)
    @job_detail :  dict   - job specific details
    """

    def create_or_update_job(
        self,
        session_id: str,
        job_name: str,
        job_type: int,
        progress: int,
        status: int,
        job_detail: dict = {},
    ):

        if (
            not isinstance(session_id, str)
            or not isinstance(job_name, str)
            or not isinstance(progress, (int, float))
            or not isinstance(JobStatus(status), JobStatus)
            or not isinstance(JobType(job_type), JobType)
        ):
            print("Invalid input field. Please check and retry")
            raise Exception(
                "Cannot create or update job. Invalid input field. Please check and retry"
            )

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        return _datalake_client.create_or_update_job(
            session_id, job_name, job_type, progress, status, job_detail
        )

    """
    Use to find documents matching for given keywords and categories
    @unique_name:  List[str] - unique name of the required embeddings
    @model_name: List[str] - model name of the required embeddings
    @page_index: int - index of the page
    @page_size: int - size of the page, maximum = 1000
    """

    def find_documents(
        self,
        keywords: List[str],
        categories: List[str],
        page_index=0,
        page_size=3,
        request_id=uuid.uuid4(),
        chat_id="",
    ):
        return self.get_item_list_from_datalake_llm(
            item_type="other",
            filter={"keywords": keywords, "categories": categories},
            page_index=page_index,
            page_size=page_size,
            sort_order={"sort_by_field": "text_score", "sort_order": "DESC"},
            request_id=request_id,
            chat_id=chat_id,
        )

    def __prepare_doc_elements_list(
        self, filtered_doc_list: list, document_elem_dict: dict, chat_id: str
    ):
        """
        document_elem_dict -->

        {
            "uniqueName": {
                "rank": number,
                "element_list": []
            }
        }
        """
        output_list = []
        # Add chunk_list to each document in the filtered list
        for doc in filtered_doc_list:

            element_list_with_rank = document_elem_dict.get(doc["uniqueName"], {})
            element_list = element_list_with_rank.get("element_list", [])
            element_rank = element_list_with_rank.get("rank", float("inf"))

            # Get name and named entities if not exist for this doc
            if "namedEntities" not in doc:
                metadata_obj = self.get_file_details(
                    doc["uniqueName"], {"name": True, "namedEntities": True}, chat_id
                )
                if "name" in metadata_obj:
                    doc["name"] = metadata_obj["name"]
                if "namedEntities" in metadata_obj:
                    doc["namedEntities"] = metadata_obj["namedEntities"]

            output_list.append(
                {
                    "name": doc.get("name", ""),
                    "unique_name": doc.get("uniqueName", ""),
                    "url": doc.get("url", ""),
                    "title": doc.get("documentTitle", ""),
                    "named_entities": doc.get("namedEntities", ""),
                    "elements": element_list,
                    "rank": element_rank,
                    "file_type": doc.get("fileType", ""),
                }
            )

        sorted_data = sorted(output_list, key=lambda item: item["rank"])
        # Remove the 'rank' key from each dictionary
        for _item in sorted_data:
            del _item["rank"]

        return sorted_data

    def query_documents_with_structure(
        self,
        original_question: str,
        document_categories: List[str],
        document_keywords: List[str],
        user_question: str,
        chat_id,
        page_index=0,
        page_size=10,
    ):
        """
        Do keyword and category based search for matching documents in MetaLake using document-wise metadata
        Parameters:
            document_categories: List of categories in MetaLake to search
            document_keywords: List of keywords
            user_question: Question asked
            page_size: How many documents to find
        Returns:
            List of dictionaries for each matched document. Each dictionary contains document metadata and matched elements
        """
        request_id = uuid.uuid4()
        logger.info(
            f" sdk | query_documents_with_structure | request_id >>>> {request_id}, document_categories:{document_categories}, document_search_keys:{document_keywords}, question:{user_question}, page_index:{page_index}, page_size:{page_size}"
        )

        doc_list = self.find_documents(
            keywords=document_keywords,
            categories=document_categories,
            page_index=page_index,
            page_size=page_size,
            request_id=request_id,
            chat_id=chat_id,
        )

        filtered_doc_list = []

        # filter docs based on text score
        if (
            doc_list and isinstance(doc_list, list) and len(doc_list) > 0
        ):  # Check if the list is not empty and get the score of the first document
            if (
                document_keywords
                and isinstance(document_keywords, list)
                and len(document_keywords) > 0
            ):  # score exists only if document_search_keys available to do text search
                if page_index == 0:
                    first_doc_score = doc_list[0]["score"]
                else:
                    first_doc_list = self.find_documents(
                        keywords=document_keywords,
                        categories=document_categories,
                        page_index=0,
                        page_size=1,
                        request_id=request_id,
                        chat_id=chat_id,
                    )
                    first_doc_score = first_doc_list[0]["score"]

                filtered_doc_list = [
                    doc for doc in doc_list if doc["score"] > 0.25 * first_doc_score
                ]
            else:
                filtered_doc_list = doc_list

        # Extract uniqueNames from the filtered list
        # unique_names = [doc["uniqueName"] for doc in filtered_doc_list]
        unique_names = [doc["uniqueName"] for doc in filtered_doc_list]

        document_element_dict = self.find_elements(
            unique_name_list=unique_names,
            original_question=original_question,
            user_question=user_question,
            chat_id=chat_id,
        )

        output_list = self.__prepare_doc_elements_list(
            filtered_doc_list, document_element_dict, chat_id
        )
        logger.info(
            f" sdk | query_documents_with_structure | request_id <<<< {request_id}, response: {output_list}"
        )
        return output_list

    def get_documents_with_structure(
        self, doc_unique_name_list: list, user_question: str, chat_id: str
    ):
        """
        For given set of documents (identified by object keys), find matching elements for user's question
        This should be called when target documents are available (in case of uploads)
        Parameters:
            doc_unique_name_list: List of document object keys
            user_question: Question asked
        Returns:
            List of dictionaries for each matched document. Each dictionary contains document metadata and matched elements
        """
        request_id = uuid.uuid4()
        logger.info(
            f" sdk | get_documents_with_structure | request_id >>>> {request_id}, document unique name list:{doc_unique_name_list}, question:{user_question}"
        )
        # Get required metadata (name, named entities ) for

        document_element_dict = self.find_elements(
            unique_name_list=doc_unique_name_list,
            original_question="",
            user_question=user_question,
            chat_id=chat_id,
            is_target_documents_available=True,
        )
        # Convert to a list of dictionaries
        filtered_doc_list = [{"uniqueName": name} for name in doc_unique_name_list]
        output_list = self.__prepare_doc_elements_list(
            filtered_doc_list, document_element_dict, chat_id
        )
        logger.info(
            f" sdk | get_documents_with_structure | request_id <<<< {request_id}, response: {output_list}"
        )
        return output_list

    def retrieve_documents(
        self,
        document_categories: List[str],
        document_search_keys: List[str],
        chunk_search_keys: List[str],
        page_index=0,
        page_size=10,
    ):
        """
        Retrieves a list of documents filtered by specified categories and search keys, along with related document chunks.

        This function performs a two-step retrieval and filtering process. First, it finds documents based on given search
        keywords and categories. It then filters these documents based on a scoring threshold, which is determined by the
        score of the first document in the list (or the first page, if pagination is used). This score is only relevant if
        document search keys are provided. In the second step, the function retrieves chunks of information related to
        these documents based on the provided chunk search keys.

        Parameters:
        - document_categories (List[str]): A list of categories used to filter the documents.
        - document_search_keys (List[str]): A list of keywords for searching documents.
        - chunk_search_keys (List[str]): A list of keys for retrieving specific chunks from the documents.
        - page_index (int, optional): The page index for pagination purposes. Defaults to 0.
        - page_size (int, optional): The number of documents to retrieve per page. Defaults to 10.

        Returns:
        - List[Dict]: A list of filtered documents, each augmented with a list of relevant chunks and without the 'score' field.
        """
        request_id = uuid.uuid4()
        logger.info(
            f" sdk | retrieve_documents | request_id >>>> {request_id}, document_categories:{document_categories}, document_search_keys:{document_search_keys}, chunk_search_keys:{chunk_search_keys}, page_index:{page_index}, page_size:{page_size}"
        )

        doc_list = self.find_documents(
            keywords=document_search_keys,
            categories=document_categories,
            page_index=page_index,
            page_size=page_size,
            request_id=request_id,
        )

        filtered_doc_list = []

        # filter docs based on text score
        if (
            doc_list and isinstance(doc_list, list) and len(doc_list) > 0
        ):  # Check if the list is not empty and get the score of the first document
            if (
                document_search_keys
                and isinstance(document_search_keys, list)
                and len(document_search_keys) > 0
            ):  # score exists only if document_search_keys available to do text search
                if page_index == 0:
                    first_doc_score = doc_list[0]["score"]
                else:
                    first_doc_list = self.find_documents(
                        keywords=document_search_keys,
                        categories=document_categories,
                        page_index=0,
                        page_size=1,
                        request_id=request_id,
                    )
                    first_doc_score = first_doc_list[0]["score"]

                filtered_doc_list = [
                    doc for doc in doc_list if doc["score"] > 0.25 * first_doc_score
                ]
            else:
                filtered_doc_list = doc_list

        # Extract uniqueNames from the filtered list
        # unique_names = [doc["uniqueName"] for doc in filtered_doc_list]
        unique_names = [
            doc["uniqueName"]
            for doc in filtered_doc_list
            if doc["uniqueName"].endswith(".pdf")
        ]

        chunk_dict = self.find_document_chunks(
            search_key_list=chunk_search_keys, unique_name_list=unique_names
        )

        chunk_list = []
        # Add chunk_list to each document in the filtered list
        for doc in filtered_doc_list:
            doc_chunk_list = chunk_dict.get(doc["uniqueName"], [])

            chunk_list.append(
                {
                    "name": doc.get("name", ""),
                    "unique_name": doc.get("uniqueName", ""),
                    "url": doc.get("url", ""),
                    "title": doc.get("documentTitle", ""),
                    "named_entities": doc.get("namedEntities", ""),
                    "chunk_list": doc_chunk_list,
                    "file_type": doc.get("fileType", ""),
                }
            )
        logger.info(
            f" sdk | retrieve_documents | request_id <<<< {request_id},  response: {chunk_list}"
        )
        return chunk_list

    def extract_document_elements_keyInfo(
        self,
        document_elements_dict: dict,
        extraction_keys: List[dict],
        user_question: str,
        chat_id: str,
    ):
        """
        Extracts the contents from a document for user's question and return the result according to extraction keys given
        """
        request_id = uuid.uuid4()
        logger.info(
            f" sdk | retrieve_documents | request_id >>>> {request_id}, document_elements_dict:{document_elements_dict}, extraction_keys:{extraction_keys}, chat_id: {chat_id}"
        )

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        response = _datalake_client.extract_doc_content(
            document_elements_dict, extraction_keys, user_question, chat_id
        )

        logger.info(
            f" sdk | retrieve_documents_with_structure | request_id <<<< {request_id}, response: {response}"
        )
        return response

    def retrieve_text_chunks(
        self, document_list: List[str], chunk_search_keys: List[str]
    ):
        """
        Retrieves a list of documents details and related document chunks for search keys.

        Parameters:
        - document_list (List[str]): A list of unique names of documents.
        - chunk_search_keys (List[str]): A list of keys for retrieving specific chunks from the documents.

        Returns:
        - List[Dict]: A list of filtered documents, each augmented with a list of relevant chunks.
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        unique_names = [
            unique_name for unique_name in document_list if unique_name.endswith(".pdf")
        ]

        chunk_dict = self.find_document_chunks(
            search_key_list=chunk_search_keys, unique_name_list=unique_names
        )

        chunk_list = []
        # Add chunk_list to each document in the filtered list
        for doc in document_list:
            doc_chunk_list = chunk_dict.get(doc, [])
            fields = [
                "objectKey",
                "name",
                "url",
                "fileTitle",
                "namedEntities",
                "fileType",
            ]
            doc_details = _datalake_client.get_metadata_details(doc, fields)
            if doc_details is None:
                doc_details = {}
            chunk_list.append(
                {
                    "name": doc_details.get("name", ""),
                    "unique_name": doc,
                    "url": doc_details.get("url", ""),
                    "title": doc_details.get("fileTitle", ""),
                    "named_entities": doc_details.get("namedEntities", ""),
                    "chunk_list": doc_chunk_list,
                    "file_type": doc_details.get("fileType", ""),
                }
            )
        logger.info(f" sdk | retrieve_documents | response: {chunk_list}")
        return chunk_list

    """
    create or update virtual collection from search objects
    @param dataset_name - name of the dataset
    @param collection_id - collection_id for search objects
    @param query - query for search objects
    @param filter - filter for filter objects - {
        "annotation_types": ["human", "raw", "machine"],
        "from_date": "", "to_date": ""
    }
    @param object_type - object_type for search objects
    @param object_list - object_list for search objects
    """

    def update_virtual_collection(
        self,
        virtual_collection_name: str = None,
        virtual_collection_id: str = None,
        collection_id: str = None,
        query: str = "",
        filter={},
        object_type="image",
        object_list=[],
        is_all_selected=True,
    ):
        print(
            f"create or update virtual collection - name: {virtual_collection_name}, id: {virtual_collection_id}"
        )

        if virtual_collection_name == None and virtual_collection_id == None:
            return {
                "is_success": False,
                "error": "Invalid virtual collection name and id",
            }
        if object_type.lower() == "image":
            object_type = ObjectType.IMAGE.value
        elif object_type.lower() == "image_collection":
            object_type = ObjectType.IMAGE_COLLECTION.value
        elif object_type.lower() == "video":
            object_type = ObjectType.VIDEO.value
        elif object_type.lower() == "video_collection":
            object_type = ObjectType.VIDEO_COLLECTION.value
        elif object_type.lower() == "other":
            object_type = ObjectType.OTHER.value
        elif object_type.lower() == "other_collection":
            object_type = ObjectType.OTHER_COLLECTION.value
        else:
            return {"is_success": False, "error": "Invalid object type"}

        filter = self.__create_filter(filter)

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        response = _datalake_client.get_selection_id(
            collection_id, query, filter, object_type, object_list, is_all_selected
        )
        print("selection id: ", response)
        get_selection_id_success = True
        if "isSuccess" in response:
            if response["isSuccess"] == False:
                get_selection_id_success = False
        if get_selection_id_success == True:
            v_collection_response = _datalake_client.update_virtual_collection(
                virtual_collection_name, virtual_collection_id, response["selectionTag"]
            )
            print("v_collection_response: ", v_collection_response)
            return v_collection_response
        else:
            print("v_collection_response: ", {"isSuccess": False})
            return {"isSuccess": False, "error": "Failed to get selection id"}

    def find_elements(
        self,
        unique_name_list: List[str],
        original_question: str,
        user_question: str,
        chat_id: str,
        is_target_documents_available: bool = False,
    ):
        """
        Find elements of documents given with unique names (object keys) according to the user question
        Parameters:
            unique_name_list: List of document object keys that need to find from
            original_question: actual question asked by user
            user_question: query sent by LLM in the single code
            is_target_documents_available: True if target documents are already known (in case of uploading), False if documents were found by keyword match
        Returns: List of dictionaries
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        response = _datalake_client.find_elements_from_docs(
            unique_name_list,
            original_question,
            user_question,
            is_target_documents_available,
            chat_id,
        )

        return response

    def get_data_dictionary_with_overview_data(self):
        """
        Retrieve the data dictionary with overview data.
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        response = _datalake_client.get_data_dictionary_with_overview_data()
        return response

    def get_data_dictionary_modified_timestamp(self):
        """
        Returns the latest timestamp that any change in data dictionary occurred
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        response = _datalake_client.get_data_dictionary_modfied_timestamp()
        return response

    def find_chunk(
        self,
        search_key_list: List[str],
        unique_name_list: List[str],
        page_index: int = 0,
        response_chunk_limit: int = 3,
        adjacent_chunk_limit: int = 1,
    ):
        """
        find chunk by search keys from text
        @param search_key_list - list of search keys
        @param unique_name_list - list of unique names
        @param response_chunk_limit - limit of the chunks searching
        @param adjacent_chunk_limit - how many adjacent chunks for each chunk returning (if 2 then return 5 chunks for each chunk with 2 adjacent chunks from each side with main chunk)
        return array of chunks
        example search_key_list - ["tax", "discount"]
        example unique_name_list - ["abc.pdf", "def.pdf"]
        example response_chunk_limit - 3
        example adjacent_chunk_limit - 0
        example response - [
            '# 000009752 Description Date Credited Amount Deposit Ref Nbr: 130012345 05-15 $3,615.08 Total Deposits & Other Credits $3,615.08 ATM Withdrawals & Debits Account # 000009752 Description Tran Date Date Paid Amount ATM',
            'Debits $20.00 ChecksPaid Account # 000009752 Date Paid Check Number Amount Reference Number 05-12 1001 75.00 00012576589 05-18 1002 30.00 00036547854 05-24 1003 200.00 00094613547 Total Checks Paid',
            'Purchases & Debits -0.00 Withdrawals & Other Debits -0.00 Checks Paid -200.00 Ending Balance on June 5, 2003 $10,521.19 Deposits & Other Credits Account # 000009752 Description Date Credited Amount Deposit Ref'
        ]
        """

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        response = _datalake_client.find_chunk(
            search_key_list,
            unique_name_list,
            page_index,
            response_chunk_limit,
            adjacent_chunk_limit,
        )

        return response

    def find_document_chunks(
        self,
        search_key_list: List[str],
        unique_name_list: List[str],
    ):
        """
        find chunk by search keys from each pdf file
        @param search_key_list - list of search keys
        @param unique_name_list - list of unique names
        return file dict with chunks
        example search_key_list - ["tax", "discount"]
        example unique_name_list - ["abc.pdf", "def.pdf"]
        example response - {
            "abc.pdf": [
            '# 000009752 Description Date Credited Amount Deposit Ref Nbr: 130012345 05-15 $3,615.08 Total Deposits & Other Credits $3,615.08 ATM Withdrawals & Debits Account # 000009752 Description Tran Date Date Paid Amount ATM',
            'Debits $20.00 ChecksPaid Account # 000009752 Date Paid Check Number Amount Reference Number 05-12 1001 75.00 00012576589 05-18 1002 30.00 00036547854 05-24 1003 200.00 00094613547 Total Checks Paid',
            'Purchases & Debits -0.00 Withdrawals & Other Debits -0.00 Checks Paid -200.00 Ending Balance on June 5, 2003 $10,521.19 Deposits & Other Credits Account # 000009752 Description Date Credited Amount Deposit Ref'
            ],
            "def.pdf": []
        }
        """

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        response = _datalake_client.find_chunk_from_each_doc(
            search_key_list, unique_name_list
        )

        return response

    """ 
    Use to get data dictionary
    """

    def get_data_dictionary(self):
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        return _datalake_client.get_data_dictionary()

    def execute_mongo_query(
        self,
        source_name: str,
        function,
        input_data,
        collection,
        request_id=uuid.uuid4(),
    ):
        """
        Use to execute mongo db query
        @function     :  This can be 'aggregate', 'find', 'updateMany', etc.
        @input_data   :  The input parameters for the MongoDB function, provided as a JSON-like dictionary or list
        @collection   :  The name of the MongoDB collection on which the query is to be run
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        return _datalake_client.execute_mongo_query(
            source_name, function, input_data, collection, request_id
        )

    def run_mongodb_aggregation(self, source_name: str, pipeline_stages, collection):
        """
        Execute an aggregation query on a specified MongoDB collection.

        This function takes a MongoDB aggregation pipeline and a collection name,
        then runs the aggregation query on the specified collection. The result of
        the aggregation is returned.

        Parameters:
        pipeline_stages (list of dict): The MongoDB aggregation pipeline. This should be a list
                                   of dictionaries, where each dictionary represents a stage
                                   in the aggregation pipeline.
        collection (str): The name of the MongoDB collection on which the aggregation
                          query is to be executed.

        Returns:
        list: The result of the aggregation query as a list. Each element in the list is
              a dictionary representing a document that matches the aggregation criteria.

        Example:
        result = run_mongodb_aggregation([
                    {"$match": {"status": "A"}},
                    {"$group": {"_id": "$cust_id", "total": {"$sum": "$amount"}}}
                 ], "transactions")
        """
        request_id = uuid.uuid4()
        logger.info(
            f" sdk | run_mongodb_aggregation | request_id >>>> {request_id}, source_name:{source_name}, pipeline_stages:{pipeline_stages}, collection:{collection}"
        )
        res = self.execute_mongo_query(
            source_name, "aggregate", pipeline_stages, collection, request_id
        )
        logger.info(
            f" sdk | run_mongodb_aggregation | request_id <<<< {request_id}, response: {res}"
        )
        return res

    def insert_mongodb_data(self, source_name: str, collection: str, data: list):
        """
        Insert data into a specified MongoDB collection.

        This function takes a list of documents and a collection name,
        then inserts the documents into the specified collection.

        Parameters:
        data (list of dict): The documents to be inserted. Each dictionary represents a document.
        collection (str): The name of the MongoDB collection where the documents should be inserted.

        Returns:
        dict: The result of the insertion operation, including details like acknowledged status and inserted IDs.

        Example:
        result = insert_mongodb_data("source_name", "LN_ForecastedDailyCompletedJobs", [
                    {"date": "2024-08-01", "count": 15},
                    {"date": "2024-08-02", "count": 20}
                ])
        """
        request_id = uuid.uuid4()
        logger.info(
            f" sdk | insert_mongodb_data | request_id >>>> {request_id}, source_name:{source_name}, collection:{collection}, data:{data}"
        )
        res = self.execute_mongo_insert(source_name, collection, data, request_id)
        logger.info(
            f" sdk | insert_mongodb_data | request_id <<<< {request_id}, response: {res}"
        )
        return res

    def execute_mongo_insert(
        self,
        source_name: str,
        collection: str,
        data: list,
        request_id=uuid.uuid4(),
    ):
        """
        Use to execute mongo db insert operation
        @data        :  The data (list of documents) to be inserted into the MongoDB collection
        @collection  :  The name of the MongoDB collection where the documents should be inserted
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        return _datalake_client.insert_mongo_data(
            source_name, collection, data, request_id
        )

    def delete_mongodb_data(self, source_name: str, collection: str, filter_obj: dict):
        """
        Delete data from a specified MongoDB collection.

        This function takes a filter object and a collection name,
        then deletes the documents matching the filter criteria from the specified collection.

        Parameters:
        filter_obj (dict): The filter criteria to identify the documents to delete.
        collection (str): The name of the MongoDB collection where the deletion should occur.

        Returns:
        dict: The result of the deletion operation, including details like acknowledged status and deleted count.

        Example:
        result = delete_mongodb_data("source_name", "LN_ForecastedDailyCompletedJobs", {"date": "2024-08-01"})
        """
        request_id = uuid.uuid4()
        logger.info(
            f" sdk | delete_mongodb_data | request_id >>>> {request_id}, source_name:{source_name}, collection:{collection}, filter_obj:{filter_obj}"
        )
        res = self.execute_mongo_delete(source_name, collection, filter_obj, request_id)
        logger.info(
            f" sdk | delete_mongodb_data | request_id <<<< {request_id}, response: {res}"
        )
        return res

    def execute_mongo_delete(
        self,
        source_name: str,
        collection: str,
        filter_obj: dict,
        request_id=uuid.uuid4(),
    ):
        """
        Use to execute mongo db delete operation
        @filter_obj   :  The filter criteria to identify the documents to delete
        @collection   :  The name of the MongoDB collection where the deletion should occur
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        return _datalake_client.delete_mongo_data(
            source_name, collection, filter_obj, request_id
        )

    def run_sql_query(self, source_name: str, query: str):
        """
        Use to execute sql db query
        @source_name     :  source name you used to create the sql db connection with metalake
        @query   :  SQL query to execute
        """
        request_id = uuid.uuid4()
        logger.info(
            f" sdk | run_sql_query | request_id >>>> {request_id}, source_name:{source_name}, query:{query}"
        )
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        res = _datalake_client.run_sql_query(source_name, query, request_id)
        logger.info(
            f" sdk | run_sql_query | request_id <<<< {request_id}, response: {res}"
        )
        return res

    def get_source_list(self, source_list: List[str]) -> List[str]:
        """
        Get connection source and their types
        @source_list: get source list

        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        return _datalake_client.get_source_list(source_list)

    def retrieve_db_unstructured_records(
        self, categories=[], filter_key_values={}, page_index=0
    ):
        """
        categories (list): Category names relevant to each section of data being considered for locating records.

        filter_key_values (dictionary): Key value pairs derived from the question to locate matching records.
        Note that the values in key information should be provided as list in below format
        { "key_1": [<value_1>, <value_2>, ...], "key_2": [<value_1>, <value_2>, ...]}
        Example:{ "id": [1101, 1302, 1435], "type": ["retail"]}

        page_index (int): Index for the batch required.

        Behavior:

        Returns: a list of dictionaries, where each dictionary contains key information as a dictionary and the unstructured data as list of strings.
                [
                    {
                    "keyInfo": {
                        "key_1": <value_1>,
                        "key_2": <value_2>
                    }
                    "data": ["data_1", "data_2", ....]
                    }
                ]
        Example usage: retrieve_documents(["reviews"], {
                "id": [1101, 1302, 1435],
                "type": ["retail"]
            }, 0)
        """

        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )

        return _datalake_client.retrieve_db_unstructured_records(
            categories, filter_key_values, page_index
        )

    def get_table_schema(self, source_name: str, table_name: str):
        """
        Fetches the schema for a specific table from a data source.

        :param source_name: The name of the data source.
        :param table_name: The name of the table.
        :return: The table schema including fields and descriptions.
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        response = _datalake_client.get_table_schema(source_name, table_name)
        return response

    def submit_user_feedback(
        self, user_question: str, ai_answer: str, feedback_comment: str
    ):
        """
        Flow the feedback given for the AI answer to the datalake to run the auto tuneup process
        Parameters:
            user_question: Original User question
            ai_answer: Latest answer given by LLM
            feedback_comment: Feedback comment given by user with @feedback prompt
        Returns: Acknowledgement status in the MetaLake
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        response = _datalake_client.submit_user_feedback(
            user_question, ai_answer, feedback_comment
        )
        return response

    def retrieve_suggested_questions(self):
        """
        Retrieves a list of suggested questions from the MetaLake

        Returns:
            List of suggested questions
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        response = _datalake_client.retrieve_suggested_questions()
        return response

    def get_datasource_metadata(self, connection_id: str):
        """
        Retrieves the metadata for a specific data source.

        Parameters:
            connection_id (str): The connection ID of the data source.

        Returns:
            dict: The metadata for the specified data source.
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        response = _datalake_client.get_datasource_metadata(connection_id)
        return response

    def add_knowledge_blocks(self, data: dict):
        """
        Add knowledge blocks to the datalake
        @data: dict
        {
            "knowledge_blocks": [],
            "knowledge_tree": {}
        }
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        response = _datalake_client.add_knowledge_blocks(data)
        return response

    def quickbooks_get_auth_uri(self) -> str:
        """
        Get QuickBooks authorization URI for OAuth flow

        Returns:
            str: The QuickBooks authorization URI
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        response = _datalake_client.quickbooks_get_auth_uri()
        return response

    def quickbooks_create_or_update_object(self, api_name: str, data: dict):
        """
        Create or update QuickBooks object
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        response = _datalake_client.quickbooks_create_or_update_object(api_name, data)
        return response

    def quickbooks_upload_attachment(
        self, chat_id: str, file_name: str, object_type: str, object_id: str
    ):
        """
        Upload attachment to QuickBooks object
        """
        _datalake_client = datalake.DatalakeClient(
            self.encoded_key_secret, self.layernext_url
        )
        file_path = "storage/public/" + chat_id + "/attachments/" + file_name
        response = _datalake_client.quickbooks_upload_attachment(
            file_path, object_type, object_id
        )
        return response
