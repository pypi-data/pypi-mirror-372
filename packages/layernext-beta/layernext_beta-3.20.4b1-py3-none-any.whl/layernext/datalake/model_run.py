from typing import TYPE_CHECKING

from .annotation import Annotation
from .constants import OPERATION_MODE_AUTO, AnnotationUploadType
from .logger import get_debug_logger


if TYPE_CHECKING:
    from . import DatalakeClient

model_logger = get_debug_logger("Model")


class ModelRun(Annotation):
    def __init__(self, client: "DatalakeClient"):
        super().__init__(client)

    def upload_modelrun_json(
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
        model_logger.debug(f"Started uploading model run data for model_id: {model_id}")
        self.upload_annotation_json(
            unique_id,
            model_id,
            file_path,
            annotation_geometry,
            OPERATION_MODE_AUTO,
            is_normalized,
            version,
            bucket_name,
            upload_type,
        )
        model_logger.debug(
            f"Finished uploading model run data for model_id: {model_id}"
        )
