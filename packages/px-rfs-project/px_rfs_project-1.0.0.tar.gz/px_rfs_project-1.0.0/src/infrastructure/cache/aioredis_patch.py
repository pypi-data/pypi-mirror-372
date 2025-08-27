"""
aioredis Python 3.12 호환성 패치
TimeoutError 중복 상속 문제 해결
"""

import sys
import builtins
import asyncio
from typing import Any


def patch_aioredis_for_python312() -> None:
    """Python 3.12에서 aioredis TimeoutError 문제 패치"""

    # Python 3.12에서만 패치 적용
    if sys.version_info < (3, 12):
        return

    # asyncio.TimeoutError와 builtins.TimeoutError가 같은지 확인
    if asyncio.TimeoutError is builtins.TimeoutError:
        try:
            import aioredis.exceptions  # type: ignore[import-not-found]

            # TimeoutError 클래스를 다시 정의
            class PatchedTimeoutError(asyncio.TimeoutError):
                """Python 3.12 호환 TimeoutError"""

                pass

            # aioredis.exceptions 모듈의 TimeoutError를 교체
            aioredis.exceptions.TimeoutError = PatchedTimeoutError

            print("✅ aioredis Python 3.12 호환성 패치 적용 완료")

        except (ImportError, AttributeError) as e:
            print(f"⚠️ aioredis 패치 적용 실패: {e}")


def safe_import_aioredis() -> Any:
    """안전한 aioredis 임포트"""
    try:
        # 패치 적용
        patch_aioredis_for_python312()

        # aioredis 임포트
        import aioredis

        return aioredis

    except Exception as e:
        print(f"❌ aioredis 임포트 실패: {e}")
        return None


if __name__ == "__main__":
    # 패치 테스트
    patch_aioredis_for_python312()
    try:
        import aioredis

        print("✅ aioredis 임포트 성공")
    except Exception as e:
        print(f"❌ aioredis 임포트 실패: {e}")
