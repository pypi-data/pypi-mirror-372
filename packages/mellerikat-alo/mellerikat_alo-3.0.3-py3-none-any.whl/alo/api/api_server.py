import os
import uuid
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import pytz
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel

# alo server의 return 을 alo pipeline 으로 넘기게

from alo.model import settings
from .models import (
    ModelMetadata,
    AloRequest,
    UploadResult,
    UploadMetadata,
    UploadResponse,
    SerializedData,
    DetectionInput,
)
from .file_handlers import (
    prepare_model_directory,
    save_file,
    save_metadata,
    save_config,
    clear_directory,
    save_image_data,
    save_bbox_data,
    save_classes_data,
    save_config_data,
    extract_tar_file,
)
from .error_handlers import handle_exception, handle_api_error
from .validators import (
    validate_metadata,
    validate_config,
    validate_detection_input,
)

logger = logging.getLogger(__name__)

def create_app(run_function):
    """FastAPI 앱을 생성하고 설정하는 함수.

    Args:
        run_function (function): ALO 모델을 실행하는 함수

    Returns:
        FastAPI: 설정된 FastAPI 인스턴스
    """
    app = FastAPI(title="ALO API")

    @app.post("/api/v1/run")
    async def api_run(request: AloRequest):
        """API 엔드포인트 - ALO 실행을 트리거

        사용방법:
        - **request**: ALO 실행을 위한 요청 데이터

        응답:
        - **status**: 성공 여부
        - **message**: 처리 결과 메시지
        """
        logger.info(f"Received API request on /run: {request.model_dump(exclude_unset=True)}")
        try:
            args_dict = request.model_dump()
            args = argparse.Namespace(**args_dict)
            logger.debug(f"Calling registered run_function with args: {vars(args)}")
            run_function(args)
            logger.info("API request processed successfully.")
            return {"status": "success", "message": "ALO execution request processed."}
        except Exception as e:
            handle_api_error(e)

    @app.post("/api/v1/data/upload")
    async def upload_detection_data(data: DetectionInput):
        """이미지와 어노테이션 데이터를 업로드하고 처리하는 엔드포인트

        사용방법:
        - **data**: DetectionInput 형식의 요청 데이터

        응답:
        - **status**: 성공 여부
        - **request_id**: 요청 ID
        - **data_id**: 데이터 ID
        - **upload_status**: 업로드 상태
        - **result**: 업로드된 파일 정보
        - **metadata**: 제공된 메타데이터
        """
        try:
            validate_detection_input(data)
            request_id = generate_request_id()
            return await process_detection_data(data, request_id)
        except Exception as e:
            handle_exception(500, e, "Failed to process detection data")

    @app.post("/api/v1/models/upload/tar", response_model=UploadResponse)
    async def upload_tar_model(
        model_file: UploadFile = File(...),
        metadata: Optional[str] = Form(None),
        config: str = Form(default="{}")
    ):
        """tar 압축 파일과 메타데이터를 업로드하는 엔드포인트

        사용방법:
        - **model_file**: alo를 통해 학습한 train_artifacts에 model.tar.gz 형식의 모델 파일 (필수)
        - **metadata**: JSON 형식의 메타데이터 (선택)
        - **config**: JSON 형식의 추가 설정 (기본값: `{}`)

        응답:
        - **status**: 성공 여부
        - **request_id**: 요청 ID
        - **model_id**: 모델 ID
        - **filename**: 업로드된 파일 이름
        - **file_size**: 업로드된 파일의 크기 (바이트 단위)
        - **metadata**: 제공된 메타데이터
        - **timestamp**: 업로드된 시간
        - **framework**: 추정된 머신 러닝 프레임워크
        """
        try:
            request_id = generate_request_id()
            model_id = generate_model_id()

            metadata_obj, metadata_dict = validate_metadata(metadata)
            config_dict = validate_config(config)

            model_path = prepare_model_directory(settings.model_artifacts_path)
            model_file_path = model_path / model_file.filename

            contents = await model_file.read()
            await save_file(contents, model_file_path)

            extract_files_from_tar(model_file_path, model_path)

            if metadata_obj:
                save_metadata(metadata_obj, metadata_dict, model_path)
            save_config(config_dict, model_path)

            file_size = model_file_path.stat().st_size
            current_time = get_current_time()
            framework = detect_framework(model_file.filename)

            response = build_upload_response(request_id, model_id, model_file.filename, file_size, metadata_obj, current_time, framework)
            logger.info(f"Successfully uploaded tar model with ID {model_id}")

            return response
        except Exception as e:
            handle_exception(500, e, "Failed to upload tar model")

    @app.get("/api/v1/health")
    async def health_check():
        """서버의 건강 상태를 확인하는 엔드포인트

        응답:
        - **status**: 서버 상태 ("healthy")
        """
        return {"status": "healthy"}

    @app.post("/api/v1/data/upload_and_infer")
    async def upload_and_infer_detection_data(data: DetectionInput):
        """데이터 업로드 후 추론을 수행하는 엔드포인트

        사용방법:
        - **data**: DetectionInput 형식의 요청 데이터

        응답:
        - **status**: 성공 여부
        - **request_id**: 요청 ID
        - **data_id**: 데이터 ID
        - **upload_status**: 업로드 상태
        - **result**: 업로드된 파일 정보 및 추론 결과
        - **metadata**: 제공된 메타데이터 및 추론 시간
        """
        try:
            validate_detection_input(data)
            request_id = generate_request_id()

            upload_response = await process_detection_data(data, request_id)

            inference_start_time = get_current_time()

            exp_plan = settings.experimental_plan
            inference_args = exp_plan.solution.function["inference"].argument
            update_inference_args(inference_args, data.config.dict())

            # 기본 필수 파라미터 추가
            inference_args.update({
                "mode": "inference",
                "operation": data.config.operation,
                "output_type": data.config.output_type
            })

            args = argparse.Namespace(**inference_args)
            inference_results = run_function(args)

            inference_end_time = get_current_time()
            processing_time = calculate_processing_time(inference_start_time, inference_end_time)

            upload_response["inference_status"] = "completed"
            upload_response["result"] = upload_response["result"]
            upload_response["result"]["inference_results"] = {
                "detections": inference_results,
                "processing_time": processing_time
            }
            upload_response["metadata"]["inference_time"] = inference_end_time.isoformat()

            return upload_response
        except Exception as e:
            handle_exception(500, e, f"Failed to process detection data and perform inference: {str(e)}")

    logger.info("FastAPI app created with endpoints /api/v1/run, /api/v1/health.")
    return app

