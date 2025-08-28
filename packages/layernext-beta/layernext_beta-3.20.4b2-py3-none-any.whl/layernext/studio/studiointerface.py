import traceback
import requests


class StudioInterface:

    def __init__(self, auth_token: str, studio_url: str):
        self.auth_token = auth_token
        self.studio_url = studio_url

    """'
    create initial project
    """

    def create_initial_project(self):
        hed = {"Authorization": "Basic " + self.auth_token}
        url = f"{self.studio_url}/api/client/projects/initial/create"

        try:
            response = requests.get(url=url, json={}, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False}
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Failed to connect with Annotation Studio")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        # Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        # Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {
                "isSuccess": False,
                "message": "An unexpected request exception occurred",
            }
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "An unexpected exception occurred"}

    """
    update of create project
    """

    def create_or_update_project(self, project_id, payload, isEditable):
        hed = {"Authorization": "Basic " + self.auth_token}
        url = f"{self.studio_url}/api/client/project/{project_id}/update?isEditable={isEditable}"

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False, "message": response.text}
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Failed to connect with Annotation Studio")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        # Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        # Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {
                "isSuccess": False,
                "message": "An unexpected request exception occurred",
            }
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "An unexpected exception occurred"}

    """
    update of create project
    """

    def delete_project(self, project_id):
        hed = {"Authorization": "Basic " + self.auth_token}
        url = f"{self.studio_url}/api/client/project/{project_id}/delete"

        try:
            response = requests.post(url=url, json={}, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False, "errorMsg": response.text}
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Failed to connect with Annotation Studio")
            return {"isSuccess": False, "errorMsg": "Failed to connect to Data Lake"}
        # Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "errorMsg": "Failed to connect to Data Lake"}
        # Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "errorMsg": "Failed to connect to Data Lake"}
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {
                "isSuccess": False,
                "errorMsg": "An unexpected request exception occurred",
            }
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "errorMsg": "An unexpected exception occurred"}

    """
    update the labels of project
    """

    def update_labels_to_project(self, project_id, add_list, remove_list):
        payload = {"addList": add_list, "removeList": remove_list}

        hed = {"Authorization": "Basic " + self.auth_token}
        url = f"{self.studio_url}/api/client/project/{project_id}/updateLabel"

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False}
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Failed to connect with Annotation Studio")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        # Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        # Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {
                "isSuccess": False,
                "message": "An unexpected request exception occurred",
            }
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "An unexpected exception occurred"}

    """
    Get list of studio project
    """

    def list_projects(self):
        hed = {"Authorization": "Basic " + self.auth_token}
        url = f"{self.studio_url}/api/client/projects/list"

        try:
            response = requests.get(url=url, headers=hed)
            return response.json()
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Failed to connect with Annotation Studio")
        # Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
        # Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()

    """
    Update the label group for the project
    """

    def set_project_label_group(self, project_id, group_id):
        hed = {"Authorization": "Basic " + self.auth_token}
        url = f"{self.studio_url}/api/client/project/{project_id}/setLabelGroup"
        payload = {
            "labelGroupId": group_id,
        }
        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return None
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Failed to connect with Annotation Studio")
            return None
        # Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return None
        # Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return None
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return None
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return None

    """
        Attach model runs to a project
    """

    def attach_model_run_to_project_process(
        self, project_id: str, operation_id_array: list
    ) -> dict:
        hed = {"Authorization": "Basic " + self.auth_token}
        url = f"{self.studio_url}/api/client/projects/modelRun/attach"
        payload = {"projectId": project_id, "operationIdArray": operation_id_array}
        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                json_output: dict = response.json()
                res: dict = {}
                if "isSuccess" in json_output:
                    res["is_success"] = json_output["isSuccess"]
                if "message" in json_output:
                    res["message"] = json_output["message"]
                return res
            elif status_code == 422:
                return {
                    "is_success": False,
                    "message": response.json()
                    .get("error", {})
                    .get("details", "Unprocessable"),
                }
            else:
                return None
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Failed to connect with Annotation Studio")
            return None
        # Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return None
        # Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return None
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return None
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return None

    def get_project_name_by_id(self, project_id: str):
        hed = {"Authorization": "Basic " + self.auth_token}
        url = f"{self.studio_url}/api/client/projects/get/projectName"
        payload = {
            "projectId": project_id,
        }
        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return None
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Failed to connect with Annotation Studio")
            return None
        # Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return None
        # Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return None
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return None
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return None
