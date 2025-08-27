"""
Redis 캐시 클라이언트 구현 (RFS Framework 4.3.1 사용)
수정된 RFS Framework로 복원, 생성자 주입 패턴 유지
"""

import json
import hashlib
import asyncio
from typing import Optional, Any, List, Dict
from datetime import timedelta

# RFS Framework 정식 버전 사용
from rfs.cache import RedisCache, RedisCacheConfig
from src.shared.kernel import Result, Success, Failure, Mono, Flux
from .redis_config import RedisCloudConfig


class RedisClient:
    """
    Redis 캐시 클라이언트 (RFS Framework 4.3.1 사용)
    생성자 주입 패턴, RFS Framework 정식 RedisCache 사용
    """

    def __init__(self, redis_config: Optional[RedisCloudConfig] = None):
        """
        생성자 주입 패턴으로 Redis 설정 주입

        Args:
            redis_config: Redis 설정 객체 (None이면 비활성화)
        """
        self.config = redis_config
        self.enabled = redis_config is not None
        self._cache: Optional[RedisCache] = None

        if self.enabled:
            self._initialize_cache()

    def _initialize_cache(self):
        """RFS Redis Cache 초기화"""
        if not self.config:
            return

        try:
            # 설정 검증
            validation_result = self.config.validate_connection_params()
            if validation_result.is_failure():
                raise ValueError(validation_result.error)

            # RFS RedisCacheConfig 생성
            rfs_config_dict = self.config.get_rfs_cache_config()
            rfs_config = RedisCacheConfig(**rfs_config_dict)

            # Redis Cache 인스턴스 생성
            self._cache = RedisCache(rfs_config)

        except Exception as e:
            # 초기화 실패 시 비활성화
            self.enabled = False
            self._cache = None
            raise ValueError(f"Redis Cache 초기화 실패: {str(e)}")

    async def connect(self) -> Result[None, str]:
        """Redis 연결 확인"""
        if not self.enabled or not self._cache:
            return Success(None)

        result = await self._cache.connect()
        if hasattr(result, 'is_failure') and result.is_failure():
            return Failure(str(result.get_error() if hasattr(result, 'get_error') else result))
        return Success(None)

    async def disconnect(self) -> Result[None, str]:
        """Redis 연결 종료"""
        if self._cache:
            result = await self._cache.disconnect()
            if hasattr(result, 'is_failure') and result.is_failure():
                return Failure(str(result.get_error() if hasattr(result, 'get_error') else result))
            return Success(None)
        return Success(None)

    def get(self, key: str) -> Mono[Optional[str]]:
        """캐시에서 값 조회 (Mono 반환)"""

        async def fetch():
            if not self.enabled:
                return None

            result = await self._cache.get(key)
            if result.is_success():
                return result.value
            return None

        return Mono.from_callable(fetch)

    def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> Mono[Result[None, str]]:
        """캐시에 값 저장 (Mono 반환)"""

        async def store():
            if not self.enabled:
                return Success(None)

            connection_result = await self._ensure_connection()
            if connection_result.is_failure():
                return Failure(connection_result.error)

            try:
                # JSON 직렬화 (문자열이 아닌 경우)
                if not isinstance(value, str):
                    try:
                        serialized_value = json.dumps(value, ensure_ascii=False)
                    except (TypeError, ValueError) as e:
                        return Failure(f"Serialization failed: {str(e)}")
                else:
                    serialized_value = value

                # TTL 설정 (기본 3개월)
                cache_ttl = ttl or (90 * 24 * 60 * 60)  # 90일

                await self._redis.set(key, serialized_value, ex=cache_ttl)
                return Success(None)

            except Exception as e:
                return Failure(f"Redis set 실패: {str(e)}")

        return Mono.from_callable(store)

    def delete(self, key: str) -> Mono[Result[None, str]]:
        """캐시에서 키 삭제 (Mono 반환)"""

        async def remove():
            if not self.enabled:
                return Success(None)

            connection_result = await self._ensure_connection()
            if connection_result.is_failure():
                return Failure(connection_result.error)

            try:
                await self._redis.delete(key)
                return Success(None)
            except Exception as e:
                return Failure(f"Redis delete 실패: {str(e)}")

        return Mono.from_callable(remove)

    def exists(self, key: str) -> Mono[bool]:
        """키 존재 확인 (Mono 반환)"""

        async def check():
            if not self.enabled:
                return False

            connection_result = await self._ensure_connection()
            if connection_result.is_failure():
                return False

            try:
                result = await self._redis.exists(key)
                return bool(result)
            except Exception:
                return False

        return Mono.from_callable(check)

    def get_many(self, keys: List[str]) -> Flux[tuple[str, Optional[str]]]:
        """여러 키의 값 조회 (Flux 반환)"""

        async def fetch_values():
            if not self.enabled:
                return [(k, None) for k in keys]

            connection_result = await self._ensure_connection()
            if connection_result.is_failure():
                return [(k, None) for k in keys]

            try:
                values = await self._redis.mget(keys)
                return list(zip(keys, values))
            except Exception:
                return [(k, None) for k in keys]

        return Flux(lambda: asyncio.run(fetch_values()))

    def set_many(
        self, data: dict[str, Any], ttl: Optional[int] = None
    ) -> Mono[Result[None, str]]:
        """여러 키-값 저장 (Mono 반환)"""

        async def store_batch():
            if not self.enabled:
                return Success(None)

            connection_result = await self._ensure_connection()
            if connection_result.is_failure():
                return Failure(connection_result.error)

            try:
                # 직렬화 처리
                serialized_data = {}
                for key, value in data.items():
                    if not isinstance(value, str):
                        try:
                            serialized_data[key] = json.dumps(value, ensure_ascii=False)
                        except (TypeError, ValueError) as e:
                            return Failure(
                                f"Serialization failed for key {key}: {str(e)}"
                            )
                    else:
                        serialized_data[key] = value

                # 배치 저장 (mset 사용)
                await self._redis.mset(serialized_data)

                # TTL 설정 (개별 키에 대해)
                cache_ttl = ttl or (90 * 24 * 60 * 60)  # 90일
                if cache_ttl:
                    for key in serialized_data.keys():
                        await self._redis.expire(key, cache_ttl)

                return Success(None)

            except Exception as e:
                return Failure(f"Redis mset 실패: {str(e)}")

        return Mono.from_callable(store_batch)

    # 캐시 키 생성 헬퍼 메소드
    @staticmethod
    def youtube_key(video_id: str) -> str:
        """YouTube 자막 캐시 키 생성"""
        return f"youtube_subtitle:{video_id}"

    @staticmethod
    def linkedin_key(username: str) -> str:
        """LinkedIn 프로필 캐시 키 생성"""
        return f"linkedin_profile:{username}"

    @staticmethod
    def website_key(url: str) -> str:
        """웹사이트 텍스트 캐시 키 생성"""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:16]
        return f"website:text:{url_hash}"

    @staticmethod
    def file_key(filename: str, file_hash: str) -> str:
        """파일 텍스트 캐시 키 생성"""
        return f"file:text:{file_hash[:16]}:{filename}"

    # 사용자 정의 캐시 키 생성
    def create_key(self, prefix: str, identifier: str) -> str:
        """범용 캐시 키 생성"""
        return f"{prefix}:{identifier}"

    # 캐시 통계 조회
    def get_stats(self) -> Mono[dict]:
        """캐시 통계 조회 (Mono 반환)"""

        async def fetch_stats():
            if not self.enabled or not self._redis:
                return {"enabled": False, "connected": False, "info": None}

            connection_result = await self._ensure_connection()
            if connection_result.is_failure():
                return {
                    "enabled": True,
                    "connected": False,
                    "error": connection_result.error,
                }

            try:
                info = await self._redis.info()
                return {
                    "enabled": True,
                    "connected": self._connected,
                    "info": {
                        "used_memory_human": info.get("used_memory_human"),
                        "connected_clients": info.get("connected_clients"),
                        "total_commands_processed": info.get(
                            "total_commands_processed"
                        ),
                        "keyspace_hits": info.get("keyspace_hits", 0),
                        "keyspace_misses": info.get("keyspace_misses", 0),
                        "uptime_in_seconds": info.get("uptime_in_seconds"),
                    },
                }
            except Exception as e:
                return {
                    "enabled": True,
                    "connected": False,
                    "error": f"통계 조회 실패: {str(e)}",
                }

        return Mono.from_callable(fetch_stats)
