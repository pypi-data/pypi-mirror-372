"""
RapidAPI 클라이언트
YouTube 자막, LinkedIn 프로필, 웹사이트 텍스트 추출
"""

import re
import hashlib
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import requests
import asyncio
from urllib.parse import urlparse, parse_qs

from src.shared.kernel import Result, Success, Failure, Mono
from src.shared.hof import pipe, compact_map, safe_map, partition


class ContentSource(str, Enum):
    """콘텐츠 소스 타입"""

    YOUTUBE = "youtube"
    LINKEDIN = "linkedin"
    WEBSITE = "website"


@dataclass
class RapidAPIConfig:
    """RapidAPI 설정"""

    api_key: str
    timeout: int = 30
    max_retries: int = 3

    def validate(self) -> Result[None, str]:
        """설정 검증"""
        if not self.api_key:
            return Failure("RapidAPI key is required")

        if len(self.api_key) < 20:
            return Failure("Invalid RapidAPI key format")

        if self.timeout <= 0:
            return Failure("Timeout must be positive")

        return Success(None)


@dataclass
class ExtractedWebContent:
    """추출된 웹 콘텐츠"""

    text: str
    source_type: ContentSource
    source_url: str
    metadata: Dict[str, Any]
    word_count: Optional[int] = None
    char_count: Optional[int] = None

    def __post_init__(self) -> None:
        if self.word_count is None:
            self.word_count = len(self.text.split())
        if self.char_count is None:
            self.char_count = len(self.text)


