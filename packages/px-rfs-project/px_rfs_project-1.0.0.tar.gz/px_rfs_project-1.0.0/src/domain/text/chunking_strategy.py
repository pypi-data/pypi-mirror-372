"""
텍스트 청킹 전략 인터페이스
전략 패턴으로 다양한 청킹 방식 지원
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import asyncio

from src.shared.kernel import Result, Success, Failure, Mono


class ChunkingMethod(str, Enum):
    """청킹 방식 열거형"""

    SEMANTIC = "semantic"  # 의미 단위 (문장 경계)
    FIXED_SIZE = "fixed_size"  # 고정 크기
    PARAGRAPH = "paragraph"  # 단락 단위
    SLIDING_WINDOW = "sliding_window"  # 슬라이딩 윈도우


@dataclass
class ChunkingConfig:
    """청킹 설정"""

    max_chunk_size: int = 2000
    overlap_size: int = 100
    min_chunk_size: int = 50
    preserve_sentences: bool = True
    preserve_paragraphs: bool = False

    def validate(self) -> Result[None, str]:
        """설정 검증"""
        errors = []

        if self.max_chunk_size <= 0:
            errors.append("max_chunk_size must be positive")

        if self.overlap_size < 0:
            errors.append("overlap_size must be non-negative")

        if self.min_chunk_size <= 0:
            errors.append("min_chunk_size must be positive")

        if self.overlap_size >= self.max_chunk_size:
            errors.append("overlap_size must be less than max_chunk_size")

        if self.min_chunk_size > self.max_chunk_size:
            errors.append("min_chunk_size must be less than or equal to max_chunk_size")

        if errors:
            return Failure(f"Configuration errors: {'; '.join(errors)}")

        return Success(None)


@dataclass
class TextChunk:
    """텍스트 청크"""

    content: str
    start_index: int
    end_index: int
    chunk_id: int
    metadata: Optional[Dict[Any, Any]] = None
    source_file: Optional[str] = None
    source_metadata: Optional[Dict[Any, Any]] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}
        if self.source_metadata is None:
            self.source_metadata = {}

    @property
    def size(self) -> int:
        """청크 크기"""
        return len(self.content)

    @property
    def word_count(self) -> int:
        """단어 수"""
        return len(self.content.split())

    @property
    def text(self) -> str:
        """텍스트 내용 (content의 별칭)"""
        return self.content

    def to_dict(self) -> dict:
        """딕셔너리로 직렬화"""
        return {
            "content": self.content,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "chunk_id": self.chunk_id,
            "metadata": self.metadata,
            "source_file": self.source_file,
            "source_metadata": self.source_metadata,
            "size": self.size,
            "word_count": self.word_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TextChunk":
        """딕셔너리에서 역직렬화"""
        return cls(
            content=data["content"],
            start_index=data["start_index"],
            end_index=data["end_index"],
            chunk_id=data["chunk_id"],
            metadata=data.get("metadata", {}),
            source_file=data.get("source_file"),
            source_metadata=data.get("source_metadata", {}),
        )


class ChunkingStrategy(ABC):
    """청킹 전략 기본 클래스"""

    def __init__(self, config: ChunkingConfig):
        self.config = config

    @abstractmethod
    def chunk_text(self, text: str) -> Mono[Result[List[TextChunk], str]]:
        """텍스트를 청크로 분할 (Mono 반환)"""
        pass

    def _create_chunk(
        self,
        content: str,
        start_index: int,
        end_index: int,
        chunk_id: int,
        metadata: Optional[Dict[Any, Any]] = None,
    ) -> TextChunk:
        """청크 생성 헬퍼"""
        return TextChunk(
            content=content.strip(),
            start_index=start_index,
            end_index=end_index,
            chunk_id=chunk_id,
            metadata=metadata or {},
        )

    def _is_valid_chunk(self, content: str) -> bool:
        """유효한 청크인지 확인"""
        clean_content = content.strip()
        return (
            len(clean_content) >= self.config.min_chunk_size
            and len(clean_content) <= self.config.max_chunk_size
        )


class FixedSizeChunkingStrategy(ChunkingStrategy):
    """고정 크기 청킹 전략"""

    def chunk_text(self, text: str) -> Mono[Result[List[TextChunk], str]]:
        """고정 크기로 텍스트 분할"""

        async def chunk() -> Result[List[TextChunk], str]:
            if not text or not text.strip():
                return Success([])

            # 설정 검증
            config_result = self.config.validate()
            if config_result.is_failure():
                return Failure(config_result.get_error() or "Config validation failed")

            # HOF 패턴: 제너레이터 + compact_map 사용
            from src.shared.hof import compact_map
            
            def generate_chunk_positions(text_length: int):
                """처크 위치들을 생성하는 제너레이터"""
                start = 0
                while start < text_length:
                    end = min(start + self.config.max_chunk_size, text_length)
                    yield (start, end)
                    start = max(start + self.config.max_chunk_size - self.config.overlap_size, end)
            
            def create_chunk_from_position(pos_and_id: tuple[tuple[int, int], int]) -> TextChunk | None:
                """위치 정보로부터 처크 생성"""
                (start, end), chunk_id = pos_and_id
                chunk_content = text[start:end]
                
                if self._is_valid_chunk(chunk_content):
                    return self._create_chunk(
                        content=chunk_content,
                        start_index=start,
                        end_index=end,
                        chunk_id=chunk_id,
                        metadata={"method": ChunkingMethod.FIXED_SIZE},
                    )
                return None
            
            # 파이프라인 기반 처크 생성 - RFS Framework pipe 패턴 사용
            from src.shared.hof import pipe
            
            chunk_generation_pipeline = pipe(
                len,  # text → text_length
                generate_chunk_positions,  # text_length → positions generator
                list,  # generator → positions list
                enumerate,  # positions → (index, position) pairs
                list,  # enumerate object → list
                lambda positions_with_id: compact_map(create_chunk_from_position, positions_with_id)  # → chunks
            )
            
            chunks = chunk_generation_pipeline(text)

            return Success(chunks)

        return Mono(lambda: asyncio.run(chunk()))


class SemanticChunkingStrategy(ChunkingStrategy):
    """의미 단위 청킹 전략 (SpaCy 활용)"""

    def __init__(self, config: ChunkingConfig, spacy_processor: Any) -> None:
        super().__init__(config)
        self.spacy_processor = spacy_processor

    def chunk_text(self, text: str) -> Mono[Result[List[TextChunk], str]]:
        """의미 단위로 텍스트 분할"""

        async def semantic_chunk() -> Result[List[TextChunk], str]:
            if not text or not text.strip():
                return Success([])

            # 설정 검증
            config_result = self.config.validate()
            if config_result.is_failure():
                return Failure(config_result.get_error() or "Config validation failed")

            # SpaCy로 문장 분리
            sentences_result = await self.spacy_processor.get_sentences(
                text
            ).to_result()
            if sentences_result.is_failure():
                # SpaCy 실패 시 간단한 문장 분리로 fallback
                sentences = self._simple_sentence_split(text)
            else:
                sentences = sentences_result.value

            if not sentences:
                return Success([])

            chunks = []
            chunk_id = 0
            current_chunk = ""
            current_start = 0

            for sentence in sentences:
                sentence_size = len(sentence)

                # 단일 문장이 최대 크기 초과
                if sentence_size > self.config.max_chunk_size:
                    # 현재 청크 저장
                    if current_chunk.strip() and self._is_valid_chunk(current_chunk):
                        chunk = self._create_chunk(
                            content=current_chunk,
                            start_index=current_start,
                            end_index=current_start + len(current_chunk),
                            chunk_id=chunk_id,
                            metadata={"method": ChunkingMethod.SEMANTIC},
                        )
                        chunks.append(chunk)
                        chunk_id += 1

                    # 긴 문장을 단어 단위로 분할
                    word_chunks = self._split_long_sentence(sentence)
                    for word_chunk in word_chunks:
                        if self._is_valid_chunk(word_chunk):
                            start_idx = text.find(word_chunk, current_start)
                            chunk = self._create_chunk(
                                content=word_chunk,
                                start_index=start_idx,
                                end_index=start_idx + len(word_chunk),
                                chunk_id=chunk_id,
                                metadata={
                                    "method": ChunkingMethod.SEMANTIC,
                                    "split_type": "word",
                                },
                            )
                            chunks.append(chunk)
                            chunk_id += 1

                    current_chunk = ""
                    current_start = text.find(sentence, current_start) + len(sentence)
                    continue

                # 현재 청크에 문장 추가 가능 여부 확인
                if len(current_chunk) + sentence_size + 1 <= self.config.max_chunk_size:
                    if not current_chunk:
                        current_start = text.find(sentence, current_start)
                    current_chunk += sentence + " "
                else:
                    # 현재 청크 저장
                    if current_chunk.strip() and self._is_valid_chunk(current_chunk):
                        chunk = self._create_chunk(
                            content=current_chunk,
                            start_index=current_start,
                            end_index=current_start + len(current_chunk),
                            chunk_id=chunk_id,
                            metadata={"method": ChunkingMethod.SEMANTIC},
                        )
                        chunks.append(chunk)
                        chunk_id += 1

                    # 오버랩 처리
                    if self.config.overlap_size > 0 and chunks:
                        overlap_text = self._get_overlap_text(
                            current_chunk, self.config.overlap_size
                        )
                        current_chunk = overlap_text + sentence + " "
                    else:
                        current_chunk = sentence + " "

                    current_start = text.find(sentence, current_start)

            # 마지막 청크 저장
            if current_chunk.strip() and self._is_valid_chunk(current_chunk):
                chunk = self._create_chunk(
                    content=current_chunk,
                    start_index=current_start,
                    end_index=current_start + len(current_chunk),
                    chunk_id=chunk_id,
                    metadata={"method": ChunkingMethod.SEMANTIC},
                )
                chunks.append(chunk)

            return Success(chunks)

        return Mono(lambda: asyncio.run(semantic_chunk()))

    def _simple_sentence_split(self, text: str) -> List[str]:
        """간단한 문장 분리 (SpaCy fallback)"""
        import re

        sentences = re.split(r"[.!?]+\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _split_long_sentence(self, sentence: str) -> List[str]:
        """긴 문장을 단어 단위로 분할 - HOF 패턴 적용"""
        words = sentence.split()
        
        # HOF 패턴: reduce + 상태 축적
        from functools import reduce
        
        def accumulate_words(acc: tuple[list[str], str], word: str) -> tuple[list[str], str]:
            chunks, current_chunk = acc
            if len(current_chunk) + len(word) + 1 <= self.config.max_chunk_size:
                return (chunks, current_chunk + word + " ")
            else:
                new_chunks = chunks + [current_chunk.strip()] if current_chunk.strip() else chunks
                return (new_chunks, word + " ")
        
        final_chunks, final_chunk = reduce(accumulate_words, words, ([], ""))  # type: ignore
        
        # 마지막 처크 추가
        if final_chunk.strip():
            final_chunks.append(final_chunk.strip())
            
        return final_chunks

    def _get_overlap_text(self, text: str, overlap_size: int) -> str:
        """오버랩 텍스트 추출"""
        words = text.split()
        if len(words) <= overlap_size:
            return text + " "

        overlap_words = words[-overlap_size:]
        return " ".join(overlap_words) + " "


class ParagraphChunkingStrategy(ChunkingStrategy):
    """단락 단위 청킹 전략"""

    def chunk_text(self, text: str) -> Mono[Result[List[TextChunk], str]]:
        """단락 단위로 텍스트 분할"""

        def paragraph_chunk() -> Result[List[TextChunk], str]:
            if not text or not text.strip():
                return Success([])

            # 설정 검증
            config_result = self.config.validate()
            if config_result.is_failure():
                return Failure(config_result.get_error() or "Config validation failed")

            # 단락 분리 (이중 줄바꿈 기준)
            paragraphs = text.split("\n\n")
            paragraphs = [p.strip() for p in paragraphs if p.strip()]

            if not paragraphs:
                return Success([])

            chunks = []
            chunk_id = 0
            current_chunk = ""
            current_start = 0

            for paragraph in paragraphs:
                paragraph_size = len(paragraph)

                # 단일 단락이 최대 크기 초과
                if paragraph_size > self.config.max_chunk_size:
                    # 현재 청크 저장
                    if current_chunk.strip() and self._is_valid_chunk(current_chunk):
                        chunk = self._create_chunk(
                            content=current_chunk,
                            start_index=current_start,
                            end_index=current_start + len(current_chunk),
                            chunk_id=chunk_id,
                            metadata={"method": ChunkingMethod.PARAGRAPH},
                        )
                        chunks.append(chunk)
                        chunk_id += 1

                    # 큰 단락을 문장 단위로 분할
                    sentences = paragraph.split(". ")
                    for sentence in sentences:
                        if self._is_valid_chunk(sentence):
                            start_idx = text.find(sentence, current_start)
                            chunk = self._create_chunk(
                                content=sentence,
                                start_index=start_idx,
                                end_index=start_idx + len(sentence),
                                chunk_id=chunk_id,
                                metadata={
                                    "method": ChunkingMethod.PARAGRAPH,
                                    "split_type": "sentence",
                                },
                            )
                            chunks.append(chunk)
                            chunk_id += 1

                    current_chunk = ""
                    current_start = text.find(paragraph, current_start) + len(paragraph)
                    continue

                # 현재 청크에 단락 추가 가능 여부 확인
                if (
                    len(current_chunk) + paragraph_size + 2
                    <= self.config.max_chunk_size
                ):
                    if not current_chunk:
                        current_start = text.find(paragraph, current_start)
                    current_chunk += paragraph + "\n\n"
                else:
                    # 현재 청크 저장
                    if current_chunk.strip() and self._is_valid_chunk(current_chunk):
                        chunk = self._create_chunk(
                            content=current_chunk,
                            start_index=current_start,
                            end_index=current_start + len(current_chunk),
                            chunk_id=chunk_id,
                            metadata={"method": ChunkingMethod.PARAGRAPH},
                        )
                        chunks.append(chunk)
                        chunk_id += 1

                    # 새 청크 시작
                    current_chunk = paragraph + "\n\n"
                    current_start = text.find(paragraph, current_start)

            # 마지막 청크 저장
            if current_chunk.strip() and self._is_valid_chunk(current_chunk):
                chunk = self._create_chunk(
                    content=current_chunk,
                    start_index=current_start,
                    end_index=current_start + len(current_chunk),
                    chunk_id=chunk_id,
                    metadata={"method": ChunkingMethod.PARAGRAPH},
                )
                chunks.append(chunk)

            return Success(chunks)

        return Mono.from_callable(paragraph_chunk)
