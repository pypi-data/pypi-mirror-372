import json
from multiprocessing.pool import ThreadPool
import os
from typing import TYPE_CHECKING
from .logger import get_debug_logger

if TYPE_CHECKING:
    from . import StudioClient


annotation_logger = get_debug_logger("Project")


class Project:
    def __init__(self, client: "StudioClient"):
        self._client = client

    """
    create the project
    """

    def create_project(
        self,
        project_name,
        selection_id,
        fps,
        frames_per_task,
        assign_to_all,
        send_email,
        default_shape_type,
        content_type,
    ):

        # check for validity of default_shape_type
        if (
            default_shape_type != "rectangle"
            and default_shape_type != "polygon"
            and default_shape_type != "line"
        ):
            default_shape_type = "rectangle"
        payload_project_creation = {
            "selectionId": selection_id,
            "name": project_name,
            "fps": fps,
            "framesPerTask": frames_per_task,
            "assignToAll": assign_to_all,
            "sendEmail": send_email,
            "defaultShapeType": default_shape_type,
            "contentType": content_type,
        }
        # print(payload_initial_project_creation)
        response = self._client.studio_interface.create_initial_project()
        get_selection_id_success = True
        if "isSuccess" in response:
            if response["isSuccess"] == False:
                get_selection_id_success = False
        if get_selection_id_success == True:
            print("project id: ", response["id"])
            project_response = self._client.studio_interface.create_or_update_project(
                response["id"], payload_project_creation, False
            )
            return project_response
        else:
            print({"isSuccess": False})
            return {"isSuccess": False}

    """
    update the project
    """

    def update_project(
        self,
        project_id,
        selection_id,
        fps,
        frames_per_task,
        assign_to_all,
        send_email,
        default_shape_type,
        content_type,
    ):

        # check for validity of default_shape_type
        if (
            default_shape_type != "rectangle"
            and default_shape_type != "polygon"
            and default_shape_type != "line"
        ):
            default_shape_type = "rectangle"
        payload_project_creation = {
            "selectionId": selection_id,
            "name": None,
            "fps": fps,
            "framesPerTask": frames_per_task,
            "assignToAll": assign_to_all,
            "sendEmail": send_email,
            "defaultShapeType": default_shape_type,
            "contentType": content_type,
        }

        response = self._client.studio_interface.create_or_update_project(
            project_id, payload_project_creation, True
        )

        return response

    """
    delete the project
    """

    def delete_project(self, project_id):
        response = self._client.studio_interface.delete_project(project_id)

        return response

    """
    update the labels of project
    """

    def update_labels_to_project(self, project_id, add_list, remove_list):
        response = self._client.studio_interface.update_labels_to_project(
            project_id, add_list, remove_list
        )
        return response

    """
    update the labels of project from label group
    """

    def update_labels_from_group_to_project(self, project_id, group_id):
        response = self._client.studio_interface.set_project_label_group(
            project_id, group_id
        )
        return response

    """
    Get list of studio project
    """

    def get_project_list(self):
        response = self._client.studio_interface.list_projects()
        return response
