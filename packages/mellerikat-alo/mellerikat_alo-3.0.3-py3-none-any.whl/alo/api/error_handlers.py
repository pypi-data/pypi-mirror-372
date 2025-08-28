from fastapi import HTTPException
import logging
from typing import Optional, Type, Union
from alo.exceptions import AloApiRequestError, AloApiInferenceError, AloError

logger = logging.getLogger(__name__)

class APIError(Exception):
    """API 관련 기본 예외 클래스"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def handle_exception(status_code: int, exception: Exception, message: Optional[str] = None) -> None:
    """예외를 처리하고 적절한 HTTP 예외를 발생시키는 함수"""
    detail = f"{message}: {str(exception)}" if message else str(exception)
    logger.error(f"{status_code} Error: {detail}")
    raise HTTPException(status_code=status_code, detail=detail)

def handle_api_error(error: Union[AloApiRequestError, AloApiInferenceError, AloError]) -> None:
    """ALO API 관련 예외를 처리하는 함수"""
    if isinstance(error, AloApiRequestError):
        logger.warning(f"API Bad Request (400): {error}")
        raise HTTPException(status_code=400, detail=str(error))
    elif isinstance(error, AloApiInferenceError):
        logger.error(f"API Inference Error (500): {error}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ALO Inference Error: {str(error)}")
    elif isinstance(error, AloError):
        logger.error(f"API ALO Internal Error (500): {error}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ALO Internal Error: {str(error)}")
    else:
        logger.critical(f"API Unexpected Internal Server Error (500): {error}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected internal server error: {str(error)}")

def validate_input_data(data: dict, required_fields: list) -> None:
    """입력 데이터의 필수 필드를 검증하는 함수"""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise APIError(f"Missing required fields: {', '.join(missing_fields)}", 400)