"""
파일 텍스트 추출기 모듈
다양한 파일 형식에서 텍스트 추출
"""

from .file_extractor import (
    SupportedFileType,
    FileInfo,
    ExtractedContent,
    FileExtractor,
    TextFileExtractor,
    PDFExtractor,
    PowerPointExtractor,
    WordExtractor,
)

from .extractor_factory import (
    ExtractorFactory,
    get_extractor_factory,
    extract_text_from_file,
)

__all__ = [
    # 파일 타입 및 데이터 클래스
    "SupportedFileType",
    "FileInfo",
    "ExtractedContent",
    # 추출기 클래스들
    "FileExtractor",
    "TextFileExtractor",
    "PDFExtractor",
    "PowerPointExtractor",
    "WordExtractor",
    # 팩토리
    "ExtractorFactory",
    "get_extractor_factory",
    "extract_text_from_file",
]
