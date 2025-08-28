from pathlib import Path
import json
import numpy as np
from PIL import Image
import io
import base64
import tarfile
import shutil
import logging
from typing import Optional, List, Any, Dict, Union

from .models import SerializedData, ModelMetadata

logger = logging.getLogger(__name__)

def prepare_model_directory(model_path: str) -> Path:
    """모델 디렉토리를 준비하는 함수"""
    model_path = Path(model_path)
    if model_path.exists():
        logger.info(f"Cleaning existing model directory: {model_path}")
        for item in model_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    else:
        model_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created model directory: {model_path}")
    return model_path

async def save_file(contents: bytes, file_path: Path) -> None:
    """파일을 저장하는 함수"""
    with open(file_path, "wb") as f:
        f.write(contents)

def save_metadata(metadata_obj: ModelMetadata, metadata_dict: dict, model_path: Path) -> None:
    """메타데이터를 저장하는 함수"""
    metadata_path = model_path / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata_dict, f, indent=2)

def save_config(config_dict: dict, model_path: Path) -> None:
    """설정을 저장하는 함수"""
    config_path = model_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config_dict, f, indent=2)

def clear_directory(directory_path: Path) -> None:
    """디렉토리를 비우는 함수"""
    for item in directory_path.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

def deserialize_data(data: SerializedData) -> tuple[Any, str]:
    """직렬화된 데이터를 역직렬화하는 함수

    Returns:
        tuple: (역직렬화된 데이터, 저장 형식)
        저장 형식은 'numpy', 'json', 'pickle' 중 하나
    """
    if data.type in ["numpy", "tensor"]:

        if isinstance(data.data, str):
            decoded_data = base64.b64decode(data.data)
            result = np.frombuffer(decoded_data, dtype=data.dtype).reshape(data.shape)
        else:
            result = np.array(data.data, dtype=data.dtype).reshape(data.shape)

        return result, "numpy"
    if data.type == "byte_array":
        decoded_data = base64.b64decode(data.data)

        if data.format == "raw":
            result = np.frombuffer(decoded_data, dtype=data.dtype).reshape(data.shape)
        else:
            result = np.array(Image.open(io.BytesIO(decoded_data)))

        return result, "numpy"
    if data.type == "pickle":
        import pickle
        decoded_data = base64.b64decode(data.data)
        result = pickle.loads(decoded_data)
        return result, "pickle"
    raise ValueError(f"Unsupported data type: {data.type}")

def save_image_data(image_data: SerializedData, data_path: Path) -> None:
    """이미지 데이터를 저장하는 함수"""
    #image_array = deserialize_data(image_data)
    image_array, _ = deserialize_data(image_data)
    image_file = data_path / "image.npy"
    np.save(image_file, image_array)

    try:
        pil_image = Image.fromarray(image_array)
        image_jpeg = data_path / "image.jpeg"
        pil_image.save(image_jpeg, "JPEG")
    except Exception as e:
        logger.warning(f"Could not save as image file: {e}")

def save_bbox_data(bbox_data: SerializedData, data_path: Path) -> None:
    """바운딩 박스 데이터를 저장하는 함수"""
    bbox_data_result, save_format = deserialize_data(bbox_data)

    if save_format == "numpy":
        bbox_file = data_path / "annotation_bbox.npy"
        np.save(bbox_file, bbox_data_result)
    elif save_format == "json":
        bbox_file = data_path / "annotation_bbox.json"
        with open(bbox_file, "w") as f:
            json.dump(bbox_data_result, f, indent=2)
    elif save_format == "pickle":
        bbox_file = data_path / "annotation_bbox.pkl"
        with open(bbox_file, "wb") as f:
            import pickle
            pickle.dump(bbox_data_result, f)

def save_classes_data(classes: List[Any], data_path: Path) -> None:
    """클래스 데이터를 저장하는 함수"""
    classes_file = data_path / "classes.json"
    with open(classes_file, "w") as f:
        json.dump([cls.model_dump() for cls in classes], f, indent=2)

def save_config_data(config: Any, metadata: Optional[Any], data_path: Path) -> None:
    """설정 데이터를 저장하는 함수"""
    config_file = data_path / "config.json"
    with open(config_file, "w") as f:
        json.dump({
            "config": config.model_dump(),
            "metadata": metadata.model_dump() if metadata else {}
        }, f, indent=2)

def extract_tar_file(tar_path: Path, extract_path: Path) -> None:
    """tar 파일을 압축 해제하는 함수"""
    try:
        with tarfile.open(tar_path) as tar_file:
            tar_file.extractall(path=extract_path)
    except tarfile.TarError as e:
        logger.error(f"Failed to extract tar file: {str(e)}")
        raise