import requests
import time
import threading
from urllib.parse import quote_plus
from tqdm import tqdm

"""
Status reporting of collection auto tagging through getting constant updates from DB collection until the request is timied out.
"""
insufficient_load = False
"""
Sending the main request to invokde flask app endpoint and start autotagging on the server side. 
@param url:url which the request is sent : {self.automatic_analysis_url} in automatic_analysis_interface.py
@param payload:payload of the request sent
@param headers: headers of the reqeust sent
"""


def send_request(url, payload, headers):
    try:
        global insufficient_load
        insufficient_load = False
        response = requests.post(
            url=f"{url}/dataIn_annotation", json=payload, headers=headers, timeout=30
        )
        if response.json()["LOAD"] == "insufficient":
            insufficient_load = True
            print(response.json())
    except requests.exceptions.Timeout:
        # print("The request timed out")
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
Sending and receving the get status reqeust periodically to return the current status reagarding the autotagging process happening 
and reporting status to the SDK terminal
@param url:url which the request is sent : {self.automatic_analysis_url} in automatic_analysis_interface.py
@param unique_id: a unique id generated to identify which autotagging process to refer. 
@param headers: headers of the reqeust sent
"""


def get_status(url, unique_id, task, headers):
    (
        flag,
        print_status_flag,
        initialize_progress_bar,
        progress_bar_end,
        inference_flag,
        initialize_upload_progress_bar,
        start_upload,
    ) = (True, True, True, False, True, True, False)
    status_message = "Started Autoannotation"
    dot_count = 0
    state_start_end_flags = [[True, True], [True, True], [True, True], [True, True]]
    while flag:
        payload = {"unique_id": unique_id, "Task": task}
        try:
            response = requests.post(f"{url}/get_status", json=payload, headers=headers)
            status_code = response.status_code
            if status_code == 200:
                pass
                """ Okay to proceed """
            elif status_code == 204:
                print(f"No content return from this API call")
                return
            elif status_code == 401:
                error_obj = response.json()
                error = error_obj.get("error")
                message = error_obj.get("message")
                print(f"Error: {format(error)}")
                print(message)
                return
            else:
                print(f"Error occur with status code: {status_code}")
                return
        # Handle connection error
        except requests.exceptions.ConnectionError as e:
            print(f"Error: {format(e)}")
            print(f"Failed to connect with Meta Lake Flask app")
            return
        # Handle timeout error
        except requests.exceptions.Timeout as e:
            print(f"Error: {format(e)}")
            print("Timeout error from Meta Lake Flask connection")
            return
        # Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print(f"Error: {format(e)}")
            print("HTTP error from Meta Lake Flask connection")
            return
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            return
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            return

        document = response.json()["status"]
        global insufficient_load
        if insufficient_load:
            flag = False
            print_status_flag = False
        # print(document)
        new_status_message = status_message
        if document == "NotFound":
            new_status_message = status_message
        else:
            if state_start_end_flags[3][0]:
                print("Started Creating Inference EndPoint")
                state_start_end_flags[3][0] = False
            if len(document["model_name_registered"]) == 1:
                print("Error occured while creating the inference endpoint")
                print(document["model_name_registered"][0])
                print_status_flag = False
                flag = False
            if len(document["collection_name_registered"]) == 1:
                print("")
                print(
                    "ERROR occured while trying to find layernext annotation project details"
                )
                print(document["collection_name_registered"][0])
                print_status_flag = False
                flag = False
                break
            if len(document["end_point_initialization"]) == 1:
                new_status_message = "Inference EndPoint Creating.. Stay Tuned"
            if len(document["logs"]) == 0:
                if len(document["end_point_initialization"]) == 2:
                    if document["end_point_initialization"][1] == "Ended":
                        if state_start_end_flags[3][1]:
                            print("Inference EndPoint Created!!!")
                            state_start_end_flags[3][1] = False
                        if state_start_end_flags[0][0]:
                            print("Started Downloading the Annotation Project")
                            state_start_end_flags[0][0] = False
                        new_status_message = "Downloading the Annotation Project files"
                    else:
                        print("Error occured while creating the inference endpoint")
                        print(document["end_point_initialization"][1])
                        print_status_flag = False
                        flag = False
            if len(document["logs"]) > 0 and inference_flag:
                print_status_flag = False
                if state_start_end_flags[0][1]:
                    print("Annotation Project Download Complete !!!")
                    state_start_end_flags[0][1] = False
                if state_start_end_flags[1][0]:
                    print("Started Auto Annotation Process")
                    state_start_end_flags[1][0] = False
                if document["logs"][0][:4] == "INFO":
                    if initialize_progress_bar:
                        constraint = document["number_of_files"]
                        pbar = tqdm(
                            total=constraint,
                            desc="Auto Annotation in progress ",
                            ncols=100,
                            unit="item",
                        )
                        initialize_progress_bar = False
                    if len(document["inferenced_files"]) > 0 and not start_upload:
                        if len(document["inferenced_files"]) < constraint:
                            second_len = len(document["inferenced_files"])
                            difference = second_len - pbar.n
                            pbar.update(difference)
                        else:
                            second_len = len(document["inferenced_files"])
                            difference = second_len - pbar.n
                            pbar.update(difference)
                            pbar.close()
                            print("Auto Annotation Process is Complete!!!")
                            print("Started Uploading Annotations to Files")
                            start_upload = True

                    if (
                        start_upload
                        and initialize_upload_progress_bar
                        and len(document["post_process_state"]) == 2
                    ):
                        constraint_upload = document["number_of_resulted_json"]
                        pbar_upload = tqdm(
                            total=constraint_upload,
                            desc="Annotations Upload in progress   ",
                            ncols=100,
                            unit="item",
                        )
                        initialize_upload_progress_bar = False
                    if (
                        start_upload
                        and len(document["uploaded_jsons"]) > 0
                        and len(document["post_process_state"]) == 2
                    ):
                        if len(document["uploaded_jsons"]) < constraint_upload:
                            second_len = len(document["uploaded_jsons"])
                            difference = second_len - pbar_upload.n
                            pbar_upload.update(difference)
                        else:
                            second_len = len(document["uploaded_jsons"])
                            difference = second_len - pbar_upload.n
                            pbar_upload.update(difference)
                            pbar_upload.close()
                            progress_bar_end = True
                            inference_flag = False
                else:
                    new_status_message = (
                        "Error Occured while Downloading the Annotation Project"
                    )
                    flag = False
            if len(document["metadata_upload"]) == 1:
                print("Error occured while trying to upload Annotations for files")
                print(document["metadata_upload"][0])
                pbar_upload.close()
                print_status_flag = False
                flag = False
            if len(document["predictor_invoke"]) == 1:
                print("Error occured while invoking inference endpoint")
                print(document["predictor_invoke"][0])
                pbar.close()
                print_status_flag = False
                flag = False
            if len(document["logs"]) == 2 and progress_bar_end:
                print_status_flag = True
                if document["logs"][1][:4] == "INFO":
                    print_status_flag = False
                    new_status_message = ""
                else:
                    print("Error Occured while Generating Annotations")
                    flag = False
            if len(document["logs"]) > 2 and progress_bar_end:
                if document["logs"][2][:4] == "INFO":
                    print("Uploading Annotations is Complete!!!")
                    print("Successfully Completed the Process \u2714 \u2714 \u2714")
                    operation_id = document["operation_id"]
                    print("")
                    print(f"Annotation Operation ID of the process :{operation_id}")
                    flag = False
                else:
                    print("Error occured while updating Annotations")
                    flag = False

        if new_status_message != status_message:
            status_message = new_status_message
            dot_count = 0
        dots = "." * (dot_count % 4)
        padded_message = f"{status_message} {dots}".ljust(100)
        if print_status_flag:
            print(f"{padded_message}", end="\r", flush=True)

        dot_count += 1

        time.sleep(1)


def get_status_sam(url, unique_id, task, headers):
    (
        flag,
        print_status_flag,
        initialize_progress_bar,
        progress_bar_end,
        inference_flag,
        initialize_upload_progress_bar,
        start_upload,
    ) = (True, True, True, False, True, True, False)
    status_message = "Started Auto Annotation Embedding Generation"
    dot_count = 0
    state_start_end_flags = [[True, True], [True, True], [True, True], [True, True]]
    while flag:
        payload = {"unique_id": unique_id, "Task": task}
        response = requests.post(f"{url}/get_status", json=payload, headers=headers)
        document = response.json()["status"]
        global insufficient_load
        if insufficient_load:
            flag = False
            print_status_flag = False
        # print(document)
        new_status_message = status_message
        if document == "NotFound":
            new_status_message = status_message
        else:
            if state_start_end_flags[3][0]:
                print(
                    "Started Creating Inference EndPoint for Annotation Embedding Generation"
                )
                state_start_end_flags[3][0] = False
            if len(document["model_name_registered"]) == 1:
                print("Error occured while creating the inference endpoint")
                print(document["model_name_registered"][0])
                print_status_flag = False
                flag = False
            if len(document["collection_name_registered"]) == 1:
                print("")
                print(
                    "ERROR occured while trying to find layernext annotation project details"
                )
                print(document["collection_name_registered"][0])
                print_status_flag = False
                flag = False
                break
            if len(document["end_point_initialization"]) == 1:
                new_status_message = "Inference EndPoint Creating.. Stay Tuned"
            if len(document["logs"]) == 0:
                if len(document["end_point_initialization"]) == 2:
                    if document["end_point_initialization"][1] == "Ended":
                        if state_start_end_flags[3][1]:
                            print("Inference EndPoint Created!!!")
                            state_start_end_flags[3][1] = False
                        if state_start_end_flags[0][0]:
                            print("Started Downloading the Annotation Project")
                            state_start_end_flags[0][0] = False
                        new_status_message = "Downloading the Annotation Project files"
                    else:
                        print("Error occured while creating the inference endpoint")
                        print(document["end_point_initialization"][1])
                        print_status_flag = False
                        flag = False
            if len(document["logs"]) > 0 and inference_flag:
                print_status_flag = False
                if state_start_end_flags[0][1]:
                    print("Annotation Project Download Complete !!!")
                    state_start_end_flags[0][1] = False
                if state_start_end_flags[1][0]:
                    print("Started Auto Annotation Embedding Generation Process")
                    state_start_end_flags[1][0] = False
                if document["logs"][0][:4] == "INFO":
                    if initialize_progress_bar:
                        constraint = document["number_of_files"]
                        pbar = tqdm(
                            total=constraint,
                            desc="Auto Annotation Embedding Generation in progress ",
                            ncols=100,
                            unit="item",
                        )
                        initialize_progress_bar = False
                    if len(document["inferenced_files"]) > 0 and not start_upload:
                        if len(document["inferenced_files"]) < constraint:
                            second_len = len(document["inferenced_files"])
                            difference = second_len - pbar.n
                            pbar.update(difference)
                        else:
                            second_len = len(document["inferenced_files"])
                            difference = second_len - pbar.n
                            pbar.update(difference)
                            pbar.close()
                            print(
                                "Auto Annotation Embedding Generation Process is Complete!!!"
                            )
                            print("Uploaded Generated Embeddings to Vector DB")
                            print(
                                "Successfully Completed the Process \u2714 \u2714 \u2714"
                            )
                            start_upload = True
                            flag = False
                else:
                    new_status_message = (
                        "Error Occured while Downloading the Annotation Project"
                    )
                    flag = False
            if len(document["predictor_invoke"]) == 1:
                print("Error occured while invoking inference endpoint")
                print(document["predictor_invoke"][0])
                pbar.close()
                print_status_flag = False
                flag = False
            if len(document["logs"]) == 2 and progress_bar_end:
                print_status_flag = True
                if document["logs"][1][:4] == "INFO":
                    print_status_flag = False
                    new_status_message = ""
                else:
                    print("Error Occured while Generating Annotation Embedding")
                    flag = False
        if new_status_message != status_message:
            status_message = new_status_message
            dot_count = 0
        dots = "." * (dot_count % 4)
        padded_message = f"{status_message} {dots}".ljust(100)
        if print_status_flag:
            print(f"{padded_message}", end="\r", flush=True)
        dot_count += 1
        time.sleep(1)


"""
combining about two processes as two threads to run them parallely
@param url:url which the request is sent : {self.automatic_analysis_url} in automatic_analysis_interface.py
@param payload:payload of the request sent
@param headers: headers of the reqeust sent
@param unique_id: a unique id generated to identify which autotagging process to refer. 
"""


def main_annotation(url, payload, headers, unique_id, task, auto_annotation_operation):
    request_thread = threading.Thread(target=send_request, args=(url, payload, headers))
    if auto_annotation_operation == "sam-text":
        status_thread = threading.Thread(
            target=get_status, args=(url, unique_id, task, headers)
        )
    else:
        status_thread = threading.Thread(
            target=get_status_sam, args=(url, unique_id, task, headers)
        )
    request_thread.start()
    status_thread.start()
    request_thread.join()
    # print("request thread finished")
    status_thread.join()
    # print("status thread finished")
