import json
import traceback
import requests


class DatasetInterface:

    def __init__(self, auth_token: str, dalalake_url: str):
        self.auth_token = auth_token
        self.dalalake_url = dalalake_url

    """
    create dataset from search objects
    """

    def create_dataset(self, selection_id, payload_dataset_creation):
        hed = {"Authorization": "Basic " + self.auth_token}
        url = f"{self.dalalake_url}/api/client/dataset/create?datasetSelectionId={selection_id}"

        try:
            response = requests.get(url=url, json=payload_dataset_creation, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                response = response.json()
                if "error" in response:
                    if "message" in response["error"]:
                        return {
                            "isSuccess": False,
                            "message": response["error"]["message"],
                        }
                    else:
                        return {"isSuccess": False}
                else:
                    return {"isSuccess": False}
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Failed to connect with Dataset Manager")
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
    update dataset from search objects
    """

    def update_existing_dataset_version(
        self, selection_id, payload_dataset_update, version_id
    ):
        hed = {"Authorization": "Basic " + self.auth_token}
        url = f"{self.dalalake_url}/api/client/dataset/updateExistingVersion?datasetSelectionId={selection_id}&datasetVersionId={version_id}"

        try:
            response = requests.get(url=url, json=payload_dataset_update, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                response = response.json()
                if "error" in response:
                    if "message" in response["error"]:
                        return {
                            "isSuccess": False,
                            "message": response["error"]["message"],
                        }
                    else:
                        return {"isSuccess": False}
                else:
                    return {"isSuccess": False}
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Failed to connect with Dataset Manager")
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
    create dataset version from search objects
    """

    def create_new_dataset_version(
        self, selection_id, payload_dataset_update, version_id
    ):
        hed = {"Authorization": "Basic " + self.auth_token}
        url = f"{self.dalalake_url}/api/client/dataset/updateNewVersion?datasetSelectionId={selection_id}&datasetVersionId={version_id}"

        try:
            response = requests.get(url=url, json=payload_dataset_update, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                response = response.json()
                if "error" in response:
                    if "message" in response["error"]:
                        return {
                            "isSuccess": False,
                            "message": response["error"]["message"],
                        }
                    else:
                        return {"isSuccess": False}
                else:
                    return {"isSuccess": False}
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Failed to connect with Dataset Manager")
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
    delete dataset version
    """

    def delete_dataset_version(self, version_id):
        hed = {"Authorization": "Basic " + self.auth_token}
        url = f"{self.dalalake_url}/api/client/dataset/deleteVersion?datasetVersionId={version_id}"

        try:
            response = requests.get(url=url, json={}, headers=hed)
            status_code = response.status_code
            if status_code == 200 or status_code == 204:
                return {"isSuccess": True}
            else:
                response = response.json()
                if "error" in response:
                    if "message" in response["error"]:
                        return {
                            "isSuccess": False,
                            "message": response["error"]["message"],
                        }
                    else:
                        return {"isSuccess": False}
                else:
                    return {"isSuccess": False}
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Failed to connect with Dataset Manager")
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
