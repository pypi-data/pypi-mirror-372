import requests
import json
import traceback

from layernext.datalake.constants import Task
from .support import generate_unique_id
from .status_check_autoannotate_project import main_annotation
from .automatic_analysis_interface import AutomaticAnalysisInterface

"""
Class to initiate AutomaticAnalysisClientInterface(class which handles all the API request and responses reagrding to automatic analysis) and handle functions integrated to it
"""


class AutomaticAnalysis:

    def __init__(self, auth_token: str, automatic_analysis_url: str):
        self.auth_token = auth_token
        self.automatic_analysis_url = automatic_analysis_url
        self.automatic_analysis_interface = AutomaticAnalysisInterface(
            auth_token, automatic_analysis_url
        )

    """
    Making the payload and sending it to the given API endpoint in and handle responses in regarding to autotagging
    """

    def tagger_detail_send(
        self,
        application,
        collection_id,
        item_type,
        model_id,
        input_resolution,
        confidence_threshold,
        session_id,
        job_id,
        job_name,
        query,
        filters,
        inference_platform,
    ):
        task = Task.AUTO_TAGGING.value
        unique_id = generate_unique_id()
        payload = {
            "Application": application,
            "ItemType": item_type,
            "collectionId": collection_id,
            "ModelID": model_id,
            "UniqueID": unique_id,
            "InputResolution": input_resolution,
            "Confidence": confidence_threshold,
            "Task": task,
            "SessionId": session_id,
            "JobName": job_name,
            "Query": query,
            "Filters": filters,
            "InferencePlatform": inference_platform,
        }

        self.automatic_analysis_interface.main_analysis(payload, task)

    def annotater_detail_send(
        self,
        application,
        project_id,
        model_id,
        annotation_type,
        session_id,
        job_name,
        **kwargs
    ):
        task = Task.AUTO_ANNOTATION.value
        unique_id = generate_unique_id()
        auto_annotation_op = (
            kwargs["auto_annotation_operation"]
            if "auto_annotation_operation" in kwargs
            else "user-model"
        )
        payload = {
            "Application": application,
            "ProjectID": project_id,
            "ModelID": model_id,
            "UniqueID": unique_id,
            "Prompt": kwargs["prompt"] if "prompt" in kwargs else [],
            "AnnotationType": annotation_type,
            "Confidence": (
                kwargs["confidence_threshold"]
                if "confidence_threshold" in kwargs
                else 0.5
            ),
            "Autoannotation_op": auto_annotation_op,
            "Labels": kwargs["labels"] if "labels" in kwargs else {},
            "Task": task,
            "SessionId": session_id,
            "JobName": job_name,
        }

        self.automatic_analysis_interface.main_analysis(payload, task)

    def embedding_detail_send(
        self,
        collection_id,
        model_id,
        application,
        item_type,
        query,
        filters,
        session_id,
        job_id,
        job_name,
        inference_platform,
    ):

        task = Task.EMBEDDING.value
        unique_id = generate_unique_id()
        payload = {
            "collectionId": collection_id,
            "ModelID": model_id,
            "UniqueID": unique_id,
            "Task": task,
            "Application": application,
            "ItemType": item_type,
            "Query": query,
            "Filters": filters,
            "SessionId": session_id,
            "JobName": job_name,
            "InferencePlatform": inference_platform,
        }

        self.automatic_analysis_interface.main_analysis(payload, task)
