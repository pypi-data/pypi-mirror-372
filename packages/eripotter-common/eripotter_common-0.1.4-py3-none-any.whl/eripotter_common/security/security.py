"""Security utility functions."""

from datetime import datetime, timedelta
from typing import Optional, Any
import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """비밀번호 해시화
    
    Args:
        password: 해시화할 비밀번호
    
    Returns:
        해시화된 비밀번호
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증
    
    Args:
        plain_password: 검증할 비밀번호
        hashed_password: 해시화된 비밀번호
    
    Returns:
        비밀번호 일치 여부
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(
    data: dict[str, Any],
    secret_key: str,
    expires_delta: Optional[timedelta] = None,
    algorithm: str = "HS256",
) -> str:
    """JWT 액세스 토큰 생성
    
    Args:
        data: 토큰에 포함될 데이터
        secret_key: 서명에 사용할 비밀키
        expires_delta: 토큰 만료 시간
        algorithm: 서명 알고리즘
    
    Returns:
        JWT 토큰
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)

def verify_access_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256",
) -> dict[str, Any]:
    """JWT 액세스 토큰 검증
    
    Args:
        token: 검증할 토큰
        secret_key: 서명 검증에 사용할 비밀키
        algorithm: 서명 알고리즘
    
    Returns:
        디코딩된 토큰 데이터
    
    Raises:
        jwt.InvalidTokenError: 토큰이 유효하지 않은 경우
    """
    return jwt.decode(token, secret_key, algorithms=[algorithm])