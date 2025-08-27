"""
파일 추출기 팩토리
파일 형식에 따라 적절한 추출기 선택
"""

from typing import Optional, Dict, List, Any
from pathlib import Path

from src.shared.kernel import Result, Success, Failure
from src.shared.hof import pipe, compact_map
from .file_extractor import (
    FileExtractor,
    SupportedFileType,
    TextFileExtractor,
    PDFExtractor,
    PowerPointExtractor,
    WordExtractor,
    FileInfo,
)


class ExtractorFactory:
    """파일 추출기 팩토리"""

    def __init__(self) -> None:
        self._extractors: Dict[SupportedFileType, FileExtractor] = {
            SupportedFileType.TXT: TextFileExtractor(),
            SupportedFileType.MD: TextFileExtractor(),
            SupportedFileType.MARKDOWN: TextFileExtractor(),
            SupportedFileType.PDF: PDFExtractor(),
            SupportedFileType.PPTX: PowerPointExtractor(),
            SupportedFileType.DOCX: WordExtractor(),
        }

    def get_extractor(self, file_info: "FileInfo") -> FileExtractor:
        """FileInfo 객체로부터 적절한 추출기 반환"""
        # 확장자로부터 파일 타입 결정
        extension = file_info.extension.lower()

        # 확장자별 매핑
        extension_mapping = {
            ".txt": SupportedFileType.TXT,
            ".md": SupportedFileType.MD,
            ".markdown": SupportedFileType.MARKDOWN,
            ".pdf": SupportedFileType.PDF,
            ".pptx": SupportedFileType.PPTX,
            ".docx": SupportedFileType.DOCX,
        }

        file_type = extension_mapping.get(extension)
        if not file_type:
            # 기본적으로 텍스트 파일로 처리
            file_type = SupportedFileType.TXT

        return self._extractors[file_type]

    def get_extractor_by_path(self, file_path: str) -> Result[FileExtractor, str]:
        """파일 경로로부터 적절한 추출기 반환 (기존 메서드)"""
        file_type_result = self.detect_file_type(file_path)
        if file_type_result.is_failure():
            return Failure(file_type_result.get_error() or "File type detection failed")

        file_type = file_type_result.get_or_none()
        if file_type is None:
            return Failure("File type detection returned None")
        extractor = self._extractors.get(file_type)

        if not extractor:
            return Failure(f"Unsupported file type: {file_type}")

        return Success(extractor)

    def get_extractor_by_type(
        self, file_type: SupportedFileType
    ) -> Result[FileExtractor, str]:
        """파일 형식으로 추출기 반환"""
        extractor = self._extractors.get(file_type)

        if not extractor:
            return Failure(f"No extractor available for file type: {file_type}")

        return Success(extractor)

    def detect_file_type(self, file_path: str) -> Result[SupportedFileType, str]:
        """파일 확장자로 파일 형식 감지 - Result 모나드 패턴"""
        
        def safe_path_processing(file_path: str) -> Result[SupportedFileType, str]:
            """안전한 파일 경로 처리"""
            try:
                path = Path(file_path)
                extension = path.suffix.lower()

                # 확장자별 파일 타입 매핑
                extension_mapping = {
                    ".txt": SupportedFileType.TXT,
                    ".md": SupportedFileType.MD,
                    ".markdown": SupportedFileType.MARKDOWN,
                    ".pdf": SupportedFileType.PDF,
                    ".pptx": SupportedFileType.PPTX,
                    ".docx": SupportedFileType.DOCX,
                }

                file_type = extension_mapping.get(extension)
                if not file_type:
                    return Failure(f"Unsupported file extension: {extension}")

                return Success(file_type)

            except Exception as e:
                return Failure(f"Failed to detect file type: {str(e)}")
        
        return safe_path_processing(file_path)

    def is_supported_file(self, file_path: str) -> bool:
        """지원되는 파일인지 확인"""
        return self.detect_file_type(file_path).is_success()

    def get_supported_extensions(self) -> List[str]:
        """지원되는 파일 확장자 목록"""
        return [".txt", ".md", ".markdown", ".pdf", ".pptx", ".docx"]

    def get_supported_mime_types(self) -> List[str]:
        """지원되는 MIME 타입 목록"""
        return [
            "text/plain",
            "text/markdown",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]

    def validate_file_for_extraction(self, file_path: str) -> Result[FileInfo, str]:
        """추출 가능한 파일인지 검증하고 FileInfo 반환 - Result 모나드 패턴"""
        
        def safe_file_validation(file_path: str) -> Result[FileInfo, str]:
            """안전한 파일 검증 처리"""
            try:
                # 파일 존재 여부 확인
                if not Path(file_path).exists():
                    return Failure(f"File not found: {file_path}")

                # 파일 형식 지원 여부 확인
                if not self.is_supported_file(file_path):
                    extension = Path(file_path).suffix
                    return Failure(f"Unsupported file type: {extension}")

                # FileInfo 생성
                file_info = FileInfo.from_path(file_path)

                # 기본 검증 (크기, 접근성 등)
                extractor = self.get_extractor(file_info)
                validation_result = extractor.validate_file(file_info)
                if validation_result.is_failure():
                    return Failure(validation_result.get_error() or "File validation failed")

                return Success(file_info)

            except Exception as e:
                return Failure(f"File validation failed: {str(e)}")
        
        return safe_file_validation(file_path)

    def get_extractor_info(self) -> Dict[str, Dict[str, Any]]:
        """등록된 추출기 정보 반환 - HOF 패턴 적용"""
        
        def create_extractor_info(item: tuple) -> tuple[str, Dict[str, Any]]:
            """추출기 항목에서 정보 생성"""
            file_type, extractor = item
            return file_type.value, {
                "extractor_class": extractor.__class__.__name__,
                "supported_extensions": self._get_extensions_for_type(file_type),
                "description": self._get_extractor_description(extractor),
            }
        
        # HOF 패턴으로 딕셔너리 생성
        return dict(create_extractor_info(item) for item in self._extractors.items())

    def _get_extensions_for_type(self, file_type: SupportedFileType) -> List[str]:
        """파일 타입별 지원 확장자"""
        mapping = {
            SupportedFileType.TXT: [".txt"],
            SupportedFileType.MD: [".md"],
            SupportedFileType.MARKDOWN: [".markdown"],
            SupportedFileType.PDF: [".pdf"],
            SupportedFileType.PPTX: [".pptx"],
            SupportedFileType.DOCX: [".docx"],
        }
        return mapping.get(file_type, [])

    def _get_extractor_description(self, extractor: FileExtractor) -> str:
        """추출기 설명"""
        descriptions = {
            TextFileExtractor: "플레인 텍스트 및 마크다운 파일 추출기",
            PDFExtractor: "PDF 문서 텍스트 추출기 (PyPDF2/PyMuPDF)",
            PowerPointExtractor: "PowerPoint 프레젠테이션 텍스트 추출기",
            WordExtractor: "Word 문서 텍스트 추출기",
        }
        return descriptions.get(type(extractor), "파일 텍스트 추출기")


