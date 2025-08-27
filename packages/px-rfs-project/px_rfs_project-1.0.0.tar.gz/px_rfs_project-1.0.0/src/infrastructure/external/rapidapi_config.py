"""
RapidAPI 설정 관리
RFS Framework 패턴 준수
"""

from typing import Optional, Any, Dict
from dataclasses import dataclass

from src.shared.kernel import Result, Success, Failure
from src.config.settings import Settings
from .rapidapi_client import RapidAPIConfig


class RapidAPIConfigFactory:
    """RapidAPI 설정 팩토리"""

    @staticmethod
    def create_from_settings(settings: Settings) -> Result[RapidAPIConfig, str]:
        """Settings 객체로부터 RapidAPI 설정 생성"""
        if not settings.rapidapi_key:
            return Failure("RapidAPI key not configured")

        try:
            config = RapidAPIConfig(
                api_key=settings.rapidapi_key,
                timeout=30,  # 기본 30초
                max_retries=3,  # 기본 3회 재시도
            )

            # 설정 검증
            validation_result = config.validate()
            if validation_result.is_failure():
                return Failure(validation_result.get_error() or "Config validation failed")

            return Success(config)

        except Exception as e:
            return Failure(f"RapidAPI config creation failed: {str(e)}")

    @staticmethod
    def create_for_environment(
        api_key: str, environment: str = "development", **overrides: Any
    ) -> Result[RapidAPIConfig, str]:
        """환경별 최적화된 RapidAPI 설정 생성"""
        base_config: Dict[str, Any] = {"api_key": api_key}

        # 환경별 기본값
        if environment == "production":
            base_config.update(
                {
                    "timeout": 60,  # 프로덕션에서는 더 긴 타임아웃
                    "max_retries": 5,  # 더 많은 재시도
                }
            )
        elif environment == "development":
            base_config.update({"timeout": 30, "max_retries": 3})  # 개발환경 기본값
        elif environment == "test":
            base_config.update(
                {"timeout": 10, "max_retries": 1}  # 테스트에서는 빠른 실패
            )

        # 사용자 재정의 적용
        base_config.update(overrides)

        try:
            config = RapidAPIConfig(**base_config)

            # 설정 검증
            validation_result = config.validate()
            if validation_result.is_failure():
                return Failure(validation_result.get_error() or "Config validation failed")

            return Success(config)

        except Exception as e:
            return Failure(
                f"Environment-specific RapidAPI config creation failed: {str(e)}"
            )
