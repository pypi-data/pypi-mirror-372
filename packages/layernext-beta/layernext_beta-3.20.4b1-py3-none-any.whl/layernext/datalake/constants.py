# System Label Type
from enum import Enum

LABEL_CLASS = 1
LABEL_CLASS_WITH_ATTRIBUTES = 2
FILE_UPLOAD_THREADS = 10
SUB_FILE_LENGTH = 100


# Annotation Geometric Type
# LINE_ANNOTATION = 'line'
# POLYGON_ANNOTATION = 'polygon'
# BOX_ANNOTATION = 'rectangle'
class AnnotationShapeType(Enum):
    LINE_ANNOTATION = "line"
    POLYGON_ANNOTATION = "polygon"
    BOX_ANNOTATION = "rectangle"
    POINTS_ANNOTATION = "points"


# Operation Data Meta Updates
OPERATION_TYPE_ANNOTATION = 1
OPERATION_MODE_HUMAN = 1
OPERATION_MODE_AUTO = 2

# Request Batch Sizes
META_UPDATE_REQUEST_BATCH_SIZE = 1000

# Chunk size in multi-part upload: 100MB
MULTI_PART_UPLOAD_CHUNK_SIZE = 100 * 1024 * 1024

MAX_UPLOAD_RETRY_COUNT = 20

REMOVED_OBJECT_UPLOAD = "The file that was previously removed from this collection has already been attached to another collection"


class MediaType(Enum):
    VIDEO = 4
    IMAGE = 5
    OTHER = 7


class ObjectType(Enum):
    VIDEO = 1
    IMAGE = 2
    DATASET = 3
    VIDEO_COLLECTION = 4
    IMAGE_COLLECTION = 5
    OTHER = 6
    OTHER_COLLECTION = 7


class ItemType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    OTHER = "other"
    IMAGE_COLLECTION = "image_collection"
    VIDEO_COLLECTION = "video_collection"
    OTHER_COLLECTION = "other_collection"
    DATASET = "dataset"


class JobStatus(Enum):
    IN_PROGRESS = 1
    COMPLETED = 2
    QUEUED = 3
    FAILED = 4


class MetadataUploadType(Enum):
    BY_JSON = 1
    BY_META_OBJECT = 2


class AnnotationUploadType(Enum):
    BY_FILE_NAME = 1
    BY_STORAGE_PATH = 2
    BY_UNIQUE_NAME = 3
    BY_FILE_NAME_OR_UNIQUE_NAME = 4
    BY_JOB_ID = 5


class SortFieldName(Enum):
    DATE_MODIFIED = "date_modified"
    DATE_CREATED = "date_created"
    NAME = "name"
    SIZE = "size"
    VIDEO_INDEX = ("video_index",)
    TEXT_SCORE = "text_score"


class SortField(Enum):
    DATE_MODIFIED = 1
    DATE_CREATED = 2
    NAME = 3
    SIZE = 4
    VIDEO_INDEX = (6,)
    TEXT_SCORE = 7


class SortOrder(Enum):
    ASC = "ASC"
    DESC = "DESC"


class JobType(Enum):
    UPLOAD_EMBEDDING = 14
    GENERATE_EMBEDDING = 15
    GENERATE_AUTO_TAGGING = 16
    GENERATE_AUTO_ANNOTATION = 17
    UNKNOWN = -1


class Task(Enum):
    EMBEDDING = "embedding"
    AUTO_TAGGING = "auto_tagging"
    AUTO_ANNOTATION = "auto_annotation"