# 전역 팩토리 인스턴스 (싱글톤)
_extractor_factory: Optional[ExtractorFactory] = None


def get_extractor_factory() -> ExtractorFactory:
    """추출기 팩토리 싱글톤 인스턴스 반환"""
    global _extractor_factory
    if _extractor_factory is None:
        _extractor_factory = ExtractorFactory()
    return _extractor_factory


def extract_text_from_file(file_path: str) -> Result[str, str]:
    """파일에서 텍스트 추출 (편의 함수)"""
    factory = get_extractor_factory()

    # 파일 검증
    file_info_result = factory.validate_file_for_extraction(file_path)
    if file_info_result.is_failure():
        return Failure(file_info_result.get_error() or "File validation failed")

    file_info = file_info_result.get_or_none()
    if file_info is None:
        return Failure("File validation returned None")

    # 추출기 가져오기
    extractor = factory.get_extractor(file_info)

    # 텍스트 추출 (동기 방식)
    try:
        import asyncio

        async def extract() -> Result[str, str]:
            content_result = await extractor.extract_text(file_info).to_result()
            if content_result.is_success():
                content = content_result.get_or_none()
                if content is None:
                    return Failure("Text extraction returned None")
                return Success(content.text if hasattr(content, 'text') else str(content))
            return Failure(content_result.get_error() or "Text extraction failed")

        # 이벤트 루프가 있으면 사용, 없으면 새로 생성
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 이미 실행 중인 루프에서는 create_task 사용
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, extract())
                    return future.result()
            else:
                return loop.run_until_complete(extract())
        except RuntimeError:
            return asyncio.run(extract())

    except Exception as e:
        return Failure(f"Text extraction failed: {str(e)}")
