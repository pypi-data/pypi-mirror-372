"""Test security module."""

from datetime import timedelta
import jwt
import pytest

from eripotter_common.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)

def test_password_hash():
    """Test password hashing and verification."""
    password = "testpassword"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_access_token():
    """Test JWT token creation and verification."""
    secret_key = "testsecret"
    data = {"sub": "testuser"}
    
    token = create_access_token(
        data=data,
        secret_key=secret_key,
        expires_delta=timedelta(minutes=30)
    )
    
    decoded = verify_access_token(token, secret_key)
    assert decoded["sub"] == data["sub"]

def test_access_token_expiration():
    """Test JWT token expiration."""
    secret_key = "testsecret"
    data = {"sub": "testuser"}
    
    token = create_access_token(
        data=data,
        secret_key=secret_key,
        expires_delta=timedelta(minutes=-1)  # Expired token
    )
    
    with pytest.raises(jwt.ExpiredSignatureError):
        verify_access_token(token, secret_key)

def test_invalid_token():
    """Test invalid JWT token."""
    secret_key = "testsecret"
    wrong_key = "wrongsecret"
    data = {"sub": "testuser"}
    
    token = create_access_token(data=data, secret_key=secret_key)
    
    with pytest.raises(jwt.InvalidTokenError):
        verify_access_token(token, wrong_key)