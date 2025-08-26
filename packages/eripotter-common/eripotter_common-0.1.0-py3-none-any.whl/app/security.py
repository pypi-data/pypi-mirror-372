"""
보안 관련 유틸리티 함수들
"""
import logging
from passlib.hash import bcrypt

logger = logging.getLogger("security")

async def hash_password(plain_password: str) -> str:
    """비밀번호 해시화"""
    # CPU-bound 작업이므로 ThreadPoolExecutor에서 실행
    return bcrypt.hash(plain_password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    # CPU-bound 작업이므로 ThreadPoolExecutor에서 실행
    return bcrypt.verify(plain_password, hashed_password)