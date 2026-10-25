import allure
import pytest


@allure.title("Создание уникального пользователя")
@allure.description("Регистрируем нового пользователя, ожидаем успешный ответ 200/201")
def test_create_unique_user(base_url, unique_user_data):
    resp = requests.post(f"{base_url}/register", json=unique_user_data)
    assert resp.status_code in (200, 201)
    body = resp.json()
    assert body.get("success") is True


@allure.title("Попытка создания уже зарегистрированного пользователя")
@allure.description("Повторная регистрация того же пользователя должна вернуть ошибку")
def test_create_duplicate_user(base_url, registered_user):
    resp = requests.post(f"{base_url}/register", json=registered_user)
    assert resp.status_code in (403, 409)


@allure.title("Регистрация без обязательного поля (email)")
@allure.description("Отправка запроса без email должна вернуть ошибку валидации")
def test_register_missing_email(base_url, unique_user_data):
    data = unique_user_data.copy()
    del data["email"]
    resp = requests.post(f"{base_url}/register", json=data)
    assert resp.status_code == 400


@allure.title("Логин под существующим пользователем")
@allure.description("Успешный логин должен вернуть токен доступа")
def test_login_existing_user(registered_user, auth_token):
    assert auth_token is not None
    assert len(auth_token) > 10


@allure.title("Логин с неверным паролем")
@allure.description("Попытка входа с неправильным паролем должна вернуть ошибку 401/403")
def test_login_wrong_password(base_url, registered_user):
    resp = requests.post(
        f"{base_url}/login",
        json={
            "email": registered_user["email"],
            "password": "wrong-password-123"
        }
    )
    assert resp.status_code in (401, 403)


@allure.title("Создание заказа с авторизацией и ингредиентами")
@allure.description("Авторизованный пользователь создаёт заказ с набором ингредиентов")
def test_create_order_authorized_with_ingredients(base_url, auth_token):
    ingredients_hash = ["6c7f6e544a9856bc7f609e6199019a8058c9a690"]  # пример хеша из документации
    resp = requests.post(
        f"{base_url}/orders",
        headers={"authorization": f"Bearer {auth_token}"},
        json={"ingredients": ingredients_hash}
    )
    assert resp.status_code in (200, 201)
    assert resp.json().get("success") is True


@allure.title("Создание заказа без авторизации")
@allure.description("Попытка создать заказ без токена должна вернуть ошибку доступа")
def test_create_order_unauthorized(base_url):
    resp = requests.post(
        f"{base_url}/orders",
        json={"ingredients": []}
    )
    assert resp.status_code in (401, 403)


@allure.title("Создание заказа без ингредиентов")
@allure.description("Заказ можно создать даже с пустым списком ингредиентов")
def test_create_order_empty_ingredients(base_url, auth_token):
    resp = requests.post(
        f"{base_url}/orders",
        headers={"authorization": f"Bearer {auth_token}"},
        json={"ingredients": []}
    )
    assert resp.status_code in (200, 201)


@allure.title("Создание заказа с неверным хешем ингредиентов")
@allure.description("Передача несуществующего хеша должна вызвать ошибку валидации или 400")
def test_create_order_invalid_ingredient_hash(base_url, auth_token):
    resp = requests.post(
        f"{base_url}/orders",
        headers={"authorization": f"Bearer {auth_token}"},
        json={"ingredients": ["invalid-hash-123"]}
    )
    assert resp.status_code in (400, 500)
