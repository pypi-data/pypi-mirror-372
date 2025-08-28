from typing import TYPE_CHECKING

from .constants import LABEL_CLASS_WITH_ATTRIBUTES
from .keys import (
    SUPERCATEGORY,
    NAME,
    LABEL_TEXT,
    VALUE,
    VALUES,
    VALUE_TEXT,
    DESCRIPTION,
    IMG_FILES,
    ATTRIBUTES,
    TYPE,
    LABEL_REF,
    LABEL,
    LABEL_COLOR,
    COLOR,
    IMAGES,
    ANNOTATIONS,
    METADATA,
)

if TYPE_CHECKING:
    from . import DatalakeClient


class Label:
    def __init__(self, client: "DatalakeClient"):
        self._client = client

    @staticmethod
    def get_system_label_create_payload(label_dict):

        # Validate className: Should exist and should not be an empty string
        className = label_dict.get("className", None)
        if not className:
            raise ValueError(
                "The 'className' must exist and should not be an empty string"
            )

        payload = {
            "labelText": className,
            "description": label_dict.get("description", ""),
            "attributes": [],
            "imgFiles": [],
            "type": 2,
        }

        # Set to keep track of unique attributeNames
        attribute_names = set()

        if "attributes" in label_dict:
            for attribute in label_dict["attributes"]:

                attribute_name = attribute.get("attributeName", None)

                # Validate attributeName: Should exist and should not be an empty string
                if not attribute_name:
                    raise ValueError(
                        "The 'attributeName' must exist and should not be an empty string"
                    )

                # Check if attributeName is duplicate
                if attribute_name in attribute_names:
                    raise ValueError(f"Duplicate attributeName found: {attribute_name}")
                attribute_names.add(attribute_name)

                attr = {
                    "labelText": attribute_name,
                    "values": [],
                }

                # Set to keep track of unique valueNames within this attribute
                value_names = set()

                if "values" in attribute:
                    for value in attribute["values"]:
                        value_name = value.get("valueName", None)

                        # Validate valueName: Should exist and should not be an empty string
                        if not value_name:
                            raise ValueError(
                                f"The 'valueName' for attributeName '{attribute_name}' must exist and should not be an empty string"
                            )

                        # Check if valueName is duplicate within this attribute
                        if value_name in value_names:
                            raise ValueError(
                                f"Duplicate valueName found for attributeName '{attribute_name}': {value_name}"
                            )
                        value_names.add(value_name)

                        val = {
                            "valueText": value_name,
                            "description": value.get("description", ""),
                        }
                        attr["values"].append(val)

                payload["attributes"].append(attr)

        return payload

    @staticmethod
    def get_label_attribute_values_dict_v2(modelrun_data):
        label_attribute_values_dict = {}

        # iterate through images
        for image in modelrun_data[IMAGES]:
            for annotation in image[ANNOTATIONS]:
                # if label class not exists in label_attribute_values_dict, then add it
                if annotation[LABEL] not in label_attribute_values_dict:
                    label_attribute_values_dict[annotation[LABEL]] = {}

                # add attributes and values to dict from metadata
                _attribute_value = label_attribute_values_dict[annotation[LABEL]]
                if ATTRIBUTES in annotation:
                    _attributes = annotation[ATTRIBUTES]
                    for attr, val in _attributes.items():
                        # if attribute not exist, then add it
                        if attr not in _attribute_value:
                            _attribute_value[attr] = []
                        # values array iterate and if value not exist, then add it
                        for _val in val:
                            if _val[VALUE] not in _attribute_value[attr]:
                                _attribute_value[attr].append(_val[VALUE])

        return label_attribute_values_dict

    @staticmethod
    def get_label_attribute_values_dict(modelrun_data):
        label_attribute_values_dict = {}

        # iterate through images
        for image in modelrun_data[IMAGES]:
            for annotation in image[ANNOTATIONS]:
                # if label class not exists in label_attribute_values_dict, then add it
                if annotation[LABEL] not in label_attribute_values_dict:
                    label_attribute_values_dict[annotation[LABEL]] = {}

                # add attributes and values to dict from metadata
                _attribute_value = label_attribute_values_dict[annotation[LABEL]]
                if METADATA in annotation:
                    _metadata = annotation[METADATA]
                    for attr, val in _metadata.items():
                        # if attribute not exist, then add it
                        if attr not in _attribute_value:
                            _attribute_value[attr] = []
                        # if value not exist, then add it
                        if val not in _attribute_value[attr]:
                            _attribute_value[attr].append(val)

        return label_attribute_values_dict

    def create_label_from_cocojson(self, categories):
        category_dict = {}

        for category in categories:
            if category[SUPERCATEGORY] in category_dict:
                category_dict[category[SUPERCATEGORY]].append(category[NAME])
            else:
                category_dict[category[SUPERCATEGORY]] = [category[NAME]]

        label_dict_list = []

        # convert coco categories into datalake system label type
        for key, value in category_dict.items():

            attributes = [{LABEL_TEXT: NAME, VALUES: []}]

            for val in value:
                attributes[0][VALUES].append(
                    {VALUE_TEXT: val, DESCRIPTION: "", IMG_FILES: []}
                )

            label_dict = {
                LABEL_TEXT: key,
                DESCRIPTION: "",
                ATTRIBUTES: attributes,
                IMG_FILES: [],
                TYPE: LABEL_CLASS_WITH_ATTRIBUTES,
            }

            label_dict_list.append(label_dict)

        # call datalake to create system labels
        system_label_dict = {}
        for _label in label_dict_list:
            response = self._client.datalake_interface.create_datalake_label_coco(
                _label
            )
            if response is not None:
                if LABEL_TEXT in response:
                    system_label_dict[response[LABEL_TEXT].lower()] = response

        # add system label references to coco categories
        for category in categories:
            if category[SUPERCATEGORY].lower() in system_label_dict:
                system_label = system_label_dict[category[SUPERCATEGORY].lower()]
                category[LABEL_REF] = system_label[LABEL]
                category[LABEL_COLOR] = system_label[COLOR]
                # TODO: add system label attribute references
