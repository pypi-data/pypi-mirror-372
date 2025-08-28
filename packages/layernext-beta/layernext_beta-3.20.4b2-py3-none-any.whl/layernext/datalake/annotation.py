import datetime
import json
import uuid
from typing import TYPE_CHECKING
import time

from .constants import (
    OPERATION_MODE_HUMAN,
    OPERATION_TYPE_ANNOTATION,
    OPERATION_MODE_AUTO,
    META_UPDATE_REQUEST_BATCH_SIZE,
    AnnotationUploadType,
    AnnotationShapeType,
)
from .keys import (
    ATTRIBUTES,
    BUCKET_NAME,
    FILE_NAME,
    IMAGES,
    IMAGE,
    ANNOTATIONS,
    BBOX,
    BOX_BOUNDARIES_AND_DIMENSIONS,
    JOB_ID,
    STORAGE_NAME,
    STORAGE_PATH,
    VALUE,
    X,
    Y,
    W,
    H,
    POINTS,
    LABEL,
    LABEL_TEXT,
    REF,
    KEY,
    COLOR,
    ATTRIBUTE_VALUES,
    METADATA,
    TEXTS,
    TYPE,
    ID,
    SHAPE_ID,
    CREATED_AT,
    OBJECT_KEY,
    ANNOTATION_OBJECTS,
    DATA,
    IS_USER_ANNOTATED,
    UPDATED_AT,
    LINE,
    POLYGON,
    CONFIDENCE,
)
from .logger import get_debug_logger
from .label import Label

if TYPE_CHECKING:
    from . import DatalakeClient

annotation_logger = get_debug_logger("Annotation")


