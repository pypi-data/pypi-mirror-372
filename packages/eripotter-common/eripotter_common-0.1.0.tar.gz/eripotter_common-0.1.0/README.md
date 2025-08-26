# EriPotter Common

EriPotter 마이크로서비스를 위한 공통 유틸리티 패키지입니다.

## 기능

- 환경변수 기반 설정 관리
- 비동기 데이터베이스 연결 및 세션 관리
- FastAPI 확장 기능 (CORS, 헬스 체크 등)
- 보안 유틸리티 (비밀번호 해시화)
- 구조화된 로깅

## 설치

```bash
pip install eripotter-common
```

## 마이그레이션 가이드

기존 `common/` 폴더에서 PyPI 패키지로 마이그레이션하는 방법:

1. 기존 `common/` 폴더 제거
```bash
rm -rf common/  # Linux/Mac
rd /s /q common  # Windows
```

2. PyPI 패키지 설치
```bash
pip install eripotter-common
```

3. import 문 수정
```python
# 이전
from common.config import settings
from common.db import get_db_engine
from common.security import hash_password

# 이후
from app import settings, db, hash_password

# 데이터베이스 사용
engine = await db.initialize()
async with db.session() as session:
    # 데이터베이스 작업
    pass
```

## 사용 예시

### FastAPI 애플리케이션 생성

```python
from app import create_app, settings, setup_logging, get_session, db, Base

# 로깅 설정
setup_logging()

# FastAPI 앱 생성
app = create_app(
    title="My Service",
    description="My Microservice"
)

# 모델 정의
class User(Base):
    __tablename__ = "users"
    # ... 모델 정의

# 라우터
@app.get("/users")
async def get_users(session = Depends(get_session)):
    users = await session.query(User).all()
    return users
```

### 환경변수 설정 (.env)

```env
# 필수 설정
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
SERVICE_NAME=my-service

# 선택적 설정
SQL_ECHO=true
LOG_LEVEL=INFO
JSON_LOGS=true
PORT=8000
```

## 개발 환경 설정

1. 저장소 클론
```bash
git clone https://github.com/eripotter/eripotter-common.git
cd eripotter-common
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 개발 의존성 설치
```bash
pip install -e ".[test]"
```

4. 테스트 실행
```bash
pytest
```

## 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.