from layernext.dataset.dataset import Dataset
from .sync import DatasetSync
from .datasetinterface import DatasetInterface


class DatasetClient:
    """
    Python SDK of Dataset download
    """

    def __init__(
        self, encoded_key_secret: str, layernext_url: str, download_path: str = None
    ) -> None:
        _datalake_url = f"{layernext_url}/dataset"  # /dataset :4000
        self.dataset_interface = DatasetInterface(encoded_key_secret, _datalake_url)
        self._dataset_sync_tool = DatasetSync(
            encoded_key_secret, layernext_url, download_path
        )

    """
    Download dataset
    @param version_id - id of dataset version 
    @param export_type - dataset export format """

    def download_dataset(
        self, version_id: str, export_type: str, is_media_include: True
    ):
        self._dataset_sync_tool.download_dataset(
            version_id, export_type, is_media_include
        )

    """
    Download collection annotations
    From datalake
    @param collection_id - id of collection
    @param model_id - Optional: id of the model (same operation_id given in upload annotations) 
    if we need annotations for that specific model """

    def download_annotations(
        self, collection_id: str, annotation_type, operation_id_list, is_media_include
    ):
        self._dataset_sync_tool.download_collection(
            collection_id, annotation_type, operation_id_list, is_media_include
        )

    """
    Download project annotations
    From datalake
    @param project_id - id of collection
    if we need annotations for that specific model """

    def download_annotations_for_project_v2(
        self, project_id_list, status_list, is_annotated_only, is_media_include
    ):
        self._dataset_sync_tool.download_project_v2(
            project_id_list, status_list, is_annotated_only, is_media_include
        )

    """
    create dataset from search objects
    """

    def create_dataset(
        self,
        dataset_name,
        selection_id,
        split_info,
        labels,
        export_types,
        operation_list,
        augmentation_list,
    ):
        _dataset = Dataset(client=self)
        response = _dataset.create_dataset(
            dataset_name,
            selection_id,
            split_info,
            labels,
            export_types,
            operation_list,
            augmentation_list,
        )
        return response

    """
    update dataset from search objects
    """

    def update_dataset_version(
        self,
        version_id,
        selection_id,
        split_info,
        labels,
        export_types,
        is_new_version_required,
        operation_list,
        augmentation_list,
    ):
        _dataset = Dataset(client=self)
        response = _dataset.update_dataset_version(
            version_id,
            selection_id,
            split_info,
            labels,
            export_types,
            is_new_version_required,
            operation_list,
            augmentation_list,
        )
        return response

    """
    delete dataset version
    """

    def delete_dataset_version(self, version_id):
        _dataset = Dataset(client=self)
        response = _dataset.delete_dataset_version(version_id)
        return response
