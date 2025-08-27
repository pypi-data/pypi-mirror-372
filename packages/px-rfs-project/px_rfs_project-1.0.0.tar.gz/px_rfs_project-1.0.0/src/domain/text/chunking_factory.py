"""
텍스트 청킹 전략 팩토리
전략 선택 및 SpaCy 폴백 로직 구현
"""

from typing import Optional, Any
from enum import Enum

from src.shared.kernel import Result, Success, Failure
from .chunking_strategy import (
    ChunkingStrategy,
    ChunkingMethod,
    ChunkingConfig,
    FixedSizeChunkingStrategy,
    SemanticChunkingStrategy,
    ParagraphChunkingStrategy,
)


class ChunkingStrategyFactory:
    """청킹 전략 팩토리"""

    def __init__(self, spacy_processor: Any = None) -> None:
        """
        팩토리 초기화

        Args:
            spacy_processor: SpaCy 프로세서 (None이면 SpaCy 전략 비활성화)
        """
        self.spacy_processor = spacy_processor
        self.spacy_available = spacy_processor is not None

    def create_strategy(
        self, method: ChunkingMethod, config: ChunkingConfig
    ) -> Result[ChunkingStrategy, str]:
        """
        청킹 전략 생성

        Args:
            method: 청킹 방식
            config: 청킹 설정

        Returns:
            청킹 전략 객체 또는 에러
        """
        try:
            # 설정 검증
            config_result = config.validate()
            if config_result.is_failure():
                return Failure(config_result.get_error() or "Config validation failed")

            if method == ChunkingMethod.SEMANTIC:
                return self._create_semantic_strategy(config)
            elif method == ChunkingMethod.FIXED_SIZE:
                return self._create_fixed_size_strategy(config)
            elif method == ChunkingMethod.PARAGRAPH:
                return self._create_paragraph_strategy(config)
            elif method == ChunkingMethod.SLIDING_WINDOW:
                # 슬라이딩 윈도우는 고정 크기 전략으로 대체
                return self._create_fixed_size_strategy(config)
            # 모든 ChunkingMethod case가 처리됨
            # else:
            #     return Failure(f"Unknown chunking method: {method}")

        except Exception as e:
            return Failure(f"Failed to create chunking strategy: {str(e)}")

    def create_best_available_strategy(
        self, config: ChunkingConfig, preferred_method: Optional[ChunkingMethod] = None
    ) -> Result[ChunkingStrategy, str]:
        """
        최적 사용 가능한 전략 생성 (폴백 로직 적용)

        Args:
            config: 청킹 설정
            preferred_method: 선호하는 방식 (None이면 자동 선택)

        Returns:
            최적 전략 또는 에러
        """
        # 선호 방식이 지정되면 먼저 시도
        if preferred_method:
            strategy_result = self.create_strategy(preferred_method, config)
            if strategy_result.is_success():
                return strategy_result

        # 폴백 우선순위: Semantic → Paragraph → Fixed Size
        fallback_methods = [
            ChunkingMethod.SEMANTIC,
            ChunkingMethod.PARAGRAPH,
            ChunkingMethod.FIXED_SIZE,
        ]

        last_error = "No strategy available"

        for method in fallback_methods:
            strategy_result = self.create_strategy(method, config)
            if strategy_result.is_success():
                return strategy_result
            last_error = strategy_result.get_error() or "Unknown error"

        return Failure(f"All fallback strategies failed. Last error: {last_error}")

    def _create_semantic_strategy(
        self, config: ChunkingConfig
    ) -> Result[ChunkingStrategy, str]:
        """의미 단위 전략 생성"""
        if not self.spacy_available:
            # SpaCy 없으면 단락 전략으로 폴백
            return self._create_paragraph_strategy(config)

        try:
            strategy = SemanticChunkingStrategy(config, self.spacy_processor)
            return Success(strategy)
        except Exception as e:
            # 에러 발생 시 단락 전략으로 폴백
            return self._create_paragraph_strategy(config)

    def _create_fixed_size_strategy(
        self, config: ChunkingConfig
    ) -> Result[ChunkingStrategy, str]:
        """고정 크기 전략 생성"""
        try:
            strategy = FixedSizeChunkingStrategy(config)
            return Success(strategy)
        except Exception as e:
            return Failure(f"Failed to create fixed size strategy: {str(e)}")

    def _create_paragraph_strategy(
        self, config: ChunkingConfig
    ) -> Result[ChunkingStrategy, str]:
        """단락 단위 전략 생성"""
        try:
            strategy = ParagraphChunkingStrategy(config)
            return Success(strategy)
        except Exception as e:
            return Failure(f"Failed to create paragraph strategy: {str(e)}")

    @staticmethod
    def create_strategy_with_spacy(
        method: ChunkingMethod,
        config: ChunkingConfig,
        spacy_processor: Optional[object] = None,
    ) -> Result[ChunkingStrategy, str]:
        """정적 메서드로 전략 생성 (기존 호환성)"""
        factory = ChunkingStrategyFactory(spacy_processor)
        return factory.create_strategy(method, config)

    @staticmethod
    def get_default_config(method: ChunkingMethod) -> ChunkingConfig:
        """청킹 방식별 기본 설정 반환"""

        if method == ChunkingMethod.SEMANTIC:
            return ChunkingConfig(
                max_chunk_size=2000,
                overlap_size=100,
                min_chunk_size=100,
                preserve_sentences=True,
                preserve_paragraphs=False,
            )

        elif method == ChunkingMethod.PARAGRAPH:
            return ChunkingConfig(
                max_chunk_size=3000,
                overlap_size=200,
                min_chunk_size=200,
                preserve_sentences=True,
                preserve_paragraphs=True,
            )

        elif method == ChunkingMethod.SLIDING_WINDOW:
            return ChunkingConfig(
                max_chunk_size=1500,
                overlap_size=300,  # 더 큰 오버랩
                min_chunk_size=50,
                preserve_sentences=False,
                preserve_paragraphs=False,
            )

        else:  # FIXED_SIZE
            return ChunkingConfig(
                max_chunk_size=2000,
                overlap_size=100,
                min_chunk_size=50,
                preserve_sentences=False,
                preserve_paragraphs=False,
            )

    @staticmethod
    def recommend_method(
        text_length: int, content_type: str = "general"
    ) -> ChunkingMethod:
        """텍스트 특성에 따른 청킹 방식 추천"""

        # 짧은 텍스트
        if text_length < 1000:
            return ChunkingMethod.FIXED_SIZE

        # 구조화된 문서 (논문, 보고서 등)
        if content_type in ["academic", "report", "article"]:
            if text_length > 10000:
                return ChunkingMethod.PARAGRAPH
            else:
                return ChunkingMethod.SEMANTIC

        # 대화형 텍스트
        elif content_type in ["chat", "conversation", "interview"]:
            return ChunkingMethod.SEMANTIC

        # 코드나 기술 문서
        elif content_type in ["code", "technical", "documentation"]:
            return ChunkingMethod.PARAGRAPH

        # 웹 콘텐츠
        elif content_type in ["web", "html", "blog"]:
            return ChunkingMethod.SEMANTIC

        # 일반 텍스트 (기본)
        else:
            if text_length > 5000:
                return ChunkingMethod.SEMANTIC
            else:
                return ChunkingMethod.FIXED_SIZE

    def get_strategy_info(self, method: ChunkingMethod) -> dict:
        """전략 정보 조회"""
        info = {
            "method": method,
            "available": True,
            "description": "",
            "requires_spacy": False,
            "fallback_to": None,
        }

        if method == ChunkingMethod.SEMANTIC:
            info.update(
                {
                    "description": "의미 단위 청킹 (문장 경계 기준)",
                    "requires_spacy": True,
                    "available": self.spacy_available,
                    "fallback_to": (
                        ChunkingMethod.PARAGRAPH if not self.spacy_available else None
                    ),
                }
            )
        elif method == ChunkingMethod.FIXED_SIZE:
            info.update(
                {
                    "description": "고정 크기 청킹 (문자 수 기준)",
                    "requires_spacy": False,
                }
            )
        elif method == ChunkingMethod.PARAGRAPH:
            info.update(
                {
                    "description": "단락 단위 청킹 (이중 줄바꿈 기준)",
                    "requires_spacy": False,
                }
            )
        elif method == ChunkingMethod.SLIDING_WINDOW:
            info.update(
                {
                    "description": "슬라이딩 윈도우 청킹",
                    "requires_spacy": False,
                    "fallback_to": ChunkingMethod.FIXED_SIZE,
                }
            )

        return info

    def get_available_methods(self) -> list[ChunkingMethod]:
        """사용 가능한 청킹 방식 목록"""
        available = [
            ChunkingMethod.FIXED_SIZE,
            ChunkingMethod.PARAGRAPH,
            ChunkingMethod.SLIDING_WINDOW,  # 고정 크기로 대체
        ]

        if self.spacy_available:
            available.append(ChunkingMethod.SEMANTIC)

        return available

    def get_recommended_method(
        self, text_length: int, content_type: str = "general"
    ) -> ChunkingMethod:
        """텍스트 특성에 따른 권장 청킹 방식"""
        # 짧은 텍스트
        if text_length < 1000:
            return ChunkingMethod.FIXED_SIZE

        # 긴 텍스트
        if text_length > 50000:
            if content_type in ["document", "article", "book"]:
                return ChunkingMethod.PARAGRAPH
            else:
                return (
                    ChunkingMethod.SEMANTIC
                    if self.spacy_available
                    else ChunkingMethod.PARAGRAPH
                )

        # 중간 길이 텍스트
        if content_type in ["code", "log", "data"]:
            return ChunkingMethod.FIXED_SIZE
        else:
            return (
                ChunkingMethod.SEMANTIC
                if self.spacy_available
                else ChunkingMethod.PARAGRAPH
            )

    def create_adaptive_config(
        self,
        text_length: int,
        target_chunk_count: Optional[int] = None,
        preserve_context: bool = True,
    ) -> ChunkingConfig:
        """텍스트 길이에 따른 적응형 설정 생성"""
        # 기본값
        max_chunk_size = 2000
        overlap_size = 100
        min_chunk_size = 50

        # 텍스트 길이에 따른 조정
        if text_length < 1000:
            max_chunk_size = min(500, text_length // 2)
            overlap_size = max(20, max_chunk_size // 10)
        elif text_length > 100000:
            max_chunk_size = 3000
            overlap_size = 200

        # 목표 청크 수가 지정된 경우 조정
        if target_chunk_count and target_chunk_count > 0:
            estimated_chunk_size = text_length // target_chunk_count
            max_chunk_size = max(500, min(5000, int(estimated_chunk_size * 1.2)))
            overlap_size = max(20, max_chunk_size // 20)

        # 컨텍스트 보존 설정
        preserve_sentences = preserve_context
        preserve_paragraphs = preserve_context and text_length > 5000

        return ChunkingConfig(
            max_chunk_size=max_chunk_size,
            overlap_size=overlap_size,
            min_chunk_size=min_chunk_size,
            preserve_sentences=preserve_sentences,
            preserve_paragraphs=preserve_paragraphs,
        )


# 팩토리 싱글톤 인스턴스
_factory_instance: Optional[ChunkingStrategyFactory] = None


def get_chunking_factory(spacy_processor: Any = None) -> ChunkingStrategyFactory:
    """청킹 팩토리 싱글톤 획득"""
    global _factory_instance

    if _factory_instance is None:
        _factory_instance = ChunkingStrategyFactory(spacy_processor)

    # SpaCy 프로세서가 새로 제공되면 업데이트
    if (
        spacy_processor is not None
        and _factory_instance.spacy_processor != spacy_processor
    ):
        _factory_instance.spacy_processor = spacy_processor
        _factory_instance.spacy_available = True

    return _factory_instance


def create_chunking_strategy(
    method: ChunkingMethod, config: ChunkingConfig, spacy_processor: Any = None
) -> Result[ChunkingStrategy, str]:
    """편의 함수: 청킹 전략 생성"""
    factory = get_chunking_factory(spacy_processor)
    return factory.create_strategy(method, config)
