import json
import re
import time
import uuid
from typing import List, Union
from layernext.datalake.annotation import Annotation
from layernext.datalake.metadata import Metadata
from layernext.datalake.query import Query

from .ground_truth import GroundTruth
from .constants import (
    AnnotationUploadType,
    JobType,
    MediaType,
    JobStatus,
    ObjectType,
    AnnotationShapeType,
)
from .datalakeinterface import DatalakeInterface
from .file_upload import FileUpload
from .file_trash import FileTrash
from .label import Label
from .logger import get_debug_logger
from .model_run import ModelRun
from .mongo_json_encoder import MongoJsonEncoder

datalake_logger = get_debug_logger("DatalakeClient")


class DatalakeClient:
    """
    Python SDK of Datalake
    """

    def __init__(self, encoded_key_secret: str, layernext_url: str) -> None:
        # _datalake_url = f"{layernext_url}/datalake"
        # _datalake_url = f"{layernext_url}:3000"
        _datalake_url = f"{layernext_url}"
        # _datalake_url = "https://localhost:3000"
        self.datalake_interface = DatalakeInterface(encoded_key_secret, _datalake_url)

    def check_sdk_version_compatibility(self, sdk_version: str):
        """
        check sdk version compatibility
        """

        if re.compile(r"^(\d+\.)+\d+$").match(sdk_version) is None:
            raise Exception("sdk_version is invalid format")

        if sdk_version is None or sdk_version == "":
            raise Exception("sdk_version is None")

        res = self.datalake_interface.check_sdk_version_compatibility(sdk_version)

        if res["isCompatible"] == False:
            raise Exception(res["message"])

    def upload_annotation_from_cocojson(self, file_path: str):
        """
        available soon
        """
        datalake_logger.debug(f"file_name={file_path}")
        _annotation = GroundTruth(client=self)
        _annotation.upload_coco(file_path)

    def upload_modelrun_from_json(
        self,
        unique_id: str,
        model_id: str,
        file_path: str,
        annotation_geometry: str,
        is_normalized: bool,
        version: str,
        bucket_name: str,
        upload_type: AnnotationUploadType,
    ):
        datalake_logger.debug(
            f"upload_modelrun_from_json file_path={file_path}, "
            f"annotation_geometry={annotation_geometry}"
        )
        _model = ModelRun(client=self)
        _model.upload_modelrun_json(
            unique_id,
            model_id,
            file_path,
            annotation_geometry,
            is_normalized,
            version,
            bucket_name,
            upload_type,
        )

    def upload_groundtruth_from_json(
        self,
        unique_id: str,
        operation_id: str,
        file_path: str,
        annotation_geometry: str,
        is_normalized: bool,
        version: str,
        bucket_name: str,
        upload_type: AnnotationUploadType,
    ):
        datalake_logger.debug(
            f"upload_groundtruth_from_json file_path={file_path}, "
            f"annotation_geometry={annotation_geometry}"
        )
        _groundTruth = GroundTruth(client=self)
        _groundTruth.upload_groundtruth_json(
            unique_id,
            operation_id,
            file_path,
            annotation_geometry,
            is_normalized,
            version,
            bucket_name,
            upload_type,
        )

    def file_upload(
        self,
        path: str,
        collection_type,
        collection_name,
        meta_data_object,
        meta_data_override,
        storage_prefix_path,
    ):
        _upload = FileUpload(client=self)
        upload_res = _upload.file_upload_initiate(
            path,
            collection_type,
            collection_name,
            meta_data_object,
            meta_data_override,
            storage_prefix_path,
        )
        return upload_res

    def get_upload_status(self, collection_name):
        _upload = FileUpload(client=self)
        return _upload.get_upload_status(collection_name)

    def remove_collection_annotations(self, collection_id: str, model_run_id: str):
        print(
            f"annotation delete of collection ={collection_id}",
            f"model id={model_run_id}",
        )
        _model = Annotation(client=self)
        return _model.remove_collection_annotations(collection_id, model_run_id)

    """
    get selection id for query, collection id, filter data
    """

    def get_selection_id(
        self,
        collection_id,
        query,
        filter,
        object_type,
        object_list,
        is_all_selected=True,
    ):
        _query = Query(client=self)
        response = _query.get_selection_id(
            collection_id, query, filter, object_type, object_list, is_all_selected
        )
        return response

    def get_object_type_by_id(self, object_id):
        response = self.datalake_interface.get_object_type_by_id(object_id)
        return response

    def get_system_labels(self, group_id=None):
        response = self.datalake_interface.get_all_label_list(group_id)
        return response

    def attach_labels_to_group(self, group_id, label_keys):
        if group_id == "" or len(label_keys) == 0:
            print("Label group id or label list is empty")
            return {"is_success": False}
        response = self.datalake_interface.add_labels_to_group(group_id, label_keys)
        return response

    def detach_labels_from_group(self, group_id, label_keys):
        if group_id == "" or len(label_keys) == 0:
            print("Label group id or label list is empty")
            return {"is_success": False}
        response = self.datalake_interface.remove_labels_from_group(
            group_id, label_keys
        )
        return response

    def get_all_label_groups(self):
        response = self.datalake_interface.get_all_group_list()
        return response

    def create_system_label(self, label_dict):
        _label_dict = Label.get_system_label_create_payload(label_dict)
        response = self.datalake_interface.create_system_label(_label_dict)
        if response is not None:
            response = {"label_reference": response["label"]}
        return response

    def create_label_group(self, group_name, label_keys):
        if group_name == "" or len(label_keys) == 0:
            print("Label group name or label list is empty")
            return None
        response = self.datalake_interface.create_label_group(group_name, label_keys)
        return response

    def wait_for_job_complete(self, job_id):
        print(f"Waiting until complete the job: {job_id}")
        while True:
            try:
                job_detils = self.datalake_interface.check_job_status(job_id)

                if job_detils["isSuccess"]:
                    job_status = job_detils["status"]
                    job_progress = job_detils["progress"]
                    print(f"Job progress: {job_progress:.2f}%")
                    if job_status == JobStatus.COMPLETED.value:
                        res = {"is_success": True, "job_status": "COMPLETED"}
                        print(res)
                        return res
                    elif job_status == JobStatus.FAILED.value:
                        res = {"is_success": True, "job_status": "COMPLETED"}
                        print(res)
                        return res
                    else:
                        time.sleep(30)
                else:
                    res = {"is_success": False, "job_status": "FAILED"}
                    print(res)
                    return res
            except Exception as e:
                print(f"An exception occurred: {format(e)}")
                res = {"is_success": False, "job_status": "FAILED"}
                print(res)
                return res

    """
    trash selection object
    """

    def trash_datalake_object(self, selection_id):
        _trash = FileTrash(client=self)
        return _trash.trash_files(selection_id)

    def get_file_download_url(self, file_key):
        return self.datalake_interface.get_file_download_url(file_key)

    """
    upload metadata by using json file
    """

    def upload_metadata_from_json(
        self, collection_id: str, file_path: str = None, json_data: dict = None
    ):
        _metadata = Metadata(client=self)
        response = _metadata.upload_metadata_json(
            file_path=file_path, json_data=json_data, collection_id=collection_id
        )
        # print(response.get("message"))
        return response

    """
    upload metadata by using json file with object keys
    @file_path: json file path
    """

    def upload_metadata_from_unique_name_json(
        self, file_path: str = None, json_data: dict = None
    ):
        _metadata = Metadata(client=self)
        response = _metadata.upload_metadata_json(
            file_path=file_path, json_data=json_data
        )
        # print(response.get("message"))
        return response

    """
    upload metadata by using json file with storage path
    @file_path: json file path
    @bucket_name: bucket name 
    """

    def upload_metadata_from_storage_path_json(
        self, file_path: str = None, json_data: dict = None, bucket_name: str = None
    ):
        _metadata = Metadata(client=self)
        if bucket_name == None or bucket_name == "":
            bucket_name = "DEFAULT"
        response = _metadata.upload_metadata_json(
            file_path=file_path, json_data=json_data, bucket_name=bucket_name
        )
        # print(response.get("message"))
        return response

    """
    upload metadata by using json file with job id
    @file_path: json file path
    @job_id: job id
    """

    def upload_metadata_from_job_id(
        self, job_id: str, file_path: str = None, json_data: dict = None
    ):
        _metadata = Metadata(client=self)
        if job_id == None or job_id == "":
            raise Exception("job_id is empty. Please provide valid job id")
        response = _metadata.upload_metadata_json(
            file_path=file_path, json_data=json_data, job_id=job_id
        )
        # print(response.get("message"))
        return response

    """
    upload metadata by using meta object
    """

    def upload_metadata_from_metaObject(
        self,
        collection_name: str,
        object_type: str,
        metadata_object: dict,
        is_apply_to_all_files: bool,
    ):
        _metadata = Metadata(client=self)
        response = _metadata.upload_metadata_object(
            collection_name, object_type, metadata_object, is_apply_to_all_files
        )
        print(response.get("message"))
        return response

    """
    get item list from datalake

    """

    def get_item_list_from_datalake(
        self,
        item_type_enum,
        query: str,
        filter={},
        page_index=0,
        page_size=20,
        sort_filter={},
    ):
        payload = {
            "pageIndex": page_index,
            "pageSize": page_size,
            "query": query,
            "filterData": filter,
            "contentType": item_type_enum,
            "sortBy": sort_filter,
        }
        item_list = self.datalake_interface.get_item_list_from_datalake(payload)

        return item_list

    def get_item_list_from_datalake_llm(
        self,
        item_type_enum,
        query: str,
        filter={},
        page_index=0,
        page_size=20,
        sort_filter={},
        request_id=uuid.uuid4(),
        chat_id="",
    ):
        payload = {
            "pageIndex": page_index,
            "pageSize": page_size,
            "query": query,
            "filterData": filter,
            "contentType": item_type_enum,
            "sortBy": sort_filter,
            "conversationId": chat_id,
        }
        item_list = self.datalake_interface.get_item_list_from_datalake_llm(
            payload, request_id
        )

        return item_list

    """
    get item count from metalake

    """

    def get_item_count_from_metalake(
        self,
        item_type_enum,
        query: str,
        filter={},
    ):
        payload = {
            "query": query,
            "filterData": filter,
            "contentType": item_type_enum,
            "sortBy": {},
        }
        item_list = self.datalake_interface.get_item_count_from_metalake(payload)

        return item_list

    """
    download files from datalake batch wise
    """

    def download_files_batch_wise(
        self,
        item_type_enum,
        query: str,
        data_filter: dict,
        page_index: int,
        page_size: int,
        custom_download_path: str,
        config: dict,
        sort_filter: dict = {},
        item_type: str = None,
    ) -> dict:
        return self.datalake_interface.download_files_batch_wise(
            item_type_enum,
            query,
            data_filter,
            page_index,
            page_size,
            custom_download_path,
            config,
            sort_filter,
            item_type,
        )

    """
    get item list from collection in datalake
    
    """

    def get_item_list_from_collection(
        self,
        item_type_enum,
        collection_id,
        query: str,
        filter={},
        page_index=0,
        page_size=20,
        sort_filter: dict = {},
    ):
        payload = {
            "" "pageIndex": page_index,
            "pageSize": page_size,
            "query": query,
            "filterData": filter,
            "contentType": item_type_enum,
            "sortBy": sort_filter,
        }
        item_list = self.datalake_interface.get_item_list_from_collection(
            payload, collection_id
        )

        return item_list

    """
    get item count from collection in datalake
    """

    def get_item_count_from_collection(
        self,
        item_type_enum,
        collection_id,
        query: str,
        filter={},
    ):
        payload = {
            "" "query": query,
            "filterData": filter,
            "contentType": item_type_enum,
            "sortBy": {},
        }
        item_count = self.datalake_interface.get_item_count_from_collection(
            payload, collection_id
        )

        return item_count

    """
    get metadata by using filter
    @param unique_name: unique file name
    @param filter: filter to get required meta data
    """

    def get_item_details(self, unique_name: str, filter: dict, chat_id: str):

        if unique_name == None or unique_name == "":
            raise Exception("unique_name is empty")

        if filter == None:
            filter = {}

        payload = {
            "uniqueFileName": unique_name,
            "requiredMetaObj": filter,
            "conversationId": chat_id,
        }

        res = self.datalake_interface.get_item_details(payload)

        if res["isSuccess"] == False:
            raise Exception(res["message"])
        else:
            return res["itemDetails"]

    """
    get metadata by using filter
    @param unique_file_name: unique file name
    @param filter: filter to get required meta data
    """

    def get_collection_details(self, collection_id: str, filter: dict):

        if collection_id == None or collection_id == "":
            raise Exception("collection_id is empty")

        if filter == None:
            filter = {}

        payload = {"collectionId": collection_id, "requiredMetaObj": filter}

        res = self.datalake_interface.get_collection_details(payload)

        if res["isSuccess"] == False:
            raise Exception(res["message"])
        else:
            return res["itemDetails"]

    """ 
    Use to get system data
    """

    def get_system_stat_count(self):

        res = self.datalake_interface.get_system_details()

        if res["isSuccess"] == False:
            raise Exception(res["message"])
        else:
            return res

    """
    get collection id by using collection name
    @param collection_name: collection name
    @param collection_type: collection type
    """

    def get_collection_id_by_name(
        self, collection_name: str, collection_type: MediaType
    ):
        if collection_name == None or collection_name == "":
            raise Exception("collection_name is empty")

        if collection_type == None or collection_type == "":
            raise Exception("collection_type is empty")

        payload = {"collectionName": collection_name, "objectType": collection_type}

        res = self.datalake_interface.get_collection_id_by_name(payload)

        if "isSuccess" in res and res["isSuccess"] == False:
            raise Exception(res["message"])
        else:
            return res["collectionId"]

    """
    use to create collection head
    @param collection_name: collection name
    @param collection_type: collection type
    @param custom_meta_object: custom meta object
    """

    def create_collection_head(
        self, collection_name: str, collection_type: MediaType, custom_meta_object: dict
    ):
        payload = {
            "collectionName": collection_name,
            "objectType": collection_type,
            "customMetaObject": custom_meta_object,
        }

        res = self.datalake_interface.create_collection_head(payload)

        if "isSuccess" in res and res["isSuccess"] == False:
            raise Exception(res["message"])
        else:
            return res

    def insert_embeddings_batch(
        self,
        batch_data: List[dict],
        model_name: str,
        vector_dimension: str,
        session_id: str = "",
    ) -> dict:
        # if embedding_model_name == None or embedding_model_name == "":
        #     raise Exception("embedding_model_name is empty")

        payload = {
            "embeddingModelName": model_name,
            "embeddingDimension": vector_dimension,
            "data": batch_data,
            "sessionId": session_id,
        }

        res = self.datalake_interface.insert_embeddings_batch(payload)

        return res

    def create_or_update_job(
        self,
        session_id: str,
        job_name: str,
        job_type: int,
        progress: int,
        status: int,
        job_detail: dict,
    ):

        payload = {
            "jobName": job_name,
            "sessionId": session_id,
            "jobType": job_type,
            "progress": progress,
            "status": status,
            "jobSpecificDetails": job_detail,
        }

        res = self.datalake_interface.create_or_update_job(payload)
        return res

    def create_embedding_collection(
        self, model_name, vector_dimension, index_type=None
    ):

        payload = {
            "embeddingModelName": model_name,
            "embeddingDimension": vector_dimension,
            "embeddingIndexType": index_type,
        }

        res = self.datalake_interface.create_embedding_collection(payload)

        return res

    """
    Use for get the embedding vector
    @unique_name:  string - unique name of the required embeddings
    @model_name: string - model name of the required embeddings
    """

    def get_embedding_vector(
        self, unique_names: List[str], model_name: str
    ) -> Union[List[dict], dict]:

        payload = {
            "embeddingUniqueNameArray": unique_names,
            "embeddingModelName": model_name,
        }

        res = self.datalake_interface.get_embedding_vector(payload)

        return res

    """
    update or create virtual collection
    """

    def update_virtual_collection(
        self,
        virtual_collection_name: str = None,
        virtual_collection_id: str = None,
        selection_id: str = None,
    ):
        payload = {
            # "virtualCollectionName": virtual_collection_name,
            # "virtualCollectionId": virtual_collection_id,
            "selectionId": selection_id
        }
        if virtual_collection_name != None:
            payload["vCollectionName"] = virtual_collection_name
        elif virtual_collection_id != None:
            payload["vCollectionId"] = virtual_collection_id

        res = self.datalake_interface.update_virtual_collection(payload)

        return res

    """
    find chunk by search keys from text
    """

    def find_chunk(
        self,
        search_key_list: List[str],
        unique_name_list: List[str],
        page_index: int = 0,
        response_chunk_limit: int = 3,
        adjacent_chunk_limit: int = 1,
    ):
        payload = {
            "searchKeys": search_key_list,
            "uniqueNames": unique_name_list,
            "chunkLimit": response_chunk_limit,
            "pageIndex": page_index,
            "adjacentChunkLimit": adjacent_chunk_limit,
        }

        res = self.datalake_interface.find_chunk(payload)

        return res

    """
    find chunk by search keys from each pdf
    """

    def find_chunk_from_each_doc(
        self, search_key_list: List[str], unique_name_list: List[str]
    ):
        payload = {"searchKeys": search_key_list, "uniqueNames": unique_name_list}

        res = self.datalake_interface.find_chunk_from_each_doc(payload)

        return res

    """
    Find matching elements of document list given
    """

    def find_elements_from_docs(
        self,
        unique_name_list: List[str],
        original_question: str,
        user_question: str,
        is_target_documents_available: bool,
        chat_id: str,
    ):
        payload = {
            "userQuestion": user_question,
            "originalQuestion": original_question,
            "objectKeyList": unique_name_list,
            "isTargetDocumentsExist": is_target_documents_available,
            "converasationId": chat_id,
        }
        res = self.datalake_interface.find_elements_from_docs(payload)

        return res

    def get_metadata_details(self, object_key: str, fields: List[str]):
        res = self.datalake_interface.get_metadata_details(object_key, fields)

        return res

    """
    Extract document content
    """

    def extract_doc_content(
        self,
        doc_elements: dict,
        extraction_keys: List[dict],
        user_question: str,
        chat_id: str,
    ):
        payload = {
            "userQuestion": user_question,
            "docElements": doc_elements,
            "extractionKeys": extraction_keys,
            "converasationId": chat_id,
        }
        res = self.datalake_interface.extract_doc_content(payload)
        return res

    """
    Use to get data dictionary from overview data
    """

    def get_data_dictionary_with_overview_data(self):
        res = self.datalake_interface.get_data_dictionary_from_overview_data()

        return res

    def get_data_dictionary_modfied_timestamp(self):
        """
        Returns the latest time that data dictionary tables or overview were changed
        """
        return self.datalake_interface.get_data_dictionary_modified_timestamp()

    """
    Use to get data dictionary
    """

    def get_data_dictionary(self):
        res = self.datalake_interface.get_data_dictionary()
        if "isSuccess" in res and res["isSuccess"] == False:
            raise Exception(res["message"])
        if "isSuccess" in res:
            if res["isSuccess"] == False:
                message = res["message"]
                print(f"Success false with. message: {message}")
                raise Exception(message)
            else:
                print("Successfully extract the dictionary data")
                return res["data"]
        else:
            print("Request return with unexpected results")
            raise Exception("Request return with unexpected results")

    """ 
    Use to execute mongo db query
    @function     :  This can be 'aggregate', 'find', 'updateMany', etc.
    @input_data   :  The input parameters for the MongoDB function, provided as a JSON-like dictionary or list 
    @collection   :  The name of the MongoDB collection on which the query is to be run
    """

    def execute_mongo_query(
        self, source_name, function, input_data, collection, request_id
    ):

        payload = {
            "sourceName": source_name,
            "function": function,
            "query": json.dumps(input_data, cls=MongoJsonEncoder),
            "collection": collection,
        }
        res = self.datalake_interface.execute_mongo_query(payload, request_id)
        return res

    """ 
    Use to insert data into a specified MongoDB collection

    @source_name  : The name of the data source in the datalake system
    @collection   : The name of the MongoDB collection into which the data should be inserted
    @data         : The data to be inserted, provided as a list of dictionaries (documents)
    @request_id   : A unique identifier for the request, used for logging and tracing purposes

    @returns      : The result of the insertion operation, which includes information like the number of 
                    documents inserted and their respective IDs
    """

    def insert_mongo_data(self, source_name, collection, data, request_id):
        payload = {
            "sourceName": source_name,
            "collectionName": collection,
            "data": json.dumps(data, cls=MongoJsonEncoder),
        }
        res = self.datalake_interface.insert_mongo_data(payload, request_id)
        return res

    """ 
    Use to delete data from a specified MongoDB collection

    @source_name  : The name of the data source in the datalake system
    @collection   : The name of the MongoDB collection from which data should be deleted
    @filter_obj   : The filter criteria used to identify the documents to delete
    @request_id   : A unique identifier for the request, used for logging and tracing purposes

    @returns      : The result of the deletion operation, which includes information like the number of 
                    documents deleted and whether the operation was acknowledged
    """

    def delete_mongo_data(self, source_name, collection, filter_obj, request_id):
        payload = {
            "sourceName": source_name,
            "collectionName": collection,
            "filter": json.dumps(filter_obj, cls=MongoJsonEncoder),
        }
        res = self.datalake_interface.delete_mongo_data(payload, request_id)
        return res

    def run_sql_query(self, source_name, query, request_id):
        """
        Use to execute sql db query
        @source_name     :  source name you used to create the sql db connection with metalake
        @query   :  SQL query to execute
        """

        payload = {"sourceName": source_name, "query": query}
        res = self.datalake_interface.run_sql_query(payload, request_id)
        return res

    def get_source_list(self, source_list: List[str]) -> List[str]:
        """
        Get connection source and their types
        @source_list: get source list

        """

        payload = {
            "sourceList": source_list,
        }
        res = self.datalake_interface.get_source_list(payload)
        return res

    def retrieve_db_unstructured_records(
        self, categories=[], filter_key_values={}, page_index=0
    ):
        payload = {
            "categories": categories,
            "filterKeyValues": filter_key_values,
            "pageIndex": page_index,
        }
        res = self.datalake_interface.retrieve_db_unstructured_records(payload)
        return res

    def get_table_schema(self, source_name: str, table_name: str):
        """
        Get table schema for the given source_name and table_name.

        :param source_name: The name of the data source.
        :param table_name: The name of the table.
        :return: The table schema with fields and descriptions.
        """
        res = self.datalake_interface.get_table_schema(source_name, table_name)
        return res

    def submit_user_feedback(self, user_question, ai_answer, feedback_comment):
        """
        Send the user's feedback comment for a chat question to the datalake.
        """
        payload = {
            "userQuestion": user_question,
            "aiAnswer": ai_answer,
            "feedbackComment": feedback_comment,
        }
        res = self.datalake_interface.submit_user_feedback(payload)
        return res

    def retrieve_suggested_questions(self):
        """
        Retrieves a list of suggested questions from the DatalakeInterface.

        This function communicates with the DatalakeInterface to fetch suggested questions
        that might be relevant to the user's query or context.

        Returns:
            The response from the DatalakeInterface containing suggested questions.
        """
        res = self.datalake_interface.retrieve_suggested_questions()
        return res

    def get_datasource_metadata(self, connection_id: str):
        """
        Get datasource metadata for the given source_name.

        :param connection_id: The connection id of the data source.
        :return: The datasource metadata.
        """
        res = self.datalake_interface.get_datasource_metadata(connection_id)
        return res

    def add_knowledge_blocks(self, data: dict):
        """
        Add knowledge blocks to the datalake
        """
        res = self.datalake_interface.add_knowledge_blocks(data)
        return res

    def quickbooks_get_auth_uri(self) -> str:
        """
        Get QuickBooks authorization URI for OAuth flow

        Returns:
            str: The QuickBooks authorization URI
        """
        res = self.datalake_interface.quickbooks_get_auth_uri()
        return res

    def quickbooks_create_or_update_object(self, api_name: str, data: dict):
        """
        Create or update QuickBooks object
        """
        payload = {
            "apiName": api_name,
            "apiParams": data,
        }
        res = self.datalake_interface.quickbooks_create_or_update_object(payload)
        return res

    def quickbooks_upload_attachment(
        self, file_path: str, object_type: str, object_id: str
    ):
        """
        Upload attachment to QuickBooks object
        """
        payload = {
            "filePath": file_path,
            "objectType": object_type,
            "objectId": object_id,
        }

        res = self.datalake_interface.quickbooks_upload_attachment(payload)
        return res
