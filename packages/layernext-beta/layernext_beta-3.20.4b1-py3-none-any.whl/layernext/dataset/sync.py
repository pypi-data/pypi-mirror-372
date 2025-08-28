"""
Script to download images and text files to local machine and generate path file
"""

import datetime
import traceback
import requests
import json
import os
from multiprocessing.pool import ThreadPool
from zipfile import ZipFile

DownloadDataset = 9
DownloadCollection = 10
DownloadProject = 11
page_size = 250


inProgress = 1
completed = 2
queued = 3
failed = 4


# # IP+port or url of the server # (eg: https://qa.deepzea.com)
# serverUrl = 'http://localhost:8080' # default


class DatasetSync:
    def __init__(self, encoded_key_secret: str, server_url: str, download_path: str):
        self.failed_downloads_present = False
        self.encoded_key_secret = encoded_key_secret
        self.server_url = server_url
        self.local_download_abs_dir = download_path

    def create_or_update_job(self, payload):

        call_url = f"{self.server_url}/datalake/api/job/updateJob/basicAuthRequest"
        hed = {"Authorization": "Basic " + self.encoded_key_secret}

        try:
            response = requests.post(url=call_url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
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
    method to get item URL list from layerX (per page)
    @params - callUrl=(Url to get itemlist of given group and version from layernext), payload=(pageNo,pageSize)
    @returns - response=(response from layerX containing URL list)"""

    def get_data_from_server(self, call_url, payload):

        hed = {"Authorization": "Basic " + self.encoded_key_secret}

        print(hed)
        print(call_url)
        try:
            call_response = requests.get(
                call_url, params=payload, headers=hed, timeout=60
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.Timeout,
        ) as e:

            self.create_or_update_job(
                {
                    "jobName": f"{self.job_type_string} Download",
                    "sessionId": self.session_id,
                    "jobType": self.download_type,
                    "progress": 0,
                    "status": inProgress,
                    "jobSpecificDetails": {
                        "errorList": f"Error connecting to layernext payload: {str(payload)}"
                    },
                }
            )
            print(f"Error connecting to layernext")
            print(e.errno)
            print(
                "We are facing a problem with the network, please retry to download missing items"
            )
            quit()
        print(call_response, flush=True)
        response = call_response.json()
        return response

    """
    Method to download files
    @params: fileData=(data including url of file), downloadLocation=(file path to save downloaded file) """

    def download_file(self, file_data, download_location, is_media_include):
        is_media_file = False
        if "isMediaFile" in file_data:
            is_media_file = file_data["isMediaFile"]
        if is_media_include == False and is_media_file == True:
            return
        # download files from newly added paths
        # print('Downloading file '+fileData["fileName"])
        r = requests.get(file_data["fileUrl"], timeout=25)
        download_path = download_location
        # print(downloadLocation)
        with open(download_path, "wb") as f:
            f.write(r.content)

    """
     handle download for a single dataset item (image and textfile)
     @params: arg_list=[fileData=(data of file), identifier=(unique identifier name for the dataset version)]
     @returns: {False<when download failed>, arg_list<from params>}
           or  {
                   True<when download success>,
                   {textFileImagePathData={imagePath=(file path of downloaded item), pathFileName=("training path file" name - stores paths of downloaded images used for training)}}
               } """

    def handle_one_download(self, arg_list):
        file_data = arg_list[0]
        is_media_include = file_data["is_media_include"]
        # //print(fileData)
        # identifier = arg_list[1]
        # ---------------------

        formatted_write_key = file_data["fileName"]
        file_path = (
            f'{file_data["fileDownloadFolderLocation"]}/' + file_data["fileName"]
        )

        # if item have to be extracted (a zip file)
        # if "isUnzipRequired" in file_data:
        #     folder_path_absolute = os.path.abspath(f'./{self.data_directory_name}/' + file_path)
        #     file_path = f'{file_path}.zip'

        # if self.local_download_abs_dir != None:
        # absPath = os.path.abspath(f'./{self.data_directory_name}/' + file_path)
        # folder_path_absolute = os.path.abspath(os.path.join(self.local_download_abs_dir, self.data_directory_name,file_path))

        if self.local_download_abs_dir != None:

            # if item have to be extracted (a zip file)
            if "isUnzipRequired" in file_data:
                folder_path_absolute = os.path.join(
                    self.local_download_abs_dir, self.data_directory_name, file_path
                )
                file_path = f"{file_path}.zip"
            # If custom path is given instead of current directory
            _file_path = os.path.join(
                self.local_download_abs_dir
                + f"/{self.data_directory_name}/"
                + file_path
            )
            _folder_path_absolute = os.path.abspath(_file_path)
            file_path = os.path.join(self.local_download_abs_dir, _folder_path_absolute)
            file_path_absoulute = file_path
        else:
            # if item have to be extracted (a zip file)
            if "isUnzipRequired" in file_data:
                folder_path_absolute = os.path.abspath(
                    f"./{self.data_directory_name}/" + file_path
                )
                file_path = f"{file_path}.zip"
            file_path_absoulute = os.path.abspath(
                f"./{self.data_directory_name}/" + file_path
            )

        if "writingPathFileName" in file_data:
            # write to a annotation file path list
            path_file_name = file_data["writingPathFileName"]
            text_file_image_path_data = (file_path_absoulute, path_file_name)
        else:
            text_file_image_path_data = None

        if "rawAnnotations" in file_data:
            # append raw annotations to json
            self.raw_data_arr.append(file_data["rawAnnotations"])

        if not os.path.exists(file_path_absoulute):
            # download files
            try:
                if "fileUrl" in file_data:
                    self.download_file(
                        file_data, file_path_absoulute, is_media_include
                    )  # download image
            except Exception as e:
                print(f"Failed downloading - {formatted_write_key}")
                print(e)
                return (False, arg_list)

            # if item have to be extracted (a zip file)
            if "isUnzipRequired" in file_data:
                with ZipFile(file_path_absoulute, "r") as zObject:
                    zObject.extractall(path=folder_path_absolute)
                os.remove(file_path_absoulute)

            # If item is not available in the syncdatafile (file hasn't downloaded before)
            if is_media_include == True:
                print("Downloded item - " + formatted_write_key)

            # return fileName and textFileName to update the textfile
            return (True, text_file_image_path_data)

        else:
            print("Item already exists, OK ", file_data["fileName"])
            return (True, text_file_image_path_data)

    """
    main method to download items and update datafiles
    @params: dataList=(response from layerX containing URL list) """

    def download_page(self, data_list, is_media_include):
        arg_list = []
        for val in data_list["resourceArray"]:
            val["is_media_include"] = is_media_include
            arg_list.append([val, data_list["identifier"]])

        # Download items in parallel
        print("starting page download")
        with ThreadPool(10) as p:
            for res in p.imap(self.handle_one_download, arg_list):
                is_downloded = res[0]
                download_data = res[1]
                if not is_downloded:
                    # try again to download the failed download
                    print(f"Retrying Download - {download_data[0]['fileName']}")
                    download_data["is_media_include"] = is_media_include
                    res = self.handle_one_download(download_data)
                    is_downloded = res[0]
                    download_data = res[1]

                if is_downloded:
                    # if file is downloaded, write it to master csv
                    text_file_image_path_data = download_data

                    if text_file_image_path_data is not None:
                        # write image file path to train text file
                        image_path = text_file_image_path_data[0]
                        path_file_name = text_file_image_path_data[1]
                        text_path_file_location = os.path.join(
                            self.data_directory_name, f"{path_file_name}.txt"
                        )
                        image_path_location = os.path.join(
                            self.data_directory_name, text_file_image_path_data[0]
                        )
                        if self.local_download_abs_dir != None:
                            text_path_file_location = os.path.join(
                                self.local_download_abs_dir,
                                self.data_directory_name,
                                f"{path_file_name}.txt",
                            )
                        with open(
                            text_path_file_location, "a+", newline=""
                        ) as train_txt_file:
                            train_txt_file.write(image_path_location + "\n")
                        p.close()
                    self.create_or_update_job(
                        {
                            "jobName": f"{self.job_type_string} Download",
                            "sessionId": self.session_id,
                            "jobType": self.download_type,
                            "progress": 0,
                            "status": inProgress,
                            "jobSpecificDetails": {},
                        }
                    )
                else:
                    print(f"Retrying Failed! - {download_data[0]['fileName']}")
                    self.create_or_update_job(
                        {
                            "jobName": f"{self.job_type_string} Download",
                            "sessionId": self.session_id,
                            "jobType": self.download_type,
                            "progress": 0,
                            "status": inProgress,
                            "jobSpecificDetails": {
                                "errorList": f"Retrying Failed! - {download_data[0]['fileName']}"
                            },
                        }
                    )
                    self.failed_downloads_present = True
                    p.close()

        print("page download done")

    """
    Method to create required directories for file download """

    def initiate_download(self, response, page_no, is_media_include):

        try:
            print("data format: ", response["format"])

            # global self.dataDirectoryName  # folder to download image and text files
            # create a folder with dataset groupname
            self.data_directory_name = response["groupUniqueName"]
            data_directory_path = f"./{self.data_directory_name}"
            if self.local_download_abs_dir != None:
                # If custom path is given for download
                data_directory_path = os.path.join(
                    self.local_download_abs_dir, data_directory_path
                )

            if page_no == 1 or page_no == 0:
                print("1st page")
                # create required files and directories
                if not os.path.exists(data_directory_path):
                    os.makedirs(data_directory_path)
                    print(f"Created {self.data_directory_name} folder")

                # get raw json file name (if applicable)
                if "rawFileName" in response:
                    self.json_file_name = response["rawFileName"]

            # create required directories
            for directory in response["creatableDirectories"]:
                dir_path = os.path.join(data_directory_path, directory)
                if not os.path.exists(dir_path) and (
                    is_media_include == True or response["format"] == "YOLO Darknet"
                ):
                    os.makedirs(dir_path)
                    print(f"Created folder - {dir_path}")

            # updateVersionData(response)
            self.download_page(response, is_media_include)
        except Exception as e:
            self.create_or_update_job(
                {
                    "jobName": f"{self.job_type_string} Download",
                    "sessionId": self.session_id,
                    "jobType": self.download_type,
                    "progress": 0,
                    "status": inProgress,
                    "jobSpecificDetails": {
                        "errorList": f"Error create required directories for file download at page no: {page_no}"
                    },
                }
            )

    """
    method to get url list from server and execute the main script for all pages
    @params - callUrl (Url to get itemlist of given group and version from layernext), pageNo 
    @params - status_list, is_annotated_only - use only for download annotation from annotation studio project
    """

    def get_all_pages(
        self,
        call_url,
        page_no,
        status_list=[],
        is_annotated_only=False,
        project_id_list=[],
        operation_id_list=[],
        annotation_type="all",
        is_media_include=True,
    ):
        if status_list == None:
            status_list = []
        payload = {
            "pageNo": page_no,
            "pageSize": page_size,
            "statusList": json.dumps(status_list),
            "isAnnotatedOnly": is_annotated_only,
            "projectIdList": json.dumps(project_id_list),
            "operationIdList": json.dumps(operation_id_list),
            "annotationType": annotation_type,
            "sessionId": self.session_id,
        }
        response = self.get_data_from_server(call_url, payload)
        print("Downloading page no: " + str(page_no))
        if "data" in response and "identifier" in response["data"]:
            response_data = response["data"]
            self.json_file_name = response_data["rawFileName"]
            # Direct the response to download files
            self.initiate_download(response_data, page_no, is_media_include)

            # recursively call this again to get next page
            if response_data["nextPage"] == True:
                next_page_no = int(page_no) + 1
                self.get_all_pages(
                    call_url,
                    next_page_no,
                    status_list,
                    is_annotated_only,
                    project_id_list,
                    operation_id_list,
                    annotation_type,
                )
            print("Download Complete")
            if self.failed_downloads_present:
                print(
                    "Unfortunately we failed to download everything, please retry to download missing items"
                )
                self.create_or_update_job(
                    {
                        "jobName": f"{self.job_type_string} Download",
                        "sessionId": self.session_id,
                        "jobType": self.download_type,
                        "progress": 0,
                        "status": failed,
                        "jobSpecificDetails": {
                            "errorList": f"Unfortunately we failed to download everything, please retry to download missing items in page no: {page_no}"
                        },
                    }
                )
            else:
                self.create_or_update_job(
                    {
                        "jobName": f"{self.job_type_string} Download",
                        "sessionId": self.session_id,
                        "jobType": self.download_type,
                        "progress": 0,
                        "status": completed,
                        "jobSpecificDetails": {},
                    }
                )

        else:
            self.create_or_update_job(
                {
                    "jobName": f"{self.job_type_string} Download",
                    "sessionId": self.session_id,
                    "jobType": self.download_type,
                    "progress": 100,
                    "status": completed,
                    "jobSpecificDetails": {
                        "warning": f"No data recieved from remote for given group and/or version in page no: {page_no}"
                    },
                }
            )
            print("No data recieved from remote for given group and/or version")

    # main script starter
    """
    Download dataset
    From dataset manager
    @param version_id - id of dataset version 
    @param export_type - dataset export format """

    def download_dataset(
        self, version_id: str, export_type: str, is_media_include: True
    ):
        self.session_id = str(datetime.datetime.now().timestamp())
        self.download_type = DownloadDataset
        self.job_type_string = "Dataset"
        # get dataset url data from server
        _base_url = f"{self.server_url}/dataset/api/dataset/getVersionData/"
        _call_url = f"{_base_url}{version_id}/{export_type}/"
        # start operation
        self.get_all_pages(_call_url, 1, [], False, [], [], "all", is_media_include)
        # quit()

    # main script starter
    """
    Download collection annotations
    From datalake - Both ground trugh
    @param collection_id - id of dataset version  
    @param model_id - Optional: id of the model (same operation_id given in upload annotations) 
    if we need annotations for that specific model """

    def download_collection(
        self, collection_id: str, annotation_type, operation_id_list, is_media_include
    ):

        if annotation_type is None:
            annotation_type = "all"

        if operation_id_list is None:
            operation_id_list = []

        if (
            annotation_type != "all"
            and annotation_type != "human"
            and annotation_type != "machine"
        ):
            print(
                "invalid annotation_type. annotation_type must be 'all', 'human', or 'machine' "
            )
            return {"isSuccess": False, "error": "annotation_type"}

        # get collection url data from server
        _base_url = f"{self.server_url}/datalake/api/client/getAnnotations/"
        # Pass the model_id only if specified
        # if model_id is None:
        _call_url = f"{_base_url}{collection_id}/collection"
        # else:
        #     _call_url = f'{_base_url}{collection_id}/collection?operationId={model_id}'

        # define annotation json object
        self.raw_data_arr = []
        self.json_file_name = "default_json_filename.json"

        self.session_id = str(datetime.datetime.now().timestamp())
        self.download_type = DownloadCollection
        self.job_type_string = "Collection"
        # start operation
        self.get_all_pages(
            _call_url,
            0,
            None,
            None,
            None,
            operation_id_list,
            annotation_type,
            is_media_include,
        )

        # save json (anno list) to a file
        _raw_annotations = {"images": self.raw_data_arr}
        json_raw_annotations = json.dumps(_raw_annotations, indent=2)
        _file_path = os.path.join(self.data_directory_name, self.json_file_name)

        if self.local_download_abs_dir != None:
            # custom path is given instead of current directory
            _file_path = os.path.join(self.local_download_abs_dir, _file_path)

        with open(_file_path, "w") as outfile:
            outfile.write(json_raw_annotations)
        print("Created RAW annotation file")
        # quit()

    """
    Download project annotations
    From datalake - Ground truth data
    @param project_id 
    """

    def download_project_v2(
        self, project_id_list, status_list, is_annotated_only, is_media_include
    ):

        # get collection url data from server
        _call_url = f"{self.server_url}/studio/api/client/projects/getAnnotations"

        # define annotation json object
        self.raw_data_arr = []
        self.json_file_name = "default_json_filename.json"

        self.session_id = str(datetime.datetime.now().timestamp())
        self.download_type = DownloadProject
        self.job_type_string = "Project"

        # start operation
        self.get_all_pages(
            _call_url,
            0,
            status_list,
            is_annotated_only,
            project_id_list,
            [],
            "all",
            is_media_include,
        )

        # save json (anno list) to a file
        _raw_annotations = {"images": self.raw_data_arr}
        json_raw_annotations = json.dumps(_raw_annotations, indent=2)
        _file_path = os.path.join(self.data_directory_name, self.json_file_name)
        if self.local_download_abs_dir != None:
            # custom path is given instead of current directory
            _file_path = os.path.join(self.local_download_abs_dir, _file_path)

        with open(_file_path, "w") as outfile:
            outfile.write(json_raw_annotations)
        print("Created RAW annotation file")


# sample run command:
# python3 sync.py <url> <version ID> <format type> <access token>
