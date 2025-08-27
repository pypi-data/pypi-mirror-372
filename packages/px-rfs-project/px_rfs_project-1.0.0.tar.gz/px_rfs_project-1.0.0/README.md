# PX - RFS Framework 기반 Python 프로젝트

RFS Framework Enterprise Architecture를 따르는 Python FastAPI 프로젝트입니다.

## 📋 개요

이 프로젝트는 RFS Framework의 핵심 원칙을 준수하여 구축되었습니다:
- **Result 패턴**: 예외 대신 안전한 Result 타입 사용
- **헥사고날 아키텍처**: 계층 분리와 의존성 역전
- **함수형 프로그래밍**: 불변성과 순수 함수 선호
- **한글 주석**: 명확한 한국어 문서화

## 🚀 빠른 시작

### 환경 설정
```bash
# 가상환경 생성 및 활성화 (필수!)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는 venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements-dev.txt

# 개발 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 개발 도구
```bash
# 테스트 실행
pytest
pytest --cov=app --cov-report=html  # 커버리지 포함

# 코드 포맷팅 및 검사
black .
isort .
flake8

# RFS Framework 규칙 검증
python scripts/validate_rfs_rules.py --mode strict
```

## 📁 프로젝트 구조

```
px/
├── src/                          # 소스 코드 루트
│   ├── api/                     # API 계층 (진입점)
│   │   ├── rest/v1/             # REST API v1
│   │   │   ├── controllers/     # HTTP 컨트롤러
│   │   │   ├── routes/          # 라우트 정의
│   │   │   └── middleware/      # API 미들웨어
│   │   └── graphql/             # GraphQL (선택사항)
│   │
│   ├── application/             # 애플리케이션 계층 (유스케이스)
│   │   ├── use_cases/           # 비즈니스 유스케이스
│   │   ├── services/            # 애플리케이션 서비스
│   │   ├── dto/                 # 데이터 전송 객체
│   │   └── mappers/             # DTO-Domain 매핑
│   │
│   ├── domain/                  # 도메인 계층 (핵심 비즈니스)
│   │   ├── models/              # 도메인 모델
│   │   ├── repositories/        # 리포지토리 인터페이스
│   │   ├── services/            # 도메인 서비스
│   │   └── events/              # 도메인 이벤트
│   │
│   ├── infrastructure/          # 인프라스트럭처 계층
│   │   ├── persistence/         # 데이터 영속성
│   │   ├── messaging/           # 메시징 시스템
│   │   ├── external/            # 외부 서비스 연동
│   │   └── cache/               # 캐싱 계층
│   │
│   ├── shared/                  # 공유 모듈
│   │   ├── kernel/              # 핵심 패턴 (Result, Monad)
│   │   ├── exceptions/          # 커스텀 예외
│   │   └── utils/               # 유틸리티
│   │
│   └── config/                  # 설정
│       ├── environments/        # 환경별 설정
│       └── dependencies.py      # 의존성 주입
│
├── tests/                       # 테스트 스위트
├── scripts/                     # 운영 스크립트
├── rules/                       # RFS 규칙 문서
└── docs/                        # 프로젝트 문서
```

## 🔧 RFS Framework 규칙 준수

### ⚠️ 필수 준수 사항

이 프로젝트는 다음 규칙들을 **반드시** 준수해야 합니다:

#### 1. RFS Framework 우선 사용
```python
# ✅ 올바른 방법: Framework 패턴 사용
from rfs.core.result import Result, Success, Failure

def process_user(data: dict) -> Result[User, str]:
    if not data:
        return Failure("데이터가 없습니다")
    return Success(User(**data))

# ❌ 잘못된 방법: 커스텀 구현
def process_user(data):
    if not data:
        raise ValueError("Invalid data")  # 금지!
    return User(**data)
```

#### 2. Result 패턴 필수 사용
```python
# ✅ 모든 비즈니스 로직은 Result 반환
async def create_order(data: dict) -> Result[Order, str]:
    return (
        validate_order_data(data)
        .bind(check_inventory)
        .bind(process_payment)
        .bind(create_order_entity)
    )
```

#### 3. 한글 주석 필수
```python
def calculate_total(items: List[Item]) -> Result[Decimal, str]:
    """
    주문 아이템들의 총 가격을 계산합니다.
    
    Args:
        items: 가격을 계산할 아이템 목록
        
    Returns:
        Result[Decimal, str]: 총액 또는 에러 메시지
    """
    # 빈 목록 검증
    if not items:
        return Failure("아이템이 없습니다")
    
    # 총액 계산
    total = sum(item.price for item in items)
    return Success(total)
