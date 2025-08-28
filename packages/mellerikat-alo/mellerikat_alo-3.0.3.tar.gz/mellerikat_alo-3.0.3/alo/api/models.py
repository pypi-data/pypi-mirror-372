# models.py

from typing import Optional, List, Union, Dict, Any
from pydantic import BaseModel, Field

# 재사용 가능한 서브 모델 정의
class DataFormat(BaseModel):
    type: str
    dtype: str

class DetectionParams(BaseModel):
    params: Dict[str, Any] = Field(default_factory=dict)
    def __init__(self, **data):
        params_dict = {}
        extra_fields = [k for k in data.keys() if k != 'params']

        for field in extra_fields:
            params_dict[field] = data.pop(field)
        if 'params' in data and isinstance(data['params'], dict):
            data['params'].update(params_dict)
        else:
            data['params'] = params_dict

        super().__init__(**data)

# 주요 모델 정의
class ModelMetadata(BaseModel):
    name: str
    version: str
    framework: str
    description: str
    input_format: DataFormat
    output_format: DataFormat
    tags: List[str]

class AloRequest(BaseModel):
    name: Optional[str] = None
    mode: Optional[str] = "inference"
    computing: Optional[str] = "local"
    log_level: Optional[str] = "DEBUG"

class UploadResult(BaseModel):
    name: Optional[str] = ""
    version: Optional[str] = ""
    framework: Optional[str] = ""
    storage_url: str

class UploadMetadata(BaseModel):
    upload_time: str
    file_size_bytes: int
    estimated_processing_time_sec: int

class UploadResponse(BaseModel):
    status: str
    request_id: str
    model_id: str
    upload_status: str
    result: UploadResult
    metadata: UploadMetadata

class SerializedData(BaseModel):
    type: str
    shape: List[int]
    dtype: str
    format: Optional[str] = None 
    data: Union[List[float], List[int], str]

class Class(BaseModel):
    id: str
    name: str
    embedding_index: int

class Config(BaseModel):
    operation: str
    output_type: str
    params: DetectionParams

class Metadata(BaseModel):
    device_id: Optional[str] = None
    timestamp: Optional[str] = None

class InputData(BaseModel):
    image: Optional[SerializedData] = None
    annotation_bbox: Optional[SerializedData] = None
    classes: Optional[List[Class]] = None

class DetectionInput(BaseModel):
    input_data: InputData
    config: Config
    metadata: Optional[Metadata] = None

class UploadFileResponse(BaseModel):
    status: str
    request_id: str
    model_id: str
    upload_status: str
    result: UploadResult
    metadata: UploadMetadata