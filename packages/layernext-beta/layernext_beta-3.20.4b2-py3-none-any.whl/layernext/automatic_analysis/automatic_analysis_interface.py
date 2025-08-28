import traceback
import requests
import time
import threading
from urllib.parse import quote_plus
from tqdm import tqdm

from layernext.datalake.constants import Task


class AutomaticAnalysisInterface:
    def __init__(self, auth_token: str, automatic_analysis_url: str):
        self.auth_token = auth_token
        self.automatic_analysis_url = automatic_analysis_url
        self.insufficient_load = False

    """
    Sending the main request to invokde flask app endpoint and start autotagging on the server side. 
    @param url:url which the request is sent : {self.automatic_analysis_url} in automatic_analysis_interface.py
    @param payload:payload of the request sent
    @param headers: headers of the reqeust sent
    """

    def send_request(self, url, payload, headers, task):

        try:
            self.insufficient_load = False
            if task == Task.EMBEDDING.value:
                response = requests.post(
                    url=f"{url}/dataIn_embedding",
                    json=payload,
                    headers=headers,
                    timeout=30,
                )
            elif task == Task.AUTO_TAGGING.value:
                response = requests.post(
                    url=f"{url}/dataIn", json=payload, headers=headers, timeout=30
                )
            elif task == Task.AUTO_ANNOTATION.value:
                response = requests.post(
                    url=f"{url}/dataIn_annotation",
                    json=payload,
                    headers=headers,
                    timeout=30,
                )
            status_code = response.status_code
            if status_code == 200:
                pass
                """ Okay to proceed """
            elif status_code == 204:
                print(f"No content return from this API call")
            elif status_code == 401:
                error_obj = response.json()
                error = error_obj.get("error")
                message = error_obj.get("message")
                print(f"Error: {format(error)}")
                print(message)
            elif status_code == 510:
                error_obj = response.json()
                error = error_obj.get("error")
                message = error_obj.get("message")
                print(f"{format(error)}")
                print(message)
            elif status_code == 509:
                print("Process is queued due to resource limitation")
            else:
                print(f"Error occur with status code: {status_code}")
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print(f"Error: {format(e)}")
            print(f"Failed to connect with Meta Lake Flask app")
        # Handle timeout error
        except requests.exceptions.Timeout as e:
            # print(f"Error: {format(e)}")
            # print("Timeout error from Meta Lake Flask connection")
            pass
        # Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print(f"Error: {format(e)}")
            print("HTTP error from Meta Lake Flask connection")
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")

    """
    combining about two processes as two threads to run them parallely
    @param url:url which the request is sent : {self.automatic_analysis_url} in automatic_analysis_interface.py
    @param payload:payload of the request sent
    @param headers: headers of the reqeust sent
    @param unique_id: a unique id generated to identify which autotagging process to refer. 
    """

    def main_analysis(self, payload, task):
        url = f"{self.automatic_analysis_url}"

        headers = {"Authorization": "Basic " + self.auth_token}
        request_thread = threading.Thread(
            target=self.send_request, args=(url, payload, headers, task)
        )
        request_thread.start()

    def inference_model_upload(
        self,
        storage_url,
        bucket_name,
        object_key,
        model_id,
        label_list,
        model_name,
        task,
    ):

        hed = {"Authorization": "Basic " + self.auth_token}
        payload = {
            "storage_url": storage_url,
            "bucket_name": bucket_name,
            "object_key": object_key,
            "model_ID": model_id,
            "model_name": model_name,
            "label_list": label_list,
            "task": task,
        }
        url = f"{self.automatic_analysis_url}/model_setup"

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                print(response.json())
                """ Okay to proceed """
            elif status_code == 204:
                print(f"No content return from this API call")
            elif status_code == 401:
                error_obj = response.json()
                error = error_obj.get("error")
                message = error_obj.get("message")
                print(f"Error: {format(error)}")
                print(message)
            else:
                print(f"Error occur with status code: {status_code}")
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print(f"Error: {format(e)}")
            print(f"Failed to connect with Meta Lake Flask app")
        # Handle timeout error
        except requests.exceptions.Timeout as e:
            # print(f"Error: {format(e)}")
            print("Timeout error from Meta Lake Flask connection")
        # Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print(f"Error: {format(e)}")
            print("HTTP error from Meta Lake Flask connection")
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")

    def prompt_detail_send(self, name, shape, **kwargs):
        hed = {"Authorization": "Basic " + self.auth_token}
        payload = {
            "bbox": kwargs["bbox"] if "bbox" in kwargs else {},
            "clicks": kwargs["clicks"] if "clicks" in kwargs else [],
            "shape": shape,
            "uniqueName": name,
        }
        url = f"{self.automatic_analysis_url}"
        try:
            response = requests.post(
                url=f"{url}/dataIn_prompt_infer", json=payload, headers=hed
            )
            # main_annotation(url,payload,hed,unique_id,task, auto_annotation_op)
            # print(response.json())
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Failed to connect with Automatic Analysis application")
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
