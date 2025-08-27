"""
텍스트 추출 애플리케이션 서비스
파이프라인 패턴으로 작은 함수들을 조합
RFS Framework 패턴 준수 + 강화된 에러 처리 및 로깅
"""

import asyncio
import hashlib
import time
from typing import List, Union, Optional, Dict, Any
from dataclasses import dataclass
from functools import lru_cache

from src.shared.kernel import Result, Success, Failure, Mono
from src.shared.logging import get_logger, log_performance, log_errors, track_error
from src.shared.hof import pipe, compact_map, safe_map, partition, result_chain, tap
from src.domain.text.chunking_strategy import ChunkingStrategy, TextChunk
from src.infrastructure.extractors.file_extractor import FileInfo, ExtractedContent
from src.infrastructure.extractors.extractor_factory import get_extractor_factory
from src.infrastructure.external.rapidapi_client import (
    RapidAPIClient,
    URLValidator,
    ContentSource,
    ExtractedWebContent,
)
from src.config.dependencies import get_container


@dataclass
class TextExtractionRequest:
    """텍스트 추출 요청"""

    # 파일 정보 (파일 업로드 시)
    files: Optional[List[FileInfo]] = None

    # URL 정보 (URL 처리 시)
    urls: Optional[List[str]] = None

    # 텍스트 청킹 설정
    max_chunk_size: int = 2000
    overlap: int = 100
    chunking_strategy: str = "semantic"  # semantic, fixed, sentence

    # 캐시 설정
    use_cache: bool = True
    cache_ttl: int = 7776000  # 3개월 (90일 * 24시간 * 60분 * 60초)


@dataclass
class TextExtractionResult:
    """텍스트 추출 결과"""

    chunks: List[TextChunk]
    metadata: Dict[str, Any]
    source_info: Dict[str, str]  # 소스별 정보
    cache_used: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "metadata": self.metadata,
            "source_info": self.source_info,
            "cache_used": self.cache_used,
        }


