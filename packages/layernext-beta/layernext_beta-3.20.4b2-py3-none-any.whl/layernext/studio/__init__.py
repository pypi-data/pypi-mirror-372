from layernext.studio.project import Project
from .studiointerface import StudioInterface
from .logger import get_debug_logger

# studio_logger = get_debug_logger('StudioClient')


class StudioClient:
    """
    Python SDK of Datalake
    """

    def __init__(self, encoded_key_secret: str, layernext_url: str) -> None:
        _studio_url = f"{layernext_url}/studio"  # /studio  :8080

        self.studio_interface = StudioInterface(encoded_key_secret, _studio_url)

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
        if project_name == "":
            print("Project name is empty")
            return None
        # print('project details: ', project_name, selection_id)
        _project = Project(client=self)
        response = _project.create_project(
            project_name,
            selection_id,
            fps,
            frames_per_task,
            assign_to_all,
            send_email,
            default_shape_type,
            content_type,
        )
        return response

    def get_project_name_by_id(self, project_id: str):
        res = self.studio_interface.get_project_name_by_id(project_id)
        if "isSuccess" in res and res["isSuccess"]:
            return {"projectName": res["projectName"]}
        else:
            message = res["message"]
            print(f"Error while getting project name by id. Error: {message}")

    """
        Attach model runs to a project
    """

    def attach_model_run_to_project(
        self, project_id: str, operation_id_array: list
    ) -> dict:
        res = self.studio_interface.attach_model_run_to_project_process(
            project_id, operation_id_array
        )
        return res

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
        # print('project details: ', project_id, selection_id)
        _project = Project(client=self)
        response = _project.update_project(
            project_id,
            selection_id,
            fps,
            frames_per_task,
            assign_to_all,
            send_email,
            default_shape_type,
            content_type,
        )
        return response

    """
    delete the project
    """

    def delete_project(self, project_id):
        # print('project details: ', project_id)
        _project = Project(client=self)
        response = _project.delete_project(project_id)
        return response

    """
    update the labels of project
    """

    def update_labels_to_project(self, project_id, add_list, remove_list):
        if project_id == "":
            print("Project Id is empty")
            return None
        _project = Project(client=self)
        response = _project.update_labels_to_project(project_id, add_list, remove_list)
        return response

    """
    Get list of studio project
    """

    def studio_project_list(self):
        _project = Project(client=self)
        response = _project.get_project_list()
        return response

    """
    Set label group
    """

    def project_set_label_group(self, project_id, group_id):
        if project_id == "" or group_id == "":
            print("Project Id or Group Id is empty")
            return None
        _project = Project(client=self)
        return _project.update_labels_from_group_to_project(project_id, group_id)
