from layernext.automatic_analysis.automatic_analysis_interface import (
    AutomaticAnalysisInterface,
)
from .automatic_analysis import AutomaticAnalysis
from .support import (
    make_tarfile_in_memory,
    validate_input_prompt,
    validate_input_annotation_type,
    validate_confidence,
    validate_task,
    validate_resolution_input,
)

"""
Class to initiate AutomaticAnalysisClient and handle functions integrated to it
"""


class AutomaticAnalysisClient:

    def __init__(self, encoded_key_secret: str, layernext_url: str):

        _automatic_analysis_url = f"{layernext_url}/analytics"
        self.encoded_key_secret = encoded_key_secret
        self.layernext_url = layernext_url
        self.automatic_analysis = AutomaticAnalysis(
            encoded_key_secret, _automatic_analysis_url
        )
        self.automatic_analysis_interface = AutomaticAnalysisInterface(
            encoded_key_secret, _automatic_analysis_url
        )

    """
    Upload models for Datalake collection automatic_analysis_models and send the stored location details in to flask app
    @param input_model_path: path of the model folder which needed to be uploaded
    @param model_id        :id/name of the model which is registered in the datalake
    @param _datalake_client: datalake_client instance in order to acquire datalake SDK s inside this function
    @param task            : automatic analysis task which should the registering model will be used to
    """

    def register_model(self, input_model_path, model_id, _datalake_client, task):
        try:
            validate_task(task)
            storage_url, bucket_name, object_key, label_list, model_name = (
                make_tarfile_in_memory(input_model_path, model_id, _datalake_client)
            )
            self.automatic_analysis_interface.inference_model_upload(
                storage_url,
                bucket_name,
                object_key,
                model_id,
                label_list,
                model_name,
                task,
            )
        except ValueError as e:
            print(f"ValueError: {e}")

    """
    initiate the API call to the flask app to autotagging a given collection through tagger_detail_send
    @param collection_id         : id of the image or video collection
    @param model_id              : id/name of the model which is registered in the datalake
    @param input_resolution      : resolution of the frames which should be considered at inference(image or video)
    @param confidence_threshold  : confidence score to consider which objects/segments to consider for the proccedings
    """

    def model_tag_collection(
        self,
        collection_id,
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
        try:
            validate_confidence(confidence_threshold)
            validate_resolution_input(input_resolution)
            application = "collection_autotag"
            item_type = ""
            self.automatic_analysis.tagger_detail_send(
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
            )
        except ValueError as e:
            print(f"ValueError: {e}")

    """
    initiate the API call to the flask app to autotagging a given item type files through tagger_detail_send
    @param item_type            : "image", "video", "other", "image_collection", "video_collection", "other_collection", "dataset"
    @param model_id             : id/name of the model which is registered in the datalake
    @param input_resolution     : resolution of the frames which should be considered at inference(image or video)
    @param confidence_threshold : confidence score to consider which objects/segments to consider for the proccedings
    """

    def model_tag_population(
        self,
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
        try:
            application = "population_autotag"
            collection_id = ""
            validate_confidence(confidence_threshold)
            validate_resolution_input(input_resolution)
            self.automatic_analysis.tagger_detail_send(
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
            )
        except ValueError as e:
            print(f"ValueError: {e}")

    """
    auto annotating a given frames of an annotation project
    @param project_id           : annotation project ID which needs to be annotated
    @param prompt               : input prompt describing which labels to annotate and their descriptions
    @param annotation_type      : bounding box annotation or polygon segment annotation
    @param model_id             : id/name of the model which is registered in the datalake
    @param confidence_threshold : confidence score to consider which objects/segments to consider for the proccedings
    @auto_annotation_operation  : Operation to do , sam-text, sam-img-encoding
    """

    def model_annotate_collection(
        self,
        project_id,
        model_id,
        # prompt,
        annotation_type,
        # confidence_threshold,
        # auto_annotation_operation
        session_id,
        job_name,
        **kwargs,
    ):

        application = "collection_autoannotate"

        try:
            validate_input_annotation_type(annotation_type)
            if "prompt" in kwargs:
                validate_input_prompt(kwargs["prompt"])
            if "confidence_threshold" in kwargs:
                validate_confidence(kwargs["confidence_threshold"])
            self.automatic_analysis.annotater_detail_send(
                application,
                project_id,
                model_id,
                annotation_type,
                session_id,
                job_name,
                **kwargs,
            )
        except ValueError as e:
            print(f"ValueError: {e}")

    def prompt_infer_image(self, name, shape, **kwargs):

        try:
            self.automatic_analysis_interface.prompt_detail_send(name, shape, **kwargs)
        except ValueError as e:
            print(f"ValueError: {e}")

    """
    generate embedding for a given collection (image) and upload the embeddings to the vector database
    @param collection_id: id of the image.
    @param model_id:id/name of the model which is registered in the datalake
    """

    def embedding_model_inference_collection(
        self,
        collection_id,
        model_id,
        query,
        filters,
        session_id,
        job_id,
        job_name,
        inference_platform,
    ):

        application = "collection_embedding"
        item_type = ""
        return self.automatic_analysis.embedding_detail_send(
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
        )

    def model_embedding_population(
        self,
        item_type,
        model_id,
        query,
        filters,
        session_id,
        job_id,
        job_name,
        inference_platform,
    ):
        try:
            application = "population_embedding"
            collection_id = ""
            return self.automatic_analysis.embedding_detail_send(
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
            )
        except ValueError as e:
            print(f"ValueError: {e}")
