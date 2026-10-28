import random
import string
from typing import Dict, Any

import pytest
import requests

BASE_URL = "https://stellarburgers.education-services.ru/api"


@pytest.fixture(scope="session")
def base_url() -> str:
    """URL API для тестов (сессия)."""
    return BASE_URL


@pytest.fixture
def unique_user_data() -> Dict[str, str]:
    """Генерирует уникальные данные для регистрации нового пользователя."""
    random_part = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return {
        "email": f"test-{random_part}@example.com",
        "password": "12345678",
        "name": f"Test User {random_part}",
    }


@pytest.fixture
def registered_user(base_url: str) -> Dict[str, Any]:
    """
    Создаёт тестового пользователя, если его ещё нет.
    Возвращает данные пользователя.
    Автоматически удаляет пользователя после завершения тестов через финализатор.
    """
    data = {
        "email": "already-registered@example.com",
        "password": "12345678",
        "name": "Already Registered",
    }
  
    resp = requests.post(f"{base_url}/register", json=data)
    if resp.status_code not in (200, 201, 409):
        resp.raise_for_status()

    def finalizer():
        
        try:
            
        except Exception as e:
            pass

    pytest.cleanup(finalizer)

    return data


@pytest.fixture
def auth_token(base_url: str, registered_user: Dict[str, Any]) -> str:
    """Получает токен для зарегистрированного пользователя."""
    resp = requests.post(
        f"{base_url}/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    resp.raise_for_status()
    body = resp.json()
    return body.get("accessToken") or body.get("token")
