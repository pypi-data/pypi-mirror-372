"""FastAPI extensions and utilities."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db import db

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 의존성으로 사용할 데이터베이스 세션"""
    async with db.session() as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행될 코드"""
    # 데이터베이스 초기화
    await db.initialize()
    
    yield
    
    # 데이터베이스 연결 종료
    await db.close()

async def health_check() -> Response:
    """헬스 체크 엔드포인트"""
    try:
        async with db.session() as session:
            # 데이터베이스 연결 테스트
            await session.execute("SELECT 1")
        return Response(
            content="healthy",
            media_type="text/plain",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            content=f"unhealthy: {str(e)}",
            media_type="text/plain",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

def create_app(
    *,
    title: str = "EriPotter Service",
    description: str = "EriPotter Microservice",
    version: str = "0.1.0",
    lifespan_handler: Callable | None = None,
) -> FastAPI:
    """FastAPI 애플리케이션 생성"""
    app = FastAPI(
        title=title,
        description=description,
        version=version,
        lifespan=lifespan_handler or lifespan
    )
    
    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 헬스 체크 엔드포인트 추가
    app.get("/health")(health_check)
    
    return app