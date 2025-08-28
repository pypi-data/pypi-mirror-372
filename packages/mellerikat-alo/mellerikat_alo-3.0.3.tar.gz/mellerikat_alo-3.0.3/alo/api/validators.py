from typing import Optional, Dict, Any
import json
import logging
from .models import ModelMetadata, DetectionInput
from .error_handlers import APIError

logger = logging.getLogger(__name__)

def validate_metadata(metadata: Optional[str]) -> tuple[Optional[ModelMetadata], Optional[Dict[str, Any]]]:
    """메타데이터를 검증하고 파싱하는 함수"""
    if not metadata:
        return None, None
        
    try:
        metadata_dict = json.loads(metadata)
        metadata_obj = ModelMetadata(**metadata_dict)
        return metadata_obj, metadata_dict
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Invalid metadata format: {str(e)}")
        return None, None

def validate_config(config: str) -> Dict[str, Any]:
    """설정 데이터를 검증하고 파싱하는 함수"""
    try:
        return json.loads(config)
    except json.JSONDecodeError:
        logger.warning("Invalid config format, using empty config")
        return {}

def validate_detection_input(data: DetectionInput) -> None:
    """DetectionInput 데이터를 검증하는 함수"""
    if not data.input_data:
        raise APIError("Input data is required", 400)
        
    if data.input_data.image:
        validate_image_data(data.input_data.image)
        
    if data.input_data.annotation_bbox:
        validate_bbox_data(data.input_data.annotation_bbox)
        
    if data.input_data.classes:
        validate_classes_data(data.input_data.classes)

def validate_image_data(image_data: Any) -> None:
    """이미지 데이터를 검증하는 함수"""
    required_fields = ["type", "shape", "dtype", "data"]
    for field in required_fields:
        if not hasattr(image_data, field):
            raise APIError(f"Image data missing required field: {field}", 400)

def validate_bbox_data(bbox_data: Any) -> None:
    """바운딩 박스 데이터를 검증하는 함수"""
    required_fields = ["type", "shape", "dtype", "data"]
    for field in required_fields:
        if not hasattr(bbox_data, field):
            raise APIError(f"Bounding box data missing required field: {field}", 400)

def validate_classes_data(classes: list) -> None:
    """클래스 데이터를 검증하는 함수"""
    if not isinstance(classes, list):
        raise APIError("Classes must be a list", 400)