"""
개선된 Redis 캐시 클라이언트 구현
Redis 6.4.0 직접 사용, RFS Framework 패턴 적용
"""

import json
import hashlib
import asyncio
from typing import Optional, Any, List, Dict
from datetime import timedelta

# Redis 6.4.0 async 클라이언트 사용
import redis.asyncio as redis

from src.shared.kernel import Result, Success, Failure, Mono, Flux
from .redis_config import RedisCloudConfig


class RedisClient:
    """
    개선된 Redis 캐시 클라이언트
    Redis 6.4.0 직접 사용, RFS Framework 패턴 준수
    """

    def __init__(self, redis_config: Optional[RedisCloudConfig] = None):
        """
        생성자 주입 패턴으로 Redis 설정 주입

        Args:
            redis_config: Redis 설정 객체 (None이면 비활성화)
        """
        self.config = redis_config
        self.enabled = redis_config is not None
        self._redis: Optional[redis.Redis] = None
        self._connected = False

        if self.enabled:
            self._initialize_client()

    def _initialize_client(self) -> None:
        """Redis 클라이언트 초기화"""
        if not self.config:
            return

        try:
            # 설정 검증
            validation_result = self.config.validate_connection_params()
            if validation_result.is_failure():
                raise ValueError(validation_result.get_error() or "Validation failed")

            # Redis 연결 매개변수 생성
            connection_params = self.config.get_connection_params()

            # Redis 클라이언트 생성
            self._redis = redis.from_url(
                connection_params["url"],
                decode_responses=connection_params["decode_responses"],
                socket_timeout=connection_params["socket_timeout"],
                socket_connect_timeout=connection_params["socket_connect_timeout"],
                socket_keepalive=connection_params["socket_keepalive"],
                max_connections=connection_params["max_connections"],
                retry_on_timeout=connection_params["retry_on_timeout"],
            )

        except Exception as e:
            # 초기화 실패 시 비활성화
            self.enabled = False
            self._redis = None
            raise ValueError(f"Redis 클라이언트 초기화 실패: {str(e)}")

    async def _ensure_connection(self) -> Result[None, str]:
        """Redis 연결 보장"""
        if not self.enabled or not self._redis:
            return Success(None)

        try:
            # ping으로 연결 확인
            await self._redis.ping()
            self._connected = True
            return Success(None)
        except Exception as e:
            self._connected = False
            return Failure(f"Redis 연결 실패: {str(e)}")

    async def connect(self) -> Result[None, str]:
        """Redis 연결 확인"""
        if not self.enabled or not self._redis:
            return Success(None)

        return await self._ensure_connection()

    async def disconnect(self) -> Result[None, str]:
        """Redis 연결 종료"""
        if self._redis:
            try:
                await self._redis.close()
                self._connected = False
                return Success(None)
            except Exception as e:
                return Failure(f"Redis 연결 종료 실패: {str(e)}")
        return Success(None)

    def get(self, key: str) -> Mono[Optional[str]]:
        """캐시에서 값 조회 (Mono 반환)"""

        async def fetch() -> Optional[str]:
            if not self.enabled or not self._redis:
                return None

            connection_result = await self._ensure_connection()
            if connection_result.is_failure():
                return None

            try:
                value = await self._redis.get(self._namespaced_key(key))
                return str(value) if value is not None else None
            except Exception:
                return None

        return Mono(lambda: asyncio.run(fetch()))

    def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> Mono[Result[None, str]]:
        """캐시에 값 저장 (Mono 반환)"""

        async def store() -> Result[None, str]:
            if not self.enabled or not self._redis:
                return Success(None)

            connection_result = await self._ensure_connection()
            if connection_result.is_failure():
                return Failure(connection_result.get_error() or "Connection failed")

            try:
                # JSON 직렬화 (문자열이 아닌 경우)
                if not isinstance(value, str):
                    try:
                        serialized_value = json.dumps(value, ensure_ascii=False)
                    except (TypeError, ValueError) as e:
                        return Failure(f"직렬화 실패: {str(e)}")
                else:
                    serialized_value = value

                # TTL 설정 (기본 3개월)
                cache_ttl = ttl or (90 * 24 * 60 * 60)  # 90일

                # Redis에 저장
                await self._redis.set(
                    self._namespaced_key(key), serialized_value, ex=cache_ttl
                )
                return Success(None)

            except Exception as e:
                return Failure(f"Redis 저장 실패: {str(e)}")

        return Mono(lambda: asyncio.run(store()))

    def delete(self, key: str) -> Mono[Result[None, str]]:
        """캐시에서 키 삭제 (Mono 반환)"""

        async def remove() -> Result[None, str]:
            if not self.enabled or not self._redis:
                return Success(None)

            connection_result = await self._ensure_connection()
            if connection_result.is_failure():
                return Failure(connection_result.get_error() or "Connection failed")

            try:
                await self._redis.delete(self._namespaced_key(key))
                return Success(None)
            except Exception as e:
                return Failure(f"Redis 삭제 실패: {str(e)}")

        return Mono(lambda: asyncio.run(remove()))

    def exists(self, key: str) -> Mono[bool]:
        """키 존재 확인 (Mono 반환)"""

        async def check() -> bool:
            if not self.enabled or not self._redis:
                return False

            connection_result = await self._ensure_connection()
            if connection_result.is_failure():
                return False

            try:
                result = await self._redis.exists(self._namespaced_key(key))
                return bool(result)
            except Exception:
                return False

        return Mono(lambda: asyncio.run(check()))

    def get_many(self, keys: List[str]) -> Flux[tuple[str, Optional[str]]]:
        """여러 키의 값 조회 (Flux 반환)"""

        async def fetch_values() -> List[tuple[str, Optional[str]]]:
            if not self.enabled or not self._redis:
                return [(k, None) for k in keys]

            connection_result = await self._ensure_connection()
            if connection_result.is_failure():
                return [(k, None) for k in keys]

            try:
                # 네임스페이스 적용된 키들
                namespaced_keys = [self._namespaced_key(k) for k in keys]
                values = await self._redis.mget(namespaced_keys)
                return list(zip(keys, values))
            except Exception:
                return [(k, None) for k in keys]

        return Flux(lambda: asyncio.run(fetch_values()))

    def set_many(
        self, data: dict[str, Any], ttl: Optional[int] = None
    ) -> Mono[Result[None, str]]:
        """여러 키-값 저장 (Mono 반환)"""

        async def store_batch() -> Result[None, str]:
            if not self.enabled or not self._redis:
                return Success(None)

            connection_result = await self._ensure_connection()
            if connection_result.is_failure():
                return Failure(connection_result.get_error() or "Connection failed")

            try:
                # 직렬화 처리
                serialized_data = {}
                for key, value in data.items():
                    namespaced_key = self._namespaced_key(key)

                    if not isinstance(value, str):
                        try:
                            serialized_data[namespaced_key] = json.dumps(
                                value, ensure_ascii=False
                            )
                        except (TypeError, ValueError) as e:
                            return Failure(f"키 {key} 직렬화 실패: {str(e)}")
                    else:
                        serialized_data[namespaced_key] = value

                # 파이프라인을 사용한 배치 저장
                pipe = self._redis.pipeline()

                # 배치 저장 (mset 사용)
                pipe.mset(serialized_data)

                # TTL 설정 (개별 키에 대해)
                cache_ttl = ttl or (90 * 24 * 60 * 60)  # 90일
                if cache_ttl:
                    for namespaced_key in serialized_data.keys():
                        pipe.expire(namespaced_key, cache_ttl)

                # 파이프라인 실행
                await pipe.execute()

                return Success(None)

            except Exception as e:
                return Failure(f"Redis 배치 저장 실패: {str(e)}")

        return Mono(lambda: asyncio.run(store_batch()))

    def _namespaced_key(self, key: str) -> str:
        """네임스페이스가 적용된 키 생성"""
        namespace = self.config.namespace if self.config else "px"
        return f"{namespace}:{key}"

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

        async def fetch_stats() -> dict:
            if not self.enabled or not self._redis:
                return {"enabled": False, "connected": False, "info": None}

            connection_result = await self._ensure_connection()
            if connection_result.is_failure():
                return {
                    "enabled": True,
                    "connected": False,
                    "error": connection_result.get_error() or "Connection failed",
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

        return Mono(lambda: asyncio.run(fetch_stats()))
