import json
from typing import TYPE_CHECKING

from .annotation import Annotation
from .constants import OPERATION_MODE_HUMAN, AnnotationUploadType
from .keys import CATEGORIES
from .label import Label
from .logger import get_debug_logger

if TYPE_CHECKING:
    from . import DatalakeClient

ground_truth_logger = get_debug_logger("GroundTruth")


class GroundTruth(Annotation):
    def __init__(self, client: "DatalakeClient"):
        super().__init__(client)

    def upload_groundtruth_json(
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
        ground_truth_logger.debug(
            f"Started uploading ground truth data for model_id: {operation_id}"
        )
        self.upload_annotation_json(
            unique_id,
            operation_id,
            file_path,
            annotation_geometry,
            OPERATION_MODE_HUMAN,
            is_normalized,
            version,
            bucket_name,
            upload_type,
        )
        ground_truth_logger.debug(
            f"Finished uploading ground truth data for model_id: {operation_id}"
        )

    def upload_coco(self, file_path: str):
        # load json file
        f = open(file_path)
        coco_data = json.load(f)
        f.close()

        label = Label(client=self._client)
        label.create_label_from_cocojson(categories=coco_data[CATEGORIES])
        # TODO: format Images and Annotations as MetaUpdates format, then call metaUpdates API
