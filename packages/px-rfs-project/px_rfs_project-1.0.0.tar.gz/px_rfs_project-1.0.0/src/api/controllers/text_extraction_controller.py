"""
텍스트 추출 API 컨트롤러
파일 업로드 및 URL 처리를 통한 텍스트 추출
"""

import tempfile
import os
from typing import List, Optional, Dict, Any, Union
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, Field, validator

from src.shared.kernel import Result
from src.shared.hof import pipe, compact_map, safe_map, partition
from src.application.services.text_extraction_service import (
    TextExtractionService,
    TextExtractionRequest,
    TextExtractionResult,
    get_text_extraction_service,
)
from src.infrastructure.extractors.file_extractor import FileInfo, SupportedFileType
from src.domain.text.chunking_strategy import ChunkingMethod


class TextExtractionURLRequest(BaseModel):
    """URL 기반 텍스트 추출 요청"""

    urls: List[HttpUrl] = Field(
        ..., description="처리할 URL 목록", min_length=1, max_length=10
    )
    max_chunk_size: int = Field(
        default=2000, description="최대 청크 크기", ge=100, le=10000
    )
    overlap: int = Field(default=100, description="청크 간 오버랩", ge=0, le=1000)
    chunking_strategy: ChunkingMethod = Field(
        default=ChunkingMethod.SEMANTIC, description="청킹 전략"
    )
    use_cache: bool = Field(default=True, description="캐시 사용 여부")
    cache_ttl: int = Field(
        default=7776000, description="캐시 TTL (초)", ge=3600, le=31536000
    )

    @validator("overlap")
    def validate_overlap(cls, v: int, values: Dict[str, Any]) -> int:
        max_chunk_size = values.get("max_chunk_size", 2000)
        if v >= max_chunk_size:
            raise ValueError("오버랩은 최대 청크 크기보다 작아야 합니다")
        return v


class TextExtractionResponse(BaseModel):
    """텍스트 추출 응답"""

    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="결과 메시지")
    data: Optional[Dict[str, Any]] = Field(default=None, description="추출된 데이터")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "텍스트 추출이 완료되었습니다",
                "data": {
                    "chunks": [
                        {
                            "content": "추출된 텍스트 내용...",
                            "chunk_id": 0,
                            "size": 150,
                            "word_count": 25,
                            "source_file": "example.pdf",
                        }
                    ],
                    "metadata": {
                        "total_chunks": 5,
                        "total_sources": 1,
                        "total_characters": 1250,
                    },
                    "source_info": {
                        "example.pdf": {"type": "pdf", "size": 2048, "chunks": 5}
                    },
                    "cache_used": False,
                },
            }
        }


# FastAPI 라우터 생성
text_extraction_router = APIRouter(
    prefix="/api/v1/text-extraction",
    tags=["텍스트 추출"],
    responses={
        400: {"description": "잘못된 요청"},
        422: {"description": "검증 오류"},
        500: {"description": "서버 내부 오류"},
    },
)