class Annotation:
    def __init__(self, client: "DatalakeClient"):
        self._client = client

    @staticmethod
    def format_bbox_annotation(annotation_object_input, annotation_object_output):
        if BBOX in annotation_object_input and len(annotation_object_input[BBOX]) == 4:
            x = annotation_object_input[BBOX][0]
            y = annotation_object_input[BBOX][1]
            width = annotation_object_input[BBOX][2]
            height = annotation_object_input[BBOX][3]

            annotation_object_output[BOX_BOUNDARIES_AND_DIMENSIONS] = {
                X: x,
                Y: y,
                W: width,
                H: height,
            }
            annotation_object_output[POINTS] = [
                [x, y],
                [x + width, y],
                [x + width, y + height],
                [x, y + height],
            ]

    @staticmethod
    def format_line_annotation(annotation_object_input, annotation_object_output):
        if LINE in annotation_object_input:
            # calculate coordinates
            annotation_object_output[POINTS] = annotation_object_input[LINE]

    @staticmethod
    def format_polygon_annotation(annotation_object_input, annotation_object_output):
        if POLYGON in annotation_object_input:
            # calculate coordinates
            annotation_object_output[POINTS] = annotation_object_input[POLYGON]

    @staticmethod
    def format_points_annotation(annotation_object_input, annotation_object_output):
        if POINTS in annotation_object_input:
            # calculate coordinates
            annotation_object_output[POINTS] = annotation_object_input[POINTS]

    def upload_annotation_json(
        self,
        unique_id: str,
        operation_id: str,
        file_path: str,
        annotation_geometry: str,
        operation_mode: int,
        is_normalized: bool,
        version: str,
        bucket_name: str,
        upload_type: AnnotationUploadType,
    ):

        session_uuid = str(datetime.datetime.now().timestamp())
        storage_path = None
        unique_name = None
        job_id = None
        file_name = None

        # load json file
        f = open(file_path)
        annotation_data = json.load(f)
        f.close()

        # get labels,attributes,values in the json files as a dictionary
        if version is None:
            label_attribute_values_dict = Label.get_label_attribute_values_dict(
                annotation_data
            )
        elif version == "v2":
            label_attribute_values_dict = Label.get_label_attribute_values_dict_v2(
                annotation_data
            )
        else:
            raise Exception(f"Invalid version: {version}")
        annotation_logger.debug("retrieving datalake label references started")
        label_references = (
            self._client.datalake_interface.find_datalake_label_references(
                label_attribute_values_dict
            )
        )
        annotation_logger.debug("retrieving datalake label references finished")
        if "isSuccess" in label_references:
            if label_references["isSuccess"] == False:
                raise Exception(
                    f'Error in retrieving datalake label references: {label_references["message"]}'
                )

        # format data to call datalake operation data update API
        meta_updates_list = []
        request_batch_size = META_UPDATE_REQUEST_BATCH_SIZE
        total_images_count = len(annotation_data[IMAGES])
        uploaded_images_count = 0
        annotation_logger.debug(
            f"total images count with annotation data: {total_images_count}"
        )

        # if upload done by collection name, unique id represents collection id.
        # if upload done by job id, unique id represents job id.
        if (
            upload_type == AnnotationUploadType.BY_FILE_NAME
            or upload_type == AnnotationUploadType.BY_FILE_NAME_OR_UNIQUE_NAME
        ):
            if unique_id is not None and unique_id != "":
                collection_object = self._client.get_collection_details(
                    unique_id, {"storagePath": True}
                )
                if collection_object is not None and "storagePath" in collection_object:
                    unique_name = collection_object["storagePath"]
                else:
                    raise Exception(f"Error in retrieving collection details")
        elif upload_type == AnnotationUploadType.BY_JOB_ID:
            if unique_id is not None and unique_id != "":
                job_id = unique_id
            else:
                raise Exception(
                    f"job id is required for upload annotation data by job id"
                )

        for image in annotation_data[IMAGES]:
            if upload_type == AnnotationUploadType.BY_FILE_NAME:
                object_key = f"{unique_name}_{image[IMAGE]}"
            elif upload_type == AnnotationUploadType.BY_STORAGE_PATH:
                object_key = None
                storage_path = f"{image[IMAGE]}"
            elif upload_type == AnnotationUploadType.BY_UNIQUE_NAME:
                object_key = f"{image[IMAGE]}"
            elif upload_type == AnnotationUploadType.BY_FILE_NAME_OR_UNIQUE_NAME:
                if unique_id is None:
                    object_key = f"{image[IMAGE]}"
                else:
                    object_key = f"{unique_name}_{image[IMAGE]}"
            elif upload_type == AnnotationUploadType.BY_JOB_ID:
                object_key = None
                file_name = f"{image[IMAGE]}"
            else:
                raise Exception(f"Invalid upload type: {upload_type}")

            if STORAGE_NAME in image:
                bucket_name = image[STORAGE_NAME]

            annotation_objects = []
            i = 1
            for annotation in image[ANNOTATIONS]:
                annotation_object = {}
                if annotation_geometry is None and TYPE not in annotation:
                    raise Exception(
                        f"Invalid annotation data. Annotation type not found in annotation {annotation}"
                    )

                if TYPE in annotation:
                    annotation_geometry = annotation[TYPE]

                # calculate coordinates and other dimensions
                if annotation_geometry == AnnotationShapeType.BOX_ANNOTATION.value:
                    self.format_bbox_annotation(annotation, annotation_object)
                elif (
                    annotation_geometry == AnnotationShapeType.POLYGON_ANNOTATION.value
                ):
                    self.format_polygon_annotation(annotation, annotation_object)
                elif annotation_geometry == AnnotationShapeType.LINE_ANNOTATION.value:
                    self.format_line_annotation(annotation, annotation_object)
                elif annotation_geometry == AnnotationShapeType.POINTS_ANNOTATION.value:
                    self.format_points_annotation(annotation, annotation_object)
                else:
                    break

                # assign annotation geometry type, ids, timestamps, confidence, etc.
                annotation_object_uuid = uuid.uuid4()
                annotation_object[ID] = f"shape_{annotation_object_uuid}"
                annotation_object[SHAPE_ID] = i
                i += 1
                annotation_object[CREATED_AT] = {"$date": str(datetime.datetime.now())}
                annotation_object[TYPE] = annotation_geometry
                if CONFIDENCE in annotation:
                    annotation_object[CONFIDENCE] = annotation[CONFIDENCE]

                # if METADATA in annotation:
                #     annotation_object[METADATA] = annotation[METADATA]

                try:
                    # assign label class
                    annotation_object[LABEL] = {
                        LABEL: label_references[annotation[LABEL]][REF],
                        LABEL_TEXT: annotation[LABEL],
                        METADATA: {},
                        KEY: label_references[annotation[LABEL]][REF],
                        COLOR: label_references[annotation[LABEL]][COLOR],
                        ATTRIBUTE_VALUES: {},
                    }
                    # assign label attribute and values
                    if version is None:
                        annotation_object[METADATA] = {}

                        if METADATA in annotation:
                            for attr, val in annotation[METADATA].items():
                                try:
                                    attr_ref = label_references[annotation[LABEL]][
                                        TEXTS
                                    ][attr][REF]
                                    val_ref = label_references[annotation[LABEL]][
                                        TEXTS
                                    ][attr][TEXTS][val]
                                    if (
                                        attr_ref
                                        not in annotation_object[LABEL][
                                            ATTRIBUTE_VALUES
                                        ]
                                    ):
                                        annotation_object[LABEL][ATTRIBUTE_VALUES][
                                            attr_ref
                                        ] = []
                                    annotation_object[LABEL][ATTRIBUTE_VALUES][
                                        attr_ref
                                    ].append(
                                        {
                                            VALUE: val_ref,
                                            CONFIDENCE: (
                                                1
                                                if operation_mode
                                                == OPERATION_MODE_HUMAN
                                                else annotation[CONFIDENCE]
                                            ),
                                        }
                                    )
                                except (TypeError, KeyError, Exception) as te:
                                    print(
                                        f"An Error Occurred at attribute value reference finding for object_key: "
                                        f"{object_key}",
                                        te,
                                    )
                                    continue
                    elif version == "v2":
                        if METADATA in annotation:
                            annotation_object[METADATA] = annotation[METADATA]
                        else:
                            annotation_object[METADATA] = {}

                        if ATTRIBUTES in annotation:
                            for attr, val_array in annotation[ATTRIBUTES].items():
                                try:
                                    attr_ref = label_references[annotation[LABEL]][
                                        TEXTS
                                    ][attr][REF]

                                    for val_obj in val_array:
                                        val_ref = label_references[annotation[LABEL]][
                                            TEXTS
                                        ][attr][TEXTS][val_obj[VALUE]]
                                        val_obj[VALUE] = val_ref
                                        confidence = 0
                                        if operation_mode == OPERATION_MODE_HUMAN:
                                            confidence = 1
                                        elif CONFIDENCE in val_obj:
                                            confidence = val_obj[CONFIDENCE]
                                        val_obj[CONFIDENCE] = confidence
                                    annotation_object[LABEL][ATTRIBUTE_VALUES][
                                        attr_ref
                                    ] = val_array
                                except (TypeError, KeyError, Exception) as te:
                                    print(
                                        f"An Error Occurred at attribute value reference finding for object_key: "
                                        f"{object_key}",
                                        te,
                                    )
                                    continue
                    else:
                        raise Exception(f"Invalid version: {version}")

                    annotation_objects.append(annotation_object)
                except (TypeError, KeyError, Exception) as te:
                    print(
                        f"An Error Occurred at label class reference finding for object_key: {object_key}",
                        te,
                    )
                    continue

            meta_update_data = {
                ANNOTATION_OBJECTS: annotation_objects,
                IS_USER_ANNOTATED: False,
            }
            meta_updates = {
                OBJECT_KEY: object_key,
                STORAGE_PATH: storage_path,
                BUCKET_NAME: bucket_name,
                JOB_ID: job_id,
                FILE_NAME: file_name,
                DATA: meta_update_data,
            }
            meta_updates_list.append(meta_updates)

            # call datalake operation data update API if batch size equals,
            # this is to reduce memory consumption & to stop request body size exceeding
            if len(meta_updates_list) == request_batch_size:
                uploaded_images_count = uploaded_images_count + len(meta_updates_list)
                annotation_logger.debug(
                    f"uploading annotation data of batch size: {len(meta_updates_list)}"
                )
                meta_update_response = (
                    self._client.datalake_interface.upload_metadata_updates(
                        meta_updates_list,
                        OPERATION_TYPE_ANNOTATION,
                        operation_mode,
                        operation_id,
                        is_normalized,
                        session_uuid,
                        total_images_count,
                        uploaded_images_count,
                    )
                )
                annotation_logger.debug(
                    f"annotation data uploaded images count: {uploaded_images_count}"
                )

                meta_updates_list = []

        # call datalake operation data update API
        # this will handle final batch
        uploaded_images_count = uploaded_images_count + len(meta_updates_list)
        annotation_logger.debug(
            f"uploading annotation data of batch size: {len(meta_updates_list)}"
        )
        meta_update_response = self._client.datalake_interface.upload_metadata_updates(
            meta_updates_list,
            OPERATION_TYPE_ANNOTATION,
            operation_mode,
            operation_id,
            is_normalized,
            session_uuid,
            total_images_count,
            uploaded_images_count,
        )
        annotation_logger.debug(
            f"annotation data uploaded images count: {uploaded_images_count}"
        )

    def remove_collection_annotations(self, collection_id, model_run_id):
        session_uuid = str(datetime.datetime.now().timestamp())
        meta_update_response = (
            self._client.datalake_interface.remove_modelrun_collection_annotation(
                collection_id, model_run_id, session_uuid
            )
        )
        print("delete annotation status: ", meta_update_response)
        return meta_update_response