async def process_detection_data(data: DetectionInput, request_id: str) -> Dict[str, Any]:
    """데이터 처리 및 저장을 담당하는 함수

    Args:
        data (DetectionInput): 업로드된 감지 입력 데이터
        request_id (str): 요청 ID

    Returns:
        Dict[str, Any]: 처리된 데이터와 관련된 정보를 포함하는 응답 딕셔너리
    """
    try:
        data_id = generate_data_id()
        data_path = Path(settings.experimental_plan.solution.inference.dataset_uri[0].path)
        clear_directory(data_path)

        if data.input_data.image:
            save_image_data(data.input_data.image, data_path)

        if data.input_data.annotation_bbox:
            save_bbox_data(data.input_data.annotation_bbox, data_path)

        if data.input_data.classes:
            save_classes_data(data.input_data.classes, data_path)

        save_config_data(data.config, data.metadata, data_path)

        response = build_detection_response(request_id, data_id, data, data_path)
        return response
    except Exception as e:
        handle_exception(500, e, "Failed to process data")

def extract_files_from_tar(model_file_path: Path, model_path: Path) -> None:
    """tar 파일을 추출하는 함수

    Args:
        model_file_path (Path): tar 파일 경로
        model_path (Path): 추출될 위치

    Raises:
        HTTPException: tar 파일을 추출하는데 실패한 경우 예외 발생
    """
    try:
        extract_tar_file(model_file_path, model_path)
    except Exception as e:
        handle_exception(500, e, "Failed to extract tar file")

def detect_framework(filename: str) -> str:
    """파일 확장자를 기반으로 프레임워크를 감지하는 함수

    Args:
        filename (str): 파일 이름

    Returns:
        str: 감지된 머신 러닝 프레임워크
    """
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension in ['.pt', '.pth']:
        return 'pytorch'
    if file_extension in ['.h5', '.keras']:
        return 'tensorflow'
    if file_extension in ['.onnx']:
        return 'onnx'
    return 'etc'

