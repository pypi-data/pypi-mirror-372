import tarfile
import io
import os
import time
import random
from tqdm import tqdm
import os
import yaml

"""
support functions to help in automatic_analysis tasks
"""

"""
Make tar files of inputted model folders and Upload tar files for Datalake collection automatic_analysis_models collection and return the stored location information
@param source_dir: path of the model folder which needed to be uploaded
@param model_id:id/name of the model which is registered in the datalake
@param _datalake_client: datalake_client instance in order to acquire datalake SDK s inside this function
"""


def make_tarfile_in_memory(source_dir, model_id, _datalake_client):
    client = _datalake_client
    tar_stream = io.BytesIO()
    print("Started compressing...")
    total_files = sum([len(files) for _, _, files in os.walk(source_dir)])
    with tarfile.open(fileobj=tar_stream, mode="w:gz") as tar:
        cwd = os.getcwd()
        os.chdir(source_dir)
        pbar = tqdm(total=total_files, desc="Compressing..", dynamic_ncols=True)
        for root, dirs, files in os.walk("."):
            for file_ in files:
                file_path = os.path.join(root, file_)
                tar.add(file_path, arcname=file_path)
                pbar.update(1)
        pbar.close()
        os.chdir(cwd)
    tar_stream.seek(0)
    print("Compressing Completed")
    temp_path = f"./{model_id}.tar.gz"
    with open(temp_path, "wb") as f:
        f.write(tar_stream.read())
    result = client.file_upload(
        temp_path,
        7,
        "automatic_analysis_models",
        meta_data_object={},
        meta_data_override=False,
        storage_prefix_path=None,
    )
    client.wait_for_job_complete(result["job_id"])
    datalake_unique_name = result["unique_name"]
    path_details = client.get_item_details(
        datalake_unique_name, {"storagePath": True, "bucketName": True}
    )
    storage_url = path_details["url"]
    bucket_name = path_details["bucketName"]
    object_key = path_details["storagePath"]
    if os.path.exists(f"{source_dir}/label_list.yaml"):
        with open(f"{source_dir}/label_list.yaml", "r") as stream:
            try:
                data = yaml.safe_load(stream)
                label_list = data["label_list"]
            except yaml.YAMLError as exc:
                print(exc)
    else:
        label_list = []
    files = os.listdir(source_dir)
    pt_files = [f for f in files if (f.endswith(".pt") or f.endswith(".pth"))]
    if pt_files:
        model_name = pt_files[0]
        print(f"The pytorch file is: {model_name}")
    else:
        model_name = "test.pt"
        print("No pytorch files found")
    os.remove(temp_path)
    return storage_url, bucket_name, object_key, label_list, model_name


"""
Generate a unique ID based on the time the instance is initiated and return that ID in order to support status reporting
"""


def generate_unique_id():
    timestamp = int(time.time() * 1000)
    random_part = random.randint(0, 9999)

    unique_id = f"{timestamp:013d}{random_part:04d}"
    return unique_id


def validate_input_prompt(input_data):
    if not isinstance(input_data, list):
        raise ValueError("Input for input_prompt should be a list.")
    for item in input_data:
        if not isinstance(item, dict):
            raise ValueError(
                "Each item in the list in input_prompt should be a dictionary."
            )
        if "label" not in item:
            raise ValueError(
                "Missing 'label' key in one of the dictionaries in input_promt."
            )
        if "description" not in item:
            raise ValueError(
                "Missing 'description' key in one of the dictionaries in input_prompt."
            )


def validate_input_annotation_type(input_string):
    if not isinstance(input_string, str):
        raise ValueError("Input for annotation_type should be a string.")
    if input_string not in ["bbox", "segment"]:
        raise ValueError(
            "Input for annotation_type should be either 'bbox' or 'segment'."
        )


def validate_confidence(value):
    if not isinstance(value, float):
        raise ValueError("confidence_threshold Input should be a float.")
    if value < 0 or value > 1:
        raise ValueError("confidence_threshold Input float should be between 0 and 1.")


def validate_resolution_input(value):
    if not isinstance(value, tuple):
        raise ValueError("input_resolution Input should be a tuple.")
    if len(value) != 2:
        raise ValueError("input_resolution Input Tuple should have exactly two values.")
    if not all(isinstance(x, int) for x in value):
        raise ValueError("input_resolution Input's both values should be integers.")


def validate_task(value):
    valid_strings = ["auto_tagging", "embedding", "auto_annotation"]
    if value not in valid_strings:
        raise ValueError(f"task Input must be one of {valid_strings}.")