```

#### 4. 불변성 유지
```python
from dataclasses import dataclass

@dataclass(frozen=True)  # 필수: 불변 객체
class User:
    id: str
    name: str
    email: str
    
    def update_name(self, new_name: str) -> 'User':
        """이름 업데이트 시 새 인스턴스 반환"""
        return dataclass.replace(self, name=new_name)
```

#### 5. 타입 힌트 필수
```python
# 모든 함수는 완전한 타입 힌트 포함
def process_payment(
    amount: Decimal, 
    payment_method: PaymentMethod,
    user_id: str
) -> Result[Payment, str]:
    """결제를 처리합니다."""
    pass
```

### 🔍 규칙 검증

#### 자동 검증 실행
```bash
# 엄격 모드로 모든 규칙 검증
python scripts/validate_rfs_rules.py --mode strict

# 경고 포함 검증
python scripts/validate_rfs_rules.py --mode warning

# JSON 형식 보고서
python scripts/validate_rfs_rules.py --report json --output report.json

# 자동 수정 가능한 항목 확인
python scripts/validate_rfs_rules.py --fix
```

#### Pre-commit 훅 사용
```bash
# Pre-commit 설치 및 설정
pip install pre-commit
pre-commit install

# 수동 실행
pre-commit run --all-files
```

### 📋 개발 체크리스트

#### 코드 작성 전
- [ ] RFS Framework에서 기존 구현 검색
- [ ] Result 패턴 사용 계획
- [ ] 의존성 주입 설계
- [ ] 불변성 유지 방법 계획

#### 코드 작성 중  
- [ ] 모든 주석을 한글로 작성
- [ ] 예외 대신 Result 반환
- [ ] 타입 힌트 완전 작성
- [ ] 불변 데이터 구조 사용

#### 코드 작성 후
- [ ] 테스트 작성 (Result 패턴 사용)
- [ ] 자동 검증 실행 및 통과
- [ ] 코드 리뷰 준비
- [ ] 문서 업데이트

## 🧪 테스트

### 테스트 실행
```bash
# 모든 테스트 실행
pytest

# 커버리지 포함
pytest --cov=src --cov-report=html --cov-report=term

# 특정 테스트만 실행
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### 테스트 작성 예제
```python
import pytest
from rfs.core.result import Success, Failure

class TestUserService:
    @pytest.mark.asyncio
    async def test_사용자_생성_성공(self):
        """유효한 데이터로 사용자 생성 시 성공해야 함"""
        # Given
        user_data = {"email": "test@example.com", "name": "테스트"}
        
        # When
        result = await user_service.create_user(user_data)
        
        # Then
        assert result.is_success()
        user = result.unwrap()
        assert user.email == "test@example.com"
        assert user.name == "테스트"
```

## 📚 추가 문서

- [필수 규칙 가이드](rules/00-mandatory-rules.md) - 절대 준수해야 할 규칙들
- [통합 규칙 가이드](rules/10-rule-integration.md) - 모든 규칙의 통합 적용 방법
- [Result 패턴](rules/01-result-pattern.md) - 안전한 에러 처리
- [함수형 프로그래밍](rules/02-functional-programming.md) - 불변성과 순수 함수
- [헥사고날 아키텍처](rules/04-hexagonal-architecture.md) - 계층 구조
- [한글 주석 가이드](rules/09-korean-comments.md) - 명확한 문서화

## 🤝 기여하기

### 기여 절차
1. **가상환경 활성화 필수**: `source venv/bin/activate`
2. **RFS 규칙 숙지**: [필수 규칙](rules/00-mandatory-rules.md) 읽기
3. **규칙 검증 통과**: `python scripts/validate_rfs_rules.py --mode strict`
4. **테스트 작성 및 통과**: `pytest`
5. **Pre-commit 훅 통과**: `pre-commit run --all-files`

### 코드 리뷰 기준
- ✅ RFS Framework 패턴 사용
- ✅ Result 패턴으로 에러 처리
- ✅ 한글 주석 및 문서화
- ✅ 완전한 타입 힌트
- ✅ 불변성 유지
- ✅ 테스트 커버리지 80% 이상

## 📞 지원

- **이슈 보고**: GitHub Issues 사용
- **질문**: Discussions 섹션 활용
- **긴급 문제**: 팀 채널로 연락

---

> 💡 **중요**: 이 프로젝트는 RFS Framework 규칙을 엄격히 준수합니다. 
> 모든 기여자는 개발 전에 [필수 규칙](rules/00-mandatory-rules.md)을 반드시 숙지해주세요.
