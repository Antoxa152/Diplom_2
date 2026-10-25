import pytest
import requests
from typing import Dict, Any

BASE_URL = "https://stellarburgers.education-services.ru/api"  

@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL

@pytest.fixture
def unique_user_data() -> Dict[str, str]:
    
    import random, string
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return {
        "email": f"test-{random_part}@example.com",
        "password": "12345678",
        "name": f"Test User {random_part}"
    }

@pytest.fixture
def registered_user(base_url: str) -> Dict[str, Any]:
    """Создаёт пользователя специально для тестов, чтобы потом логиниться под ним."""
    data = {
        "email": "already-registered@example.com",  # можно сделать уникальным, но оставить фиксированным для сессии
        "password": "12345678",
        "name": "Already Registered"
    }
   
    try:
        resp = requests.post(f"{base_url}/register", json=data)
       
        if resp.status_code not in (200, 403, 409):
            resp.raise_for_status()
    except Exception:
        pass  
    return data

@pytest.fixture
def auth_token(base_url: str, registered_user: Dict[str, Any]) -> str:
    resp = requests.post(
        f"{base_url}/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
    )
    resp.raise_for_status()
    return resp.json()["accessToken"]
