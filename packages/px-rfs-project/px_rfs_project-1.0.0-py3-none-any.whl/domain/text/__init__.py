"""
텍스트 처리 도메인 레이어
청킹 전략과 텍스트 처리 서비스
"""

from .chunking_strategy import (
    ChunkingMethod,
    ChunkingConfig,
    TextChunk,
    ChunkingStrategy,
    FixedSizeChunkingStrategy,
    SemanticChunkingStrategy,
    ParagraphChunkingStrategy,
)

from .chunking_factory import ChunkingStrategyFactory

from .text_processor import TextProcessingRequest, TextProcessingResult, TextProcessor

__all__ = [
    # 청킹 전략
    "ChunkingMethod",
    "ChunkingConfig",
    "TextChunk",
    "ChunkingStrategy",
    "FixedSizeChunkingStrategy",
    "SemanticChunkingStrategy",
    "ParagraphChunkingStrategy",
    # 청킹 팩토리
    "ChunkingStrategyFactory",
    # 텍스트 프로세서
    "TextProcessingRequest",
    "TextProcessingResult",
    "TextProcessor",
]