class URLValidator:
    """URL 유효성 검증기"""

    @staticmethod
    def validate_youtube_url(url: str) -> Result[str, str]:
        """YouTube URL 검증 및 비디오 ID 추출"""
        youtube_patterns = [
            r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
            r"youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})",
        ]

        # HOF 패턴으로 YouTube URL 검증
        def try_pattern(pattern: str) -> Optional[str]:
            """단일 패턴으로 URL 매칭 시도"""
            match = re.search(pattern, url)
            return match.group(1) if match else None
        
        # compact_map으로 첫 번째 매칭되는 비디오 ID 찾기
        video_ids = compact_map(try_pattern, youtube_patterns)
        
        return Success(video_ids[0]) if video_ids else Failure(f"Invalid YouTube URL: {url}")

    @staticmethod
    def validate_linkedin_url(url: str) -> Result[str, str]:
        """LinkedIn URL 검증 및 사용자명 추출"""
        linkedin_pattern = r"linkedin\.com/in/([a-zA-Z0-9-]+)"
        match = re.search(linkedin_pattern, url)

        if match:
            return Success(match.group(1))

        return Failure(f"Invalid LinkedIn profile URL: {url}")

    @staticmethod
    def validate_website_url(url: str) -> Result[str, str]:
        """일반 웹사이트 URL 검증"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme in ["http", "https"]:
                return Failure("URL must use HTTP or HTTPS protocol")

            if not parsed.netloc:
                return Failure("Invalid URL format")

            return Success(url)

        except Exception as e:
            return Failure(f"URL validation failed: {str(e)}")


class RapidAPIClient:
    """RapidAPI 통합 클라이언트"""

    def __init__(self, config: RapidAPIConfig):
        """
        생성자 주입 패턴으로 설정 주입

        Args:
            config: RapidAPI 설정
        """
        self.config = config
        self.validator = URLValidator()

        # 설정 검증
        validation_result = config.validate()
        if validation_result.is_failure():
            raise ValueError(validation_result.get_error())

        # 기본 헤더 설정
        self.headers = {
            "X-RapidAPI-Key": config.api_key,
            "X-RapidAPI-Host": "",  # API별로 설정
            "Content-Type": "application/json",
        }

    def extract_youtube_subtitles(
        self, youtube_url: str
    ) -> Mono[Result[ExtractedWebContent, str]]:
        """YouTube 비디오 자막 추출"""

        async def extract() -> Result[ExtractedWebContent, str]:
            # URL 검증
            video_id_result = self.validator.validate_youtube_url(youtube_url)
            if video_id_result.is_failure():
                return Failure(video_id_result.get_error() or "Video ID extraction failed")

            video_id = video_id_result.get_or_none()
            if video_id is None:
                return Failure("Video ID extraction failed")

            try:
                # YouTube 자막 API 호출
                subtitles_result = self._fetch_youtube_subtitles(video_id)
                if subtitles_result.is_failure():
                    return Failure(subtitles_result.get_error() or "Subtitles fetch failed")

                subtitles_data = subtitles_result.get_or_none()
                if subtitles_data is None:
                    return Failure("Subtitles data is None")

                # 자막 텍스트 추출
                text = self._parse_youtube_subtitles(subtitles_data)

                # 메타데이터 생성
                metadata = {
                    "video_id": video_id,
                    "source_url": youtube_url,
                    "extractor": "RapidAPI_YouTube",
                    "language": subtitles_data.get("language", "unknown"),
                    "duration": subtitles_data.get("duration"),
                    "title": subtitles_data.get("title", ""),
                }

                content = ExtractedWebContent(
                    text=text,
                    source_type=ContentSource.YOUTUBE,
                    source_url=youtube_url,
                    metadata=metadata,
                )

                return Success(content)

            except Exception as e:
                return Failure(f"YouTube subtitle extraction failed: {str(e)}")

        return Mono(lambda: asyncio.run(extract()))

    def extract_linkedin_profile(
        self, linkedin_url: str
    ) -> Mono[Result[ExtractedWebContent, str]]:
        """LinkedIn 프로필 정보 추출"""

        async def extract() -> Result[ExtractedWebContent, str]:
            # URL 검증
            username_result = self.validator.validate_linkedin_url(linkedin_url)
            if username_result.is_failure():
                return Failure(username_result.get_error() or "LinkedIn URL validation failed")

            username = username_result.get_or_none()
            if username is None:
                return Failure("Username extraction failed")

            try:
                # LinkedIn 프로필 API 호출
                profile_result = self._fetch_linkedin_profile(username)
                if profile_result.is_failure():
                    return Failure(profile_result.get_error() or "LinkedIn profile fetch failed")

                profile_data = profile_result.get_or_none()
                if profile_data is None:
                    return Failure("LinkedIn profile data is None")

                # 프로필 텍스트 추출
                text = self._parse_linkedin_profile(profile_data)

                # 메타데이터 생성
                metadata = {
                    "username": username,
                    "source_url": linkedin_url,
                    "extractor": "RapidAPI_LinkedIn",
                    "profile_data": {
                        "name": profile_data.get("name", ""),
                        "headline": profile_data.get("headline", ""),
                        "location": profile_data.get("location", ""),
                        "industry": profile_data.get("industry", ""),
                    },
                }

                content = ExtractedWebContent(
                    text=text,
                    source_type=ContentSource.LINKEDIN,
                    source_url=linkedin_url,
                    metadata=metadata,
                )

                return Success(content)

            except Exception as e:
                return Failure(f"LinkedIn profile extraction failed: {str(e)}")

        return Mono(lambda: asyncio.run(extract()))

    def extract_website_content(
        self, website_url: str
    ) -> Mono[Result[ExtractedWebContent, str]]:
        """웹사이트 텍스트 내용 추출"""

        async def extract() -> Result[ExtractedWebContent, str]:
            # URL 검증
            url_result = self.validator.validate_website_url(website_url)
            if url_result.is_failure():
                return Failure(url_result.get_error() or "Website URL validation failed")

            validated_url = url_result.get_or_none()
            if validated_url is None:
                return Failure("URL validation failed")

            try:
                # 웹사이트 콘텐츠 API 호출
                content_result = self._fetch_website_content(validated_url)
                if content_result.is_failure():
                    return Failure(content_result.get_error() or "Website content fetch failed")

                content_data = content_result.get_or_none()
                if content_data is None:
                    return Failure("Website content data is None")

                # 웹사이트 텍스트 추출
                text = self._parse_website_content(content_data)

                # 메타데이터 생성
                metadata = {
                    "source_url": website_url,
                    "extractor": "RapidAPI_Website",
                    "title": content_data.get("title", ""),
                    "description": content_data.get("description", ""),
                    "domain": urlparse(website_url).netloc,
                }

                content = ExtractedWebContent(
                    text=text,
                    source_type=ContentSource.WEBSITE,
                    source_url=website_url,
                    metadata=metadata,
                )

                return Success(content)

            except Exception as e:
                return Failure(f"Website content extraction failed: {str(e)}")

        return Mono(lambda: asyncio.run(extract()))

    def _fetch_youtube_subtitles(self, video_id: str) -> Result[Dict[str, Any], str]:
        """YouTube 자막 API 호출"""
        try:
            # 실제 RapidAPI YouTube 자막 서비스 호출
            # 여기서는 Mock 데이터로 대체
            headers = {
                **self.headers,
                "X-RapidAPI-Host": "youtube-subtitle-downloader.p.rapidapi.com",
            }

            # API 호출 (실제 구현에서는 실제 API 엔드포인트 사용)
            response_data = {
                "video_id": video_id,
                "title": "Sample Video Title",
                "language": "ko",
                "duration": "00:10:30",
                "subtitles": [
                    {
                        "start_time": "00:00:01",
                        "end_time": "00:00:05",
                        "text": "안녕하세요, 첫 번째 자막입니다.",
                    },
                    {
                        "start_time": "00:00:06",
                        "end_time": "00:00:10",
                        "text": "두 번째 자막 내용입니다.",
                    },
                ],
            }

            return Success(response_data)

        except Exception as e:
            return Failure(f"YouTube API call failed: {str(e)}")

    def _fetch_linkedin_profile(self, username: str) -> Result[Dict[str, Any], str]:
        """LinkedIn 프로필 API 호출"""
        try:
            # 실제 RapidAPI LinkedIn 서비스 호출
            # 여기서는 Mock 데이터로 대체
            headers = {
                **self.headers,
                "X-RapidAPI-Host": "linkedin-profile-scraper.p.rapidapi.com",
            }

            # API 호출 (실제 구현에서는 실제 API 엔드포인트 사용)
            response_data = {
                "username": username,
                "name": "홍길동",
                "headline": "소프트웨어 개발자",
                "location": "서울, 대한민국",
                "industry": "정보기술",
                "summary": "10년 경력의 풀스택 개발자입니다. Python, JavaScript, React 전문가입니다.",
                "experience": [
                    {
                        "title": "시니어 개발자",
                        "company": "테크 회사",
                        "duration": "2020-현재",
                        "description": "웹 애플리케이션 개발 및 팀 리딩",
                    }
                ],
            }

            return Success(response_data)

        except Exception as e:
            return Failure(f"LinkedIn API call failed: {str(e)}")

    def _fetch_website_content(self, url: str) -> Result[Dict[str, Any], str]:
        """웹사이트 콘텐츠 API 호출"""
        try:
            # 실제 RapidAPI 웹사이트 스크래핑 서비스 호출
            # 여기서는 Mock 데이터로 대체
            headers = {
                **self.headers,
                "X-RapidAPI-Host": "website-content-extractor.p.rapidapi.com",
            }

            # API 호출 (실제 구현에서는 실제 API 엔드포인트 사용)
            response_data = {
                "url": url,
                "title": "웹사이트 제목",
                "description": "웹사이트 설명",
                "content": "웹사이트의 주요 텍스트 내용입니다. 이 부분에 실제 웹페이지의 텍스트가 포함됩니다.",
                "headings": ["제목1", "제목2", "제목3"],
                "links": ["https://example1.com", "https://example2.com"],
            }

            return Success(response_data)

        except Exception as e:
            return Failure(f"Website API call failed: {str(e)}")

    def _parse_youtube_subtitles(self, subtitles_data: Dict[str, Any]) -> str:
        """YouTube 자막 데이터 파싱"""
        subtitles = subtitles_data.get("subtitles", [])
        text_parts = []

        # HOF 패턴으로 자막 텍스트 추출
        text_parts = compact_map(
            lambda subtitle: subtitle.get("text") if subtitle.get("text") else None,
            subtitles
        )

        return " ".join(text_parts)

    def _parse_linkedin_profile(self, profile_data: Dict[str, Any]) -> str:
        """LinkedIn 프로필 데이터 파싱"""
        text_parts = []

        # 기본 정보
        if profile_data.get("name"):
            text_parts.append(f"이름: {profile_data['name']}")

        if profile_data.get("headline"):
            text_parts.append(f"직책: {profile_data['headline']}")

        if profile_data.get("location"):
            text_parts.append(f"위치: {profile_data['location']}")

        if profile_data.get("summary"):
            text_parts.append(f"요약: {profile_data['summary']}")

        # 경력 정보 - HOF 패턴으로 처리
        experiences = profile_data.get("experience", [])
        if experiences:
            text_parts.append("경력:")
            
            def format_experience(exp: dict) -> str:
                """경력 항목 포맷팅"""
                exp_text = f"- {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})"
                if exp.get("description"):
                    exp_text += f": {exp['description']}"
                return exp_text
            
            experience_texts = [format_experience(exp) for exp in experiences]
            text_parts.extend(experience_texts)

        return "\n".join(text_parts)

    def _parse_website_content(self, content_data: Dict[str, Any]) -> str:
        """웹사이트 콘텐츠 데이터 파싱"""
        text_parts = []

        # 제목
        if content_data.get("title"):
            text_parts.append(f"제목: {content_data['title']}")

        # 설명
        if content_data.get("description"):
            text_parts.append(f"설명: {content_data['description']}")

        # 주요 내용
        if content_data.get("content"):
            text_parts.append(f"내용:\n{content_data['content']}")

        # 헤딩들 - HOF 패턴으로 처리
        headings = content_data.get("headings", [])
        if headings:
            text_parts.append("주요 제목들:")
            heading_texts = [f"- {heading}" for heading in headings]
            text_parts.extend(heading_texts)

        return "\n\n".join(text_parts)

    def get_cache_key(self, source_type: ContentSource, identifier: str) -> str:
        """캐시 키 생성"""
        if source_type == ContentSource.YOUTUBE:
            return f"youtube_subtitle:{identifier}"
        elif source_type == ContentSource.LINKEDIN:
            return f"linkedin_profile:{identifier}"
        elif source_type == ContentSource.WEBSITE:
            url_hash = hashlib.md5(identifier.encode()).hexdigest()[:16]
            return f"website:text:{url_hash}"
        # 모든 ContentSource case가 처리됨
        # else:
        #     return f"unknown:{identifier}"