def build_upload_response(request_id: str, model_id: str, filename: str, file_size: int, metadata_obj: ModelMetadata, current_time: str, framework: str) -> UploadResponse:
    """업로드 응답을 생성하는 함수

    Args:
        request_id (str): 요청 ID
        model_id (str): 모델 ID
        filename (str): 파일 이름
        file_size (int): 파일 크기 (바이트 단위)
        metadata_obj (ModelMetadata): 모델 메타데이터 객체
        current_time (str): 현재 시간
        framework (str): 추정된 머신 러닝 프레임워크

    Returns:
        UploadResponse: 업로드 응답 객체
    """
    return UploadResponse(
        status="success",
        request_id=request_id,
        model_id=model_id,
        upload_status="processing",
        result=UploadResult(
            name=metadata_obj.name if metadata_obj else os.path.splitext(filename)[0],
            version=metadata_obj.version if metadata_obj else "",
            framework=metadata_obj.framework if metadata_obj else framework,
            storage_url=f"models/{model_id}/"
        ),
        metadata=UploadMetadata(
            upload_time=current_time,
            file_size_bytes=file_size,
            estimated_processing_time_sec=120
        )
    )

def build_detection_response(request_id: str, data_id: str, data: DetectionInput, data_path: Path) -> Dict[str, Any]:
    """감지 응답을 생성하는 함수

    Args:
        request_id (str): 요청 ID
        data_id (str): 데이터 ID
        data (DetectionInput): 감지 입력 데이터
        data_path (Path): 데이터 저장 경로

    Returns:
        Dict[str, Any]: 구성된 감지 응답 딕셔너리
    """
    response = {
        "status": "success",
        "request_id": request_id,
        "data_id": data_id,
        "upload_status": "completed",
        "result": {"storage_url": f"data/{data_id}/"},
        "metadata": {
            "upload_time": get_current_time().isoformat(),
            "device_id": data.metadata.device_id if data.metadata else None,
            "timestamp": data.metadata.timestamp if data.metadata else None
        },
        "files": {"config": str(data_path / "config.json")}
    }

    if data.input_data.image:
        response["result"]["image_info"] = {
            "shape": data.input_data.image.shape,
            "dtype": data.input_data.image.dtype,
            "type": data.input_data.image.type
        }
        response["files"]["image"] = str(data_path / "image.npy")

    if data.input_data.annotation_bbox:
        response["result"]["annotation_info"] = {
            "shape": data.input_data.annotation_bbox.shape,
            "dtype": data.input_data.annotation_bbox.dtype,
            "type": data.input_data.annotation_bbox.type
        }
        response["files"]["annotation_bbox"] = str(data_path / "annotation_bbox.npy")

    if data.input_data.classes:
        response["result"]["num_classes"] = len(data.input_data.classes)
        response["files"]["classes"] = str(data_path / "classes.json")

    return response

def update_inference_args(inference_args: dict, config_dict: dict) -> None:
    """추론 인자를 업데이트하는 함수

    Args:
        inference_args (dict): 기존 추론 인자 딕셔너리
        config_dict (dict): 업데이트 할 추론 인자 딕셔너리
    """
    for key, value in config_dict.items():
        if key in inference_args:
            inference_args[key] = value

def get_current_time() -> datetime:
    """현재 시간을 반환하는 함수

    Returns:
        datetime: 현재 시간 (UTC)
    """
    return datetime.now(pytz.UTC)

def calculate_processing_time(start_time: datetime, end_time: datetime) -> float:
    """처리 시간을 계산하는 함수

    Args:
        start_time (datetime): 처리 시작 시간
        end_time (datetime): 처리 종료 시간

    Returns:
        float: 처리 시간 (초 단위)
    """
    return (end_time - start_time).total_seconds()

def generate_request_id() -> str:
    """요청 ID를 생성하는 함수

    Returns:
        str: 생성된 요청 ID
    """
    return f"req-{uuid.uuid4().hex[:8]}"

def generate_model_id() -> str:
    """모델 ID를 생성하는 함수

    Returns:
        str: 생성된 모델 ID
    """
    return f"model-{uuid.uuid4().hex[:8]}"

def generate_data_id() -> str:
    """데이터 ID를 생성하는 함수

    Returns:
        str: 생성된 데이터 ID
    """
    return f"data-{uuid.uuid4().hex[:8]}"

def run_server(host: str = "0.0.0.0", port: int = 3000, run_function=None):
    """서버를 실행하는 함수

    Args:
        host (str): 서버 호스트 주소
        port (int): 서버 포트 번호
        run_function (Optional[function]): 서버에서 실행할 함수
    """
    import uvicorn
    logger.info(f"Preparing to start Uvicorn server on {host}:{port}")
    app_instance = create_app(run_function)
    uvicorn.run(app_instance, host=host, port=port)