"""
텍스트 처리 도메인 서비스
청킹 전략을 활용한 텍스트 처리
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
import asyncio

from src.shared.kernel import Result, Success, Failure, Mono
from .chunking_strategy import ChunkingMethod, ChunkingConfig, TextChunk
from .chunking_factory import ChunkingStrategyFactory


@dataclass
class TextProcessingRequest:
    """텍스트 처리 요청"""

    content: str
    source_type: str = "general"  # general, academic, web, code, etc.
    chunking_method: Optional[ChunkingMethod] = None
    chunking_config: Optional[ChunkingConfig] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TextProcessingResult:
    """텍스트 처리 결과"""

    chunks: list[TextChunk]
    original_length: int
    chunk_count: int
    processing_method: ChunkingMethod
    processing_config: ChunkingConfig
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}

    @property
    def total_chunk_size(self) -> int:
        """전체 청크 크기"""
        return sum(chunk.size for chunk in self.chunks)

    @property
    def average_chunk_size(self) -> float:
        """평균 청크 크기"""
        if not self.chunks:
            return 0.0
        return self.total_chunk_size / len(self.chunks)

    @property
    def compression_ratio(self) -> float:
        """압축율 (원본 대비 청크 크기 비율)"""
        if self.original_length == 0:
            return 0.0
        return self.total_chunk_size / self.original_length


class TextProcessor:
    """텍스트 처리 도메인 서비스"""

    def __init__(self, spacy_processor: Any) -> None:
        self.spacy_processor = spacy_processor
        self.strategy_factory = ChunkingStrategyFactory()

    def process_text(
        self, request: TextProcessingRequest
    ) -> Mono[Result[TextProcessingResult, str]]:
        """텍스트 처리 메인 메소드"""

        async def process() -> Result[TextProcessingResult, str]:
            # 입력 검증
            if not request.content or not request.content.strip():
                return Failure("Empty content provided")

            try:
                # 청킹 방식 결정
                chunking_method = self._determine_chunking_method(request)

                # 청킹 설정 결정
                chunking_config = self._determine_chunking_config(
                    request, chunking_method
                )

                # 청킹 전략 생성
                strategy_result = self.strategy_factory.create_strategy(
                    method=chunking_method,
                    config=chunking_config,
                )

                if strategy_result.is_failure():
                    return Failure(strategy_result.get_error() or "Strategy creation failed")

                strategy = strategy_result.get_or_none()
                if strategy is None:
                    return Failure("Strategy creation returned None")

                # 텍스트 청킹 실행
                chunks_result = await strategy.chunk_text(request.content).to_result()

                if chunks_result.is_failure():
                    return Failure(chunks_result.get_error() or "Chunking failed")

                from typing import cast
                raw_chunks = chunks_result.get_or_none()
                chunks: list[TextChunk] = cast(list[TextChunk], raw_chunks) if raw_chunks is not None else []
                if not chunks:
                    return Failure("Chunking returned no results")

                # 결과 생성
                result = TextProcessingResult(
                    chunks=chunks,
                    original_length=len(request.content),
                    chunk_count=len(chunks),
                    processing_method=chunking_method,
                    processing_config=chunking_config,
                    metadata={
                        "source_type": request.source_type,
                        "original_metadata": request.metadata,
                        "processing_stats": {
                            "total_chunk_size": sum(chunk.size for chunk in chunks),
                            "average_chunk_size": (
                                sum(chunk.size for chunk in chunks) / len(chunks)
                                if chunks
                                else 0
                            ),
                            "largest_chunk": (
                                max(chunk.size for chunk in chunks) if chunks else 0
                            ),
                            "smallest_chunk": (
                                min(chunk.size for chunk in chunks) if chunks else 0
                            ),
                        },
                    },
                )

                return Success(result)

            except Exception as e:
                return Failure(f"Text processing failed: {str(e)}")

        return Mono(lambda: asyncio.run(process()))

    def validate_request(self, request: TextProcessingRequest) -> Result[None, str]:
        """요청 검증"""
        errors = []

        if not request.content:
            errors.append("Content is required")

        if request.chunking_config:
            config_result = request.chunking_config.validate()
            if config_result.is_failure():
                errors.append(f"Invalid chunking config: {config_result.get_error()}")

        # 텍스트 길이 검증
        if len(request.content) > 1000000:  # 1MB 제한
            errors.append("Content too large (max 1MB)")

        if errors:
            return Failure(f"Validation errors: {'; '.join(errors)}")

        return Success(None)

    def _determine_chunking_method(
        self, request: TextProcessingRequest
    ) -> ChunkingMethod:
        """청킹 방식 결정"""
        # 명시적 방식이 지정된 경우
        if request.chunking_method:
            return request.chunking_method

        # 텍스트 특성에 따른 추천
        text_length = len(request.content)
        content_type = request.source_type

        # 임시로 기본값 반환 (recommend_method가 구현되지 않음)
        if text_length > 10000:
            return ChunkingMethod.SEMANTIC
        elif content_type == "academic":
            return ChunkingMethod.PARAGRAPH
        else:
            return ChunkingMethod.FIXED_SIZE

    def _determine_chunking_config(
        self, request: TextProcessingRequest, method: ChunkingMethod
    ) -> ChunkingConfig:
        """청킹 설정 결정"""
        # 명시적 설정이 있는 경우
        if request.chunking_config:
            return request.chunking_config

        # 기본 설정 사용
        # 임시로 기본 설정 반환 (get_default_config가 구현되지 않음)
        return ChunkingConfig(max_chunk_size=1000, overlap_size=100)

    def get_processing_stats(self, result: TextProcessingResult) -> Dict[str, Any]:
        """처리 통계 조회"""
        if not result.chunks:
            return {
                "chunk_count": 0,
                "total_size": 0,
                "average_size": 0,
                "compression_ratio": 0.0,
            }

        chunk_sizes = [chunk.size for chunk in result.chunks]

        return {
            "chunk_count": result.chunk_count,
            "total_size": result.total_chunk_size,
            "average_size": result.average_chunk_size,
            "largest_chunk": max(chunk_sizes),
            "smallest_chunk": min(chunk_sizes),
            "compression_ratio": result.compression_ratio,
            "method_used": result.processing_method.value,
            "config_used": {
                "max_chunk_size": result.processing_config.max_chunk_size,
                "overlap_size": result.processing_config.overlap_size,
                "preserve_sentences": result.processing_config.preserve_sentences,
            },
        }

    def extract_keywords(
        self, content: str, limit: int = 10
    ) -> Mono[Result[list[str], str]]:
        """키워드 추출 (SpaCy 활용)"""
        # SpaCy processor의 get_keywords 메서드 호출 대신 기본 구현
        def simple_keywords() -> Result[list[str], str]:
            # 파이프라인 패턴: 키워드 추출
            from src.shared.hof import pipe
            
            keyword_pipeline = pipe(
                lambda text: text.lower(),  # text → lowercase
                lambda text: text.split(),  # lowercase → words list
                set,  # words → unique words set
                list,  # set → unique words list
                lambda words: words[:limit]  # limit → limited keywords
            )
            
            unique_keywords = keyword_pipeline(content)
            return Success(unique_keywords)
        
        return Mono(simple_keywords)

    def analyze_text_structure(self, content: str) -> Mono[Result[Dict[str, Any], str]]:
        """텍스트 구조 분석"""

        async def analyze() -> Result[Dict[str, Any], str]:
            try:
                # 기본 통계
                word_count = len(content.split())
                char_count = len(content)

                # SpaCy 분석
                sentences_result = await self.spacy_processor.get_sentences(
                    content
                ).to_result()
                entities_result = await self.spacy_processor.extract_entities(
                    content
                ).to_result()
                keywords_result = await self.spacy_processor.get_keywords(
                    content, 10
                ).to_result()

                analysis = {
                    "basic_stats": {
                        "character_count": char_count,
                        "word_count": word_count,
                        "estimated_reading_time_minutes": word_count
                        / 200,  # 평균 200 단어/분
                    },
                    "structure": {
                        "sentence_count": (
                            len(sentences_result.value)
                            if sentences_result.is_success()
                            else 0
                        ),
                        "paragraph_count": len(content.split("\n\n")),
                        "average_sentence_length": (
                            word_count / len(sentences_result.value)
                            if sentences_result.is_success() and sentences_result.value
                            else 0
                        ),
                    },
                    "entities": (
                        entities_result.value if entities_result.is_success() else []
                    ),
                    "keywords": (
                        keywords_result.value if keywords_result.is_success() else []
                    ),
                    "content_indicators": {
                        "has_code_blocks": "```" in content or "    " in content,
                        "has_urls": "http" in content.lower(),
                        "has_emails": "@" in content and "." in content,
                        "language_hints": {
                            "has_korean": any(
                                "\uac00" <= char <= "\ud7a3" for char in content
                            ),
                            "has_english": any(
                                "a" <= char.lower() <= "z" for char in content
                            ),
                            "has_numbers": any(char.isdigit() for char in content),
                        },
                    },
                }

                return Success(analysis)

            except Exception as e:
                return Failure(f"Text analysis failed: {str(e)}")

        return Mono(lambda: asyncio.run(analyze()))