@text_extraction_router.post(
    "/files",
    response_model=TextExtractionResponse,
    summary="파일에서 텍스트 추출",
    description="""
    업로드된 파일들에서 텍스트를 추출하고 청킹하여 반환합니다.
    
    지원 파일 형식:
    - PDF (.pdf)
    - PowerPoint (.pptx)
    - 텍스트 파일 (.txt)
    - 마크다운 (.md, .markdown)
    
    텍스트는 지정된 전략에 따라 청킹되며, Redis에 캐시됩니다.
    """,
    response_description="추출된 텍스트 청크와 메타데이터",
)
async def extract_text_from_files(
    files: List[UploadFile] = File(..., description="추출할 파일들"),
    max_chunk_size: int = Form(
        default=2000, description="최대 청크 크기", ge=100, le=10000
    ),
    overlap: int = Form(default=100, description="청크 간 오버랩", ge=0, le=1000),
    chunking_strategy: ChunkingMethod = Form(
        default=ChunkingMethod.SEMANTIC, description="청킹 전략"
    ),
    use_cache: bool = Form(default=True, description="캐시 사용 여부"),
    cache_ttl: int = Form(
        default=7776000, description="캐시 TTL (초)", ge=3600, le=31536000
    ),
    service: TextExtractionService = Depends(get_text_extraction_service),
) -> TextExtractionResponse:
    """파일에서 텍스트 추출"""

    # 입력 검증
    if not files:
        raise HTTPException(status_code=400, detail="업로드할 파일이 없습니다")

    if len(files) > 10:
        raise HTTPException(
            status_code=400, detail="한 번에 최대 10개 파일까지 처리 가능합니다"
        )

    if overlap >= max_chunk_size:
        raise HTTPException(
            status_code=400, detail="오버랩은 최대 청크 크기보다 작아야 합니다"
        )

    file_infos = []
    temp_files = []

    try:
        # HOF 패턴으로 파일 처리 함수 분리
        async def process_single_file(file: UploadFile) -> tuple[str, FileInfo]:
            """단일 파일 처리 - 검증, 저장, FileInfo 생성"""
            # 파일 형식 검증
            if not file.filename:
                raise HTTPException(status_code=400, detail="파일명이 없습니다")

            file_extension = os.path.splitext(file.filename)[1].lower()
            supported_extensions = {".pdf", ".pptx", ".txt", ".md", ".markdown"}

            if file_extension not in supported_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"지원되지 않는 파일 형식: {file_extension}. 지원 형식: {', '.join(supported_extensions)}",
                )

            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=file_extension
            ) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name

            # FileInfo 객체 생성 (파일 해시 계산)
            import hashlib
            file_hash = hashlib.md5(content).hexdigest()
            
            return temp_file_path, FileInfo(
                filename=file.filename or "unknown",
                file_path=temp_file_path,
                file_size=len(content),
                file_hash=file_hash,
                mime_type=file.content_type or "application/octet-stream",
                extension=file_extension,
            )
        
        # 모든 파일을 비동기 HOF 패턴으로 처리
        import asyncio
        from src.shared.hof import safe_map
        
        # 비동기 매핑 함수
        async def process_files_concurrently():
            # 모든 파일을 동시에 처리 (성능 향상)
            tasks = [process_single_file(file) for file in files]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 예외 처리 및 결과 분리 - HOF 패턴 사용
            # 예외 처리
            for result in results:
                if isinstance(result, Exception):
                    raise result
            
            # 결과 분리
            processed_temp_files = list(map(lambda r: r[0], results))
            processed_file_infos = list(map(lambda r: r[1], results))
                
            return processed_temp_files, processed_file_infos
        
        temp_files, file_infos = await process_files_concurrently()

        # 텍스트 추출 요청 생성
        extraction_request = TextExtractionRequest(
            files=file_infos,
            urls=None,
            max_chunk_size=max_chunk_size,
            overlap=overlap,
            chunking_strategy=chunking_strategy.value,
            use_cache=use_cache,
            cache_ttl=cache_ttl,
        )

        # 텍스트 추출 실행
        result = await service.extract_text(extraction_request).execute()

        if result.is_failure():
            raise HTTPException(
                status_code=500, detail=f"텍스트 추출 실패: {result.error}"
            )

        extraction_result = result.value

        return TextExtractionResponse(
            success=True,
            message=f"총 {len(extraction_result.chunks)}개의 텍스트 청크가 추출되었습니다",
            data=extraction_result.to_dict(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"예상치 못한 오류가 발생했습니다: {str(e)}"
        )

    finally:
        # 임시 파일 정리 - HOF 패턴으로 처리
        def safe_cleanup_file(temp_file_path: str) -> bool:
            """안전한 파일 정리"""
            try:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    return True
                return False
            except Exception:
                return False  # 정리 실패는 무시
        
        # 모든 임시 파일 정리
        [safe_cleanup_file(temp_file_path) for temp_file_path in temp_files]


@text_extraction_router.post(
    "/urls",
    response_model=TextExtractionResponse,
    summary="URL에서 텍스트 추출",
    description="""
    제공된 URL들에서 텍스트를 추출하고 청킹하여 반환합니다.
    
    지원 URL 타입:
    - YouTube 동영상 (자막 추출)
    - LinkedIn 프로필 
    - 일반 웹사이트
    
    RapidAPI를 통해 외부 콘텐츠를 가져오며, Redis에 캐시됩니다.
    """,
    response_description="추출된 텍스트 청크와 메타데이터",
)
async def extract_text_from_urls(
    request: TextExtractionURLRequest,
    service: TextExtractionService = Depends(get_text_extraction_service),
) -> TextExtractionResponse:
    """URL에서 텍스트 추출"""

    try:
        # URL을 문자열로 변환
        url_strings = [str(url) for url in request.urls]

        # 텍스트 추출 요청 생성
        extraction_request = TextExtractionRequest(
            files=None,
            urls=url_strings,
            max_chunk_size=request.max_chunk_size,
            overlap=request.overlap,
            chunking_strategy=request.chunking_strategy.value,
            use_cache=request.use_cache,
            cache_ttl=request.cache_ttl,
        )

        # 텍스트 추출 실행
        result = await service.extract_text(extraction_request).execute()

        if result.is_failure():
            raise HTTPException(
                status_code=500, detail=f"텍스트 추출 실패: {result.error}"
            )

        extraction_result = result.value

        return TextExtractionResponse(
            success=True,
            message=f"총 {len(extraction_result.chunks)}개의 텍스트 청크가 추출되었습니다",
            data=extraction_result.to_dict(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"예상치 못한 오류가 발생했습니다: {str(e)}"
        )


@text_extraction_router.post(
    "/mixed",
    response_model=TextExtractionResponse,
    summary="파일과 URL에서 텍스트 추출",
    description="""
    파일 업로드와 URL을 함께 처리하여 텍스트를 추출합니다.
    
    파일과 URL을 동시에 처리할 수 있으며, 결과는 통합되어 반환됩니다.
    """,
    response_description="통합된 텍스트 청크와 메타데이터",
)
async def extract_text_mixed(
    files: Optional[List[UploadFile]] = File(default=None, description="추출할 파일들"),
    urls: Optional[str] = Form(default=None, description="처리할 URL들 (쉼표로 구분)"),
    max_chunk_size: int = Form(
        default=2000, description="최대 청크 크기", ge=100, le=10000
    ),
    overlap: int = Form(default=100, description="청크 간 오버랩", ge=0, le=1000),
    chunking_strategy: ChunkingMethod = Form(
        default=ChunkingMethod.SEMANTIC, description="청킹 전략"
    ),
    use_cache: bool = Form(default=True, description="캐시 사용 여부"),
    cache_ttl: int = Form(
        default=7776000, description="캐시 TTL (초)", ge=3600, le=31536000
    ),
    service: TextExtractionService = Depends(get_text_extraction_service),
) -> TextExtractionResponse:
    """파일과 URL에서 텍스트 혼합 추출"""

    # 입력 검증
    if not files and not urls:
        raise HTTPException(
            status_code=400, detail="파일 또는 URL 중 하나는 반드시 제공되어야 합니다"
        )

    if overlap >= max_chunk_size:
        raise HTTPException(
            status_code=400, detail="오버랩은 최대 청크 크기보다 작아야 합니다"
        )

    file_infos = []
    temp_files = []
    url_list = []

    try:
        # 파일 처리
        if files:
            if len(files) > 10:
                raise HTTPException(
                    status_code=400, detail="한 번에 최대 10개 파일까지 처리 가능합니다"
                )

            # 각 파일 처리
            for file in files:
                if not file.filename:
                    raise HTTPException(status_code=400, detail="파일명이 없습니다")

                file_extension = os.path.splitext(file.filename)[1].lower()
                supported_extensions = {".pdf", ".pptx", ".txt", ".md", ".markdown"}

                if file_extension not in supported_extensions:
                    raise HTTPException(
                        status_code=400,
                        detail=f"지원되지 않는 파일 형식: {file_extension}",
                    )

                # 임시 파일로 저장
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=file_extension
                ) as temp_file:
                    content = await file.read()
                    temp_file.write(content)
                    temp_file_path = temp_file.name
                    temp_files.append(temp_file_path)

                # FileInfo 객체 생성 (파일 해시 계산)
                import hashlib

                file_hash = hashlib.md5(content).hexdigest()

                file_info = FileInfo(
                    filename=file.filename or "unknown",
                    file_path=temp_file_path,
                    file_size=len(content),
                    file_hash=file_hash,
                    mime_type=file.content_type or "application/octet-stream",
                    extension=file_extension,
                )
                file_infos.append(file_info)

        # URL 처리
        if urls:
            url_list = [url.strip() for url in urls.split(",") if url.strip()]
            if len(url_list) > 10:
                raise HTTPException(
                    status_code=400, detail="한 번에 최대 10개 URL까지 처리 가능합니다"
                )

        # 텍스트 추출 요청 생성
        extraction_request = TextExtractionRequest(
            files=file_infos if file_infos else None,
            urls=url_list if url_list else None,
            max_chunk_size=max_chunk_size,
            overlap=overlap,
            chunking_strategy=chunking_strategy.value,
            use_cache=use_cache,
            cache_ttl=cache_ttl,
        )

        # 텍스트 추출 실행
        result = await service.extract_text(extraction_request).execute()

        if result.is_failure():
            raise HTTPException(
                status_code=500, detail=f"텍스트 추출 실패: {result.error}"
            )

        extraction_result = result.value

        return TextExtractionResponse(
            success=True,
            message=f"총 {len(extraction_result.chunks)}개의 텍스트 청크가 추출되었습니다",
            data=extraction_result.to_dict(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"예상치 못한 오류가 발생했습니다: {str(e)}"
        )

    finally:
        # 임시 파일 정리
        for temp_file_path in temp_files:
            try:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            except Exception:
                pass


@text_extraction_router.get(
    "/health",
    summary="텍스트 추출 서비스 상태 확인",
    description="텍스트 추출 관련 서비스들의 상태를 확인합니다",
    response_description="서비스 상태 정보",
)
async def health_check(
    service: TextExtractionService = Depends(get_text_extraction_service),
) -> Dict[str, Any]:
    """텍스트 추출 서비스 헬스체크"""

    status = {
        "service": "healthy",
        "redis": "unknown",
        "rapidapi": "unknown",
        "spacy": "unknown",
    }

    try:
        # Redis 상태 확인
        redis_result = await service.redis_client.ping()
        status["redis"] = "healthy" if redis_result.is_success() else "unhealthy"
    except Exception:
        status["redis"] = "unhealthy"

    try:
        # RapidAPI 클라이언트 상태
        status["rapidapi"] = (
            "available" if service.rapidapi_client else "not_configured"
        )
    except Exception:
        status["rapidapi"] = "error"

    try:
        # SpaCy 상태 확인
        if hasattr(service.chunking_strategy, 'spacy_processor'):
            spacy_available = service.chunking_strategy.spacy_processor.is_available()
        else:
            spacy_available = False
        status["spacy"] = "healthy" if spacy_available else "unhealthy"
    except Exception:
        status["spacy"] = "unhealthy"

    return {
        "status": status,
        "timestamp": "2024-01-01T00:00:00Z",  # 실제로는 datetime.utcnow().isoformat()
        "message": "텍스트 추출 서비스 상태",
    }


def _get_file_type(file_extension: str) -> str:
    """파일 확장자로부터 파일 타입 결정"""
    extension_map = {
        ".pdf": SupportedFileType.PDF.value,
        ".pptx": SupportedFileType.PPTX.value,
        ".txt": SupportedFileType.TXT.value,
        ".md": SupportedFileType.MD.value,
        ".markdown": SupportedFileType.MARKDOWN.value,
    }
    return extension_map.get(file_extension.lower(), SupportedFileType.TXT.value)
