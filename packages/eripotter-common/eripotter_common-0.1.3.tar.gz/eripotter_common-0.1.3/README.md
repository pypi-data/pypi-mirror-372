# EriPotter Common

Common utilities for EriPotter microservices.

## Features

- Database management with SQLAlchemy
  - Railway PostgreSQL support
  - Sync/Async database support
  - Session management
  - Connection pooling
- Security utilities
  - Password hashing with bcrypt
  - JWT token management
- Environment variables and API keys
  - Centralized configuration
  - API key management

## Installation

```bash
pip install eripotter-common
```

## Usage

### Database

```python
from eripotter_common.database import get_db_engine, get_session
from eripotter_common.www import DATABASE_URL

# Use default engine (configured in www.env)
with get_session() as session:
    result = session.query(YourModel).all()

# Or create custom engine
engine = get_db_engine("your-database-url")

# Async support
from eripotter_common.database import get_async_db_engine, get_async_session

async with get_async_session() as session:
    result = await session.query(YourModel).all()
```

### Security

```python
from eripotter_common.security import hash_password, verify_password

# Hash password
hashed = hash_password("mypassword")

# Verify password
is_valid = verify_password("mypassword", hashed)

# JWT tokens
from eripotter_common.security import create_access_token

token = create_access_token(
    data={"sub": "user@example.com"},
    secret_key="your-secret-key"
)
```

### Environment Variables & API Keys

```python
from eripotter_common.www import (
    OPENAI_API_KEY,
    DATABASE_URL,
    ASYNC_DATABASE_URL,
)

# Use API keys
openai.api_key = OPENAI_API_KEY

# Use database URLs
engine = get_db_engine(DATABASE_URL)
```

## Development

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[test]"
   ```
3. Run tests:
   ```bash
   pytest
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.