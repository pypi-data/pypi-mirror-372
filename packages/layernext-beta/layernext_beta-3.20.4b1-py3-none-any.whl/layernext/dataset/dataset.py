from typing import TYPE_CHECKING
from .logger import get_debug_logger

if TYPE_CHECKING:
    from . import DatasetClient


annotation_logger = get_debug_logger("Dataset")


class Dataset:
    def __init__(self, client: "DatasetClient"):
        self._client = client

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
        if dataset_name == "" or dataset_name == None:
            return {"isSuccess": False, "message": "dataset name not valid"}
        if selection_id == "" or selection_id == None:
            return {"isSuccess": False, "message": "selection_id not valid"}
        validationObj = self.validate_split_info(split_info)
        if validationObj["isValidate"] == False:
            return {"isSuccess": False, "message": validationObj["message"]}
        if augmentation_list != None:
            if "IMAGE_LEVEL" in augmentation_list:
                for i in range(len(augmentation_list["IMAGE_LEVEL"])):
                    augmentation_list["IMAGE_LEVEL"][i]["isSelected"] = True

        split_info = {
            "train": split_info["train"],
            "test": split_info["test"],
            "validation": split_info["validation"],
        }
        payload_dataset_creation = {
            "name": dataset_name,
            "splitInfo": split_info,
            "labels": labels,
            "exportTypes": export_types,
            "operations": operation_list,
            "augmentations": augmentation_list,
        }

        response = self._client.dataset_interface.create_dataset(
            selection_id, payload_dataset_creation
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
        if version_id == "" or version_id == None:
            return {"isSuccess": False, "message": "dataset name not valid"}
        if selection_id == "" or selection_id == None:
            return {"isSuccess": False, "message": "selection_id not valid"}
        validationObj = self.validate_split_info(split_info)
        if validationObj["isValidate"] == False:
            return {"isSuccess": False, "message": validationObj["message"]}

        if augmentation_list != None:
            if "IMAGE_LEVEL" in augmentation_list:
                for i in range(len(augmentation_list["IMAGE_LEVEL"])):
                    augmentation_list["IMAGE_LEVEL"][i]["isSelected"] = True

        split_info = {
            "train": split_info["train"],
            "test": split_info["test"],
            "validation": split_info["validation"],
        }
        payload_dataset_update = {
            "splitInfo": split_info,
            "labels": labels,
            "exportTypes": export_types,
            "operations": operation_list,
            "augmentations": augmentation_list,
        }
        if is_new_version_required == False:
            response = self._client.dataset_interface.update_existing_dataset_version(
                selection_id, payload_dataset_update, version_id
            )
        else:
            response = self._client.dataset_interface.create_new_dataset_version(
                selection_id, payload_dataset_update, version_id
            )
        return response

    """
    validate split info object for dataset creation and update
    """

    def validate_split_info(self, split_info):

        if (
            ("train" not in split_info)
            or ("test" not in split_info)
            or ("validation" not in split_info)
        ):
            return {"isValidate": False, "message": "split info not valid"}
        elif (
            split_info["train"] + split_info["test"] + split_info["validation"]
        ) != 100:
            return {
                "isValidate": False,
                "message": "Invalid split percentages. The test, train, and validation splits must sum up to 100%.",
            }
        else:
            return {"isValidate": True, "message": "split info valid"}

    """
    delete dataset version
    """

    def delete_dataset_version(self, version_id):
        response = self._client.dataset_interface.delete_dataset_version(version_id)

        return response