class TextExtractionService:
    """
    텍스트 추출 애플리케이션 서비스

    파이프라인 패턴:
    1. 요청 검증 및 분류
    2. 캐시 확인
    3. 텍스트 추출 (파일 또는 URL)
    4. 텍스트 청킹
    5. 결과 캐시 저장
    6. 응답 구성
    """

    def _initialize_dependencies(self) -> None:
        """의존성 초기화 - 작은 단위 함수 (20줄 이하)"""
        self.url_validator = URLValidator()
        self.extractor_factory = get_extractor_factory()

    def _initialize_logger(self) -> None:
        """로거 초기화 - 작은 단위 함수 (20줄 이하)"""
        self.logger = get_logger(
            __name__, {"service": "text_extraction", "version": "1.0.0"}
        )

    def __init__(
        self,
        redis_client: Any,  # RedisClient 타입 힌트 제거 (import 이슈 때문에)
        rapidapi_client: Optional[RapidAPIClient],
        chunking_strategy: ChunkingStrategy,
    ) -> None:
        """생성자 주입 패턴 - 작은 단위 함수 (20줄 이하)"""
        # 의존성 주입 및 초기화
        self.redis_client = redis_client
        self.rapidapi_client = rapidapi_client  
        self.chunking_strategy = chunking_strategy
        self._initialize_dependencies()
        self._initialize_logger()

    @log_performance("text_extraction_pipeline")
    @log_errors("text_extraction_pipeline")
    def extract_text(
        self, request: TextExtractionRequest
    ) -> Mono[Result[TextExtractionResult, str]]:
        """
        메인 텍스트 추출 파이프라인

        Args:
            request: 텍스트 추출 요청

        Returns:
            Mono[Result[TextExtractionResult, str]]: 추출 결과
        """

        # RFS Framework 함수형 개발 3대 규칙 적용: 작은 단위 함수형 개발
        async def execute_pipeline():
            return await self._execute_extraction_pipeline(request)
        
        return Mono.from_callable(execute_pipeline)

    def _log_pipeline_start(self, request: TextExtractionRequest) -> None:
        """파이프라인 시작 로깅 - 작은 단위 함수 (20줄 이하)"""
        self.logger.info(
            "텍스트 추출 파이프라인 시작",
            files_count=len(request.files or []),
            urls_count=len(request.urls or []),
            max_chunk_size=request.max_chunk_size,
            chunking_strategy=request.chunking_strategy,
            use_cache=request.use_cache,
        )

    async def _check_cache_with_early_return(
        self, request: TextExtractionRequest, start_time: float
    ) -> Result[Optional[TextExtractionResult], str]:
        """캐시 확인 및 조기 반환 처리 - 작은 단위 함수 (20줄 이하)"""
        if not request.use_cache:
            return Success(None)
        
        self.logger.debug("캐시 확인 중...")
        cache_result = await self._check_cache(request)
        cache_value = cache_result.get_or_none() if cache_result.is_success() else None
        
        if cache_value is not None:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.info("캐시 히트", duration_ms=duration_ms)
            return Success(cache_value)
        
        self.logger.debug("캐시 미스")
        return Success(None)

    async def _process_extraction_chain(
        self, request: TextExtractionRequest
    ) -> Result[List[ExtractedContent], str]:
        """추출 체인 처리 - 작은 단위 함수 (20줄 이하)"""
        self.logger.debug("텍스트 추출 시작")
        extraction_result = await self._extract_all_sources(request)
        
        if extraction_result.is_failure():
            error_msg = extraction_result.get_error() or "텍스트 추출 실패"
            self.logger.error("텍스트 추출 실패", error=error_msg)
            return Failure(error_msg)
        
        return extraction_result

    async def _process_chunking_chain(
        self, extracted_contents: List[ExtractedContent], request: TextExtractionRequest
    ) -> Result[List[TextChunk], str]:
        """청킹 체인 처리 - 작은 단위 함수 (20줄 이하)"""
        self.logger.debug("텍스트 청킹 시작")
        chunking_result = await self._chunk_all_texts(extracted_contents, request)
        
        if chunking_result.is_failure():
            error_msg = chunking_result.get_error() or "텍스트 청킹 실패"
            self.logger.error("텍스트 청킹 실패", error=error_msg)
            return Failure(error_msg)
        
        return chunking_result

    def _log_pipeline_success(
        self, result: TextExtractionResult, cache_hit: bool, start_time: float
    ) -> None:
        """파이프라인 성공 로깅 - 작은 단위 함수 (20줄 이하)"""
        duration_ms = (time.time() - start_time) * 1000
        total_text_length = sum(len(chunk.content) for chunk in result.chunks)
        
        self.logger.info(
            "텍스트 추출 파이프라인 완료",
            duration_ms=duration_ms,
            chunks_count=len(result.chunks),
            cache_used=cache_hit,
            total_text_length=total_text_length,
        )

    def _track_pipeline_error(
        self, e: Exception, request: TextExtractionRequest, duration_ms: float
    ) -> None:
        """파이프라인 에러 추적 - 작은 단위 함수 (20줄 이하)"""
        track_error(
            e, "text_extraction_pipeline", __name__, "extract_text",
            {
                "request_files": len(request.files or []),
                "request_urls": len(request.urls or []),
                "duration_ms": duration_ms,
            },
        )

    def _log_pipeline_error(
        self, e: Exception, duration_ms: float
    ) -> None:
        """파이프라인 에러 로깅 - 작은 단위 함수 (20줄 이하)"""
        self.logger.error(
            "텍스트 추출 파이프라인 예외 발생",
            error_type=type(e).__name__,
            error_message=str(e),
            duration_ms=duration_ms,
        )

    def _handle_pipeline_exception(
        self, e: Exception, request: TextExtractionRequest, start_time: float
    ) -> Failure:
        """파이프라인 예외 처리 - 작은 단위 함수 (20줄 이하)"""
        duration_ms = (time.time() - start_time) * 1000
        
        # 에러 추적 및 로깅 위임
        self._track_pipeline_error(e, request, duration_ms)
        self._log_pipeline_error(e, duration_ms)
        
        return Failure(f"파이프라인 실행 중 예외 발생: {str(e)}")

    async def _execute_extraction_pipeline(
        self, request: TextExtractionRequest
    ) -> Result[TextExtractionResult, str]:
        """메인 추출 파이프라인 - 작은 함수들의 조합 (20줄 이하)"""
        start_time = time.time()
        
        try:
            # 1. 파이프라인 시작 로깅
            self._log_pipeline_start(request)
            
            # 2. 요청 검증
            validation_result = self._validate_request(request)
            if validation_result.is_failure():
                error_msg = validation_result.get_error() or "요청 검증 실패"
                self.logger.warning("요청 검증 실패", error=error_msg)
                return Failure(error_msg)
            
            # 3. 캐시 확인 및 조기 반환
            cache_result = await self._check_cache_with_early_return(request, start_time)
            if cache_result.is_failure():
                return Failure(cache_result.get_error() or "캐시 처리 실패")
            
            cache_value = cache_result.get_or_none()
            if cache_value is not None:
                return Success(cache_value)  # 캐시 히트 시 조기 반환
            
            return await self._execute_main_processing(request, start_time, False)
            
        except Exception as e:
            return self._handle_pipeline_exception(e, request, start_time)

    async def _execute_main_processing(
        self, request: TextExtractionRequest, start_time: float, cache_hit: bool
    ) -> Result[TextExtractionResult, str]:
        """메인 처리 로직 - 추출, 청킹, 결과 구성 (20줄 이하)"""
        # 4. 텍스트 추출
        extraction_result = await self._process_extraction_chain(request)
        if extraction_result.is_failure():
            return Failure(extraction_result.get_error() or "텍스트 추출 실패")
        
        extracted_contents = extraction_result.get_or_none()
        if extracted_contents is None:
            return Failure("추출 결과에서 값을 가져올 수 없습니다")
        
        # 5. 텍스트 청킹
        chunking_result = await self._process_chunking_chain(extracted_contents, request)
        if chunking_result.is_failure():
            return Failure(chunking_result.get_error() or "청킹 처리 실패")
        
        chunks = chunking_result.get_or_none()
        if chunks is None:
            return Failure("청킹 결과에서 값을 가져올 수 없습니다")
        
        return await self._finalize_processing(request, chunks, extracted_contents, cache_hit, start_time)

    async def _finalize_processing(
        self, request: TextExtractionRequest, chunks: List[TextChunk], 
        extracted_contents: List[ExtractedContent], cache_hit: bool, start_time: float
    ) -> Result[TextExtractionResult, str]:
        """처리 마무리 - 결과 구성 및 캐시 저장 (20줄 이하)"""
        # 6. 결과 구성
        self.logger.debug("결과 구성 중...")
        result = self._build_result(chunks, extracted_contents)
        
        # 7. 캐시 저장 (실패해도 전체 파이프라인은 성공)
        if request.use_cache:
            self.logger.debug("캐시 저장 중...")
            await self._save_to_cache(request, result, cache_ttl=request.cache_ttl)
        
        # 8. 성공 로깅
        self._log_pipeline_success(result, cache_hit, start_time)
        
        return Success(result)

    def _validate_request(self, request: TextExtractionRequest) -> Result[None, str]:
        """요청 검증"""
        if not request.files and not request.urls:
            return Failure("파일 또는 URL이 제공되지 않았습니다")

        if request.max_chunk_size <= 0:
            return Failure("청크 크기는 0보다 커야 합니다")

        if request.overlap < 0 or request.overlap >= request.max_chunk_size:
            return Failure("오버랩은 0 이상이고 청크 크기보다 작아야 합니다")

        return Success(None)

    async def _check_cache(
        self, request: TextExtractionRequest
    ) -> Result[Optional[TextExtractionResult], str]:
        """캐시 확인 파이프라인 - HOF 패턴 적용"""
        
        # 캐시 키 생성 파이프라인
        cache_keys = pipe(
            # 파일과 URL을 하나의 리스트로 결합
            lambda req: (req.files or [], req.urls or []),
            # 파일 캐시 키 생성
            lambda files_urls: compact_map(
                lambda file_info: self._generate_file_cache_key(file_info),
                files_urls[0]
            ) + compact_map(
                lambda url: self._generate_url_cache_key(url),
                files_urls[1]
            )
        )(request)

        # 캐시 키 확인 - 첫 번째 히트된 결과 반환
        async def check_single_cache_key(cache_key: str) -> Result[Optional[TextExtractionResult], str]:
            """단일 캐시 키 확인 - Result 모나드 패턴"""
            cache_result = await self.redis_client.get(cache_key)
            
            cache_value = cache_result.get_or_none() if cache_result.is_success() else None
            if cache_value is None:
                return Success(None)
            
            # JSON 파싱을 Result 모나드로 처리
            def safe_json_parse(json_str: str) -> Result[dict, str]:
                """안전한 JSON 파싱 - Result 모나드 패턴"""
                try:
                    import json
                    return Success(json.loads(json_str))
                except Exception as e:
                    return Failure(f"JSON 파싱 실패: {str(e)}")
            
            parse_result = safe_json_parse(cache_value)
            if parse_result.is_failure():
                return Success(None)  # 캐시 데이터 오류 시 미스 처리
            
            try:
                parse_value = parse_result.get_or_none()
                if parse_value is None:
                    return Success(None)
                result = self._deserialize_result(parse_value)
                result.cache_used = True
                return Success(result)
            except Exception:
                return Success(None)  # 역직렬화 실패 시 미스 처리

        # 모든 캐시 키를 순차적으로 확인하여 첫 번째 히트 반환
        for cache_key in cache_keys:
            cache_result = await check_single_cache_key(cache_key)
            cache_check_value = cache_result.get_or_none() if cache_result.is_success() else None
            if cache_check_value is not None:
                return Success(cache_check_value)

        return Success(None)  # 캐시 미스

    async def _extract_all_sources(
        self, request: TextExtractionRequest
    ) -> Result[List[ExtractedContent], str]:
        """모든 소스에서 텍스트 추출"""
        all_results: List[ExtractedContent] = []

        # 파일 추출
        if request.files:
            file_results = await self._extract_files(request.files)
            if file_results.is_failure():
                return file_results
            file_data = file_results.get_or_none()
            if file_data:
                all_results.extend(file_data)

        # URL 추출
        if request.urls:
            url_results = await self._extract_urls(request.urls)
            if url_results.is_failure():
                return url_results
            url_data = url_results.get_or_none()
            if url_data:
                all_results.extend(url_data)

        if not all_results:
            return Failure("추출된 텍스트가 없습니다")

        return Success(all_results)

    async def _extract_files(
        self, files: List[FileInfo]
    ) -> Result[List[ExtractedContent], str]:
        """파일들에서 텍스트 추출 - HOF 패턴 적용"""
        
        async def extract_single_file(file_info: FileInfo) -> Result[ExtractedContent, str]:
            """단일 파일 추출 - Result 모나드 패턴"""
            extractor = self.extractor_factory.get_extractor(file_info)
            # extract_text가 이미 Mono[Result[...]]를 반환하므로 await를 통해 Result를 얻음
            mono_result = await extractor.extract_text(file_info).to_result()
            if mono_result.is_failure():
                return Failure(mono_result.get_error() or "Extraction failed")
            inner_result = mono_result.get_or_none()
            if inner_result is None:
                return Failure("Extraction result is None")
            return inner_result
        
        # 모든 파일에 대해 추출 작업을 수행
        extraction_results: List[ExtractedContent] = []
        for file_info in files:
            result = await extract_single_file(file_info)
            if result.is_failure():
                return Failure(result.get_error() or "File extraction failed")  # 타입 맞춤
            extracted_content = result.get_or_none()
            if extracted_content is not None:
                extraction_results.append(extracted_content)
        
        return Success(extraction_results)

    async def _extract_urls(
        self, urls: List[str]
    ) -> Result[List[ExtractedContent], str]:
        """URL들에서 텍스트 추출"""
        if not self.rapidapi_client:
            return Failure(
                "URL 텍스트 추출을 위한 RapidAPI 클라이언트가 설정되지 않았습니다"
            )

        async def extract_single_url(url: str) -> Result[ExtractedContent, str]:
            """단일 URL 추출 - Result 모나드 패턴"""
            # URL 타입 판별 및 추출 파이프라인
            url_type = self._determine_url_type(url)
            
            # 타입별 추출 함수 매핑 - rapidapi_client는 이미 None 체크됨
            client = self.rapidapi_client  # 명시적 할당으로 타입 가드
            if client is None:
                return Failure("RapidAPI client is not available")
            
            extract_functions = {
                ContentSource.YOUTUBE: lambda: client.extract_youtube_subtitles(url).to_result(),
                ContentSource.LINKEDIN: lambda: client.extract_linkedin_profile(url).to_result(),
                ContentSource.WEBSITE: lambda: client.extract_website_content(url).to_result()
            }
            
            if url_type not in extract_functions:
                return Failure(f"지원되지 않는 URL 형식: {url}")
            
            # 추출 실행 - Mono[Result[...]]를 처리
            mono_result = await extract_functions[url_type]()
            if mono_result.is_failure():
                return Failure(mono_result.get_error() or "URL extraction failed")
            
            inner_result = mono_result.get_or_none()
            if inner_result is None:
                return Failure("URL extraction result is None")
            
            if inner_result.is_failure():
                return Failure(inner_result.get_error() or "Web content extraction failed")
            
            # ExtractedWebContent를 ExtractedContent로 변환
            web_content = inner_result.get_or_none()
            if web_content is None:
                return Failure("Web content is None")
                
            return Success(ExtractedContent(
                text=web_content.text,
                metadata={
                    **web_content.metadata,
                    "source_type": url_type.value,  # ContentSource는 enum이므로 .value 사용
                    "source_url": url,
                    "filename": f"{url_type.value}_content",
                    "word_count": web_content.word_count,
                    "char_count": web_content.char_count,
                },
            ))
        
        # 모든 URL에 대해 추출 작업을 순차적으로 수행
        extraction_results: List[ExtractedContent] = []
        for url in urls:
            result = await extract_single_url(url)
            if result.is_failure():
                return Failure(result.get_error() or "URL extraction failed")  # 타입 맞춤
            extracted_content = result.get_or_none()
            if extracted_content is not None:
                extraction_results.append(extracted_content)
        
        return Success(extraction_results)

    async def _chunk_all_texts(
        self, extracted_contents: List[ExtractedContent], request: TextExtractionRequest
    ) -> Result[List[TextChunk], str]:
        """모든 추출된 텍스트를 청킹 - HOF 패턴 적용"""
        # 요청에 따른 청킹 설정 생성
        from src.domain.text.chunking_strategy import (
            ChunkingConfig,
            FixedSizeChunkingStrategy,
        )

        config = ChunkingConfig(
            max_chunk_size=request.max_chunk_size,
            overlap_size=request.overlap,
            min_chunk_size=50,
            preserve_sentences=True,
        )

        chunking_strategy = FixedSizeChunkingStrategy(config)

        async def chunk_single_content(content: ExtractedContent) -> Result[List[TextChunk], str]:
            """단일 콘텐츠 청킹 - Result 모나드 패턴"""
            chunk_mono = chunking_strategy.chunk_text(content.text)
            # chunk_text가 이미 Mono[Result[...]를 반환하므로 중첩 처리 필요
            mono_result = await chunk_mono.to_result()
            if mono_result.is_failure():
                return Failure(mono_result.get_error() or "Chunking mono failed")
                
            inner_result = mono_result.get_or_none()
            if inner_result is None:
                return Failure("Chunking mono returned None")
                
            if inner_result.is_failure():
                return Failure(inner_result.get_error() or "Chunking failed")
            
            chunks_data = inner_result.get_or_none()
            if chunks_data is None:
                return Failure("Chunks data is None")
            
            # 소스 정보 추가를 HOF 패턴으로 처리
            def add_source_info(chunk: TextChunk) -> TextChunk:
                chunk.source_file = content.metadata.get("filename", "unknown")
                chunk.source_metadata = content.metadata
                return chunk
            
            enhanced_chunks = [add_source_info(chunk) for chunk in chunks_data]
            return Success(enhanced_chunks)
        
        # 모든 콘텐츠에 대해 청킹 작업을 순차적으로 수행
        all_chunks: List[TextChunk] = []
        for content in extracted_contents:
            chunk_result = await chunk_single_content(content)
            if chunk_result.is_failure():
                return Failure(chunk_result.get_error() or "Content chunking failed")  # 타입 맞춤
            chunks_data = chunk_result.get_or_none()
            if chunks_data is not None:
                all_chunks.extend(chunks_data)

        return Success(all_chunks)

    def _create_result_metadata(
        self, chunks: List[TextChunk], extracted_contents: List[ExtractedContent]
    ) -> Dict[str, Any]:
        """결과 메타데이터 생성 - 파이프라인 패턴 사용 (20줄 이하)"""
        from src.shared.hof import pipe
        
        # 캐릭터 수 계산 파이프라인
        calculate_total_chars = pipe(
            lambda chunks: map(lambda chunk: len(chunk.text), chunks),
            sum
        )
        
        total_characters = calculate_total_chars(chunks)
        
        return {
            "total_chunks": len(chunks),
            "total_sources": len(extracted_contents),
            "total_characters": total_characters,
            "avg_chunk_size": total_characters / len(chunks) if chunks else 0,
        }

    def _create_single_source_info(
        self, content: ExtractedContent, chunks: List[TextChunk]
    ) -> tuple[str, str]:
        """단일 콘텐츠 소스 정보 생성 - 작은 단위 함수 (20줄 이하)"""
        filename = content.metadata.get("filename", "unknown")
        source_type = content.metadata.get("source_type", "unknown")
        file_size = content.metadata.get("file_size", 0)
        chunk_count = len([c for c in chunks if c.source_file == filename])
        return filename, f"{source_type} (size: {file_size}, chunks: {chunk_count})"

    def _create_source_info_dict(
        self, extracted_contents: List[ExtractedContent], chunks: List[TextChunk]
    ) -> Dict[str, str]:
        """소스 정보 딕셔너리 생성 - 작은 단위 함수 (20줄 이하)"""
        return dict(
            self._create_single_source_info(content, chunks) 
            for content in extracted_contents
        )

    def _build_result(
        self, chunks: List[TextChunk], extracted_contents: List[ExtractedContent]
    ) -> TextExtractionResult:
        """최종 결과 구성 - 작은 단위 함수 (20줄 이하)"""
        metadata = self._create_result_metadata(chunks, extracted_contents)
        source_info = self._create_source_info_dict(extracted_contents, chunks)
        
        return TextExtractionResult(
            chunks=chunks, metadata=metadata, source_info=source_info, cache_used=False
        )

    async def _save_to_cache(
        self,
        request: TextExtractionRequest,
        result: TextExtractionResult,
        cache_ttl: int,
    ):
        """결과를 캐시에 저장"""
        import json

        # 캐시 키들 생성을 HOF 패턴으로 처리
        cache_keys = pipe(
            # 파일과 URL을 하나의 리스트로 결합
            lambda req: (req.files or [], req.urls or []),
            # 캐시 키 생성
            lambda files_urls: compact_map(
                lambda file_info: self._generate_file_cache_key(file_info),
                files_urls[0]
            ) + compact_map(
                lambda url: self._generate_url_cache_key(url),
                files_urls[1]
            )
        )(request)

        # 결과 직렬화
        serialized_result = json.dumps(result.to_dict(), ensure_ascii=False)

        # 각 캐시 키에 저장을 안전한 방식으로 수행
        async def save_to_single_key(cache_key: str) -> Result[None, str]:
            """단일 캐시 키에 저장 - Result 모나드 패턴"""
            try:
                await self.redis_client.set(cache_key, serialized_result, cache_ttl)
                return Success(None)
            except Exception as e:
                return Failure(f"캐시 저장 실패: {str(e)}")
        
        # 모든 캐시 키에 저장 (실패해도 계속 진행)
        for cache_key in cache_keys:
            await save_to_single_key(cache_key)

    def _generate_file_cache_key(self, file_info: FileInfo) -> str:
        """파일용 캐시 키 생성"""
        # 파일 해시를 직접 사용 (이미 계산되어 있음)
        content_hash = file_info.file_hash[:16]
        return f"file:text:{content_hash}"

    def _generate_url_cache_key(self, url: str) -> Optional[str]:
        """URL용 캐시 키 생성 (URL 타입별로 다른 키 형식)"""
        url_type = self._determine_url_type(url)

        if url_type == ContentSource.YOUTUBE:
            video_id_result = self.url_validator.validate_youtube_url(url)
            if video_id_result.is_success():
                return f"youtube_subtitle:{video_id_result.get_or_none()}"

        elif url_type == ContentSource.LINKEDIN:
            username_result = self.url_validator.validate_linkedin_url(url)
            if username_result.is_success():
                return f"linkedin_profile:{username_result.get_or_none()}"

        elif url_type == ContentSource.WEBSITE:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:16]
            return f"website:text:{url_hash}"

        return None

    def _determine_url_type(self, url: str) -> Optional[ContentSource]:
        """URL 타입 판별"""
        if "youtube.com" in url or "youtu.be" in url:
            return ContentSource.YOUTUBE
        elif "linkedin.com/in/" in url:
            return ContentSource.LINKEDIN
        else:
            return ContentSource.WEBSITE

    def _deserialize_result(self, cached_data: Dict[str, Any]) -> TextExtractionResult:
        """캐시된 데이터를 결과 객체로 변환"""
        chunks = [
            TextChunk.from_dict(chunk_data) for chunk_data in cached_data["chunks"]
        ]
        return TextExtractionResult(
            chunks=chunks,
            metadata=cached_data["metadata"],
            source_info=cached_data["source_info"],
            cache_used=True,
        )


def _create_default_chunking_config():
    """기본 청킹 설정 생성 - 작은 단위 함수 (20줄 이하)"""
    from src.domain.text.chunking_strategy import ChunkingConfig
    
    return ChunkingConfig(
        max_chunk_size=2000,
        overlap_size=100,
        min_chunk_size=50,
        preserve_sentences=True,
    )

def _create_chunking_strategy():
    """청킹 전략 생성 - 작은 단위 함수 (20줄 이하)"""
    from src.domain.text.chunking_strategy import FixedSizeChunkingStrategy
    
    config = _create_default_chunking_config()
    return FixedSizeChunkingStrategy(config)

@lru_cache()
def get_text_extraction_service() -> TextExtractionService:
    """텍스트 추출 서비스 싱글톤 반환"""
    container = get_container()

    # 청킹 전략 생성 (작은 단위 함수 위임)
    chunking_strategy = _create_chunking_strategy()

    return TextExtractionService(
        redis_client=container.redis,
        rapidapi_client=container.rapidapi,
        chunking_strategy=chunking_strategy,
    )
