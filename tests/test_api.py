import allure
import pytest
import requests


@allure.feature("Registration")
class TestRegistration:
    @allure.title("Создание уникального пользователя")
    @allure.description("Регистрируем нового пользователя, ожидаем успешный ответ 201")
    def test_create_unique_user(self, base_url, unique_user_data):
        with allure.step("Отправляем POST-запрос на регистрацию нового пользователя"):
            resp = requests.post(f"{base_url}/register", json=unique_user_data)

        with allure.step("Проверяем статус-код ответа"):
            assert resp.status_code == 201

        with allure.step("Проверяем, что в ответе success == True"):
            body = resp.json()
            assert body.get("success") is True

    @allure.title("Попытка создания уже зарегистрированного пользователя")
    @allure.description("Повторная регистрация того же пользователя должна вернуть ошибку 409")
    def test_create_duplicate_user(self, base_url, registered_user):
        with allure.step("Пытаемся зарегистрировать уже существующего пользователя"):
            resp = requests.post(f"{base_url}/register", json=registered_user)

        with allure.step("Ожидаем статус 409 Conflict"):
            assert resp.status_code == 409

    @allure.title("Регистрация без обязательного поля (email)")
    @allure.description("Отправка запроса без email должна вернуть ошибку валидации 400")
    def test_register_missing_email(self, base_url, unique_user_data):
        data = unique_user_data.copy()
        del data["email"]

        with allure.step("Отправляем запрос на регистрацию без поля email"):
            resp = requests.post(f"{base_url}/register", json=data)

        with allure.step("Ожидаем статус 400 Bad Request"):
            assert resp.status_code == 400


@allure.feature("Authentication")
class TestAuthentication:
    @allure.title("Логин под существующим пользователем")
    @allure.description("Успешный логин должен вернуть токен доступа и статус 200")
    def test_login_existing_user(self, base_url, registered_user):
        payload = {
            "email": registered_user["email"],
            "password": registered_user["password"],
        }

        with allure.step("Выполняем логин существующего пользователя"):
            resp = requests.post(f"{base_url}/login", json=payload)

        with allure.step("Проверяем успешный статус 200"):
            assert resp.status_code == 200

        with allure.step("Получаем токен из ответа и проверяем его длину"):
            body = resp.json()
            auth_token = body.get("token")
            assert auth_token is not None
            assert len(auth_token) > 10

    @allure.title("Логин с неверным паролем")
    @allure.description("Попытка входа с неправильным паролем должна вернуть ошибку 401")
    def test_login_wrong_password(self, base_url, registered_user):
        payload = {
            "email": registered_user["email"],
            "password": "wrong-password-123",
        }

        with allure.step("Пытаемся залогиниться с неверным паролем"):
            resp = requests.post(f"{base_url}/login", json=payload)

        with allure.step("Ожидаем статус 401 Unauthorized"):
            assert resp.status_code == 401


@allure.feature("Orders")
class TestOrders:
    @allure.title("Создание заказа с авторизацией и ингредиентами")
    @allure.description("Авторизованный пользователь создаёт заказ с набором ингредиентов")
    def test_create_order_authorized_with_ingredients(self, base_url, registered_user):
        
        login_payload = {
            "email": registered_user["email"],
            "password": registered_user["password"],
        }
        resp_login = requests.post(f"{base_url}/login", json=login_payload)
        auth_token = resp_login.json().get("token")

        ingredients_hash = ["6c7f6e544a9856bc7f609e6199019a8058c9a690"]

        with allure.step("Создаём заказ с авторизацией и списком ингредиентов"):
            resp = requests.post(
                f"{base_url}/orders",
                headers={"authorization": f"Bearer {auth_token}"},
                json={"ingredients": ingredients_hash},
            )

        with allure.step("Ожидаем успешный статус 201"):
            assert resp.status_code == 201

        with allure.step("Проверяем, что success == True в теле ответа"):
            body = resp.json()
            assert body.get("success") is True

    @allure.title("Создание заказа без авторизации")
    @allure.description("Попытка создать заказ без токена должна вернуть ошибку доступа 401")
    def test_create_order_unauthorized(self, base_url):
        with allure.step("Пытаемся создать заказ без заголовка Authorization"):
            resp = requests.post(
                f"{base_url}/orders",
                json={"ingredients": []},
            )

        with allure.step("Ожидаем статус 401 Unauthorized"):
            assert resp.status_code == 401

    @allure.title("Создание заказа с пустым списком ингредиентов")
    @allure.description("Заказ можно создать даже с пустым списком ингредиентов")
    def test_create_order_empty_ingredients(self, base_url, registered_user):
        login_payload = {
            "email": registered_user["email"],
            "password": registered_user["password"],
        }
        resp_login = requests.post(f"{base_url}/login", json=login_payload)
        auth_token = resp_login.json().get("token")

        with allure.step("Создаём заказ с пустым списком ингредиентов"):
            resp = requests.post(
                f"{base_url}/orders",
                headers={"authorization": f"Bearer {auth_token}"},
                json={"ingredients": []},
            )

        with allure.step("Ожидаем успешный статус 201"):
            assert resp.status_code == 201

    @allure.title("Создание заказа с неверным хешем ингредиентов")
    @allure.description("Передача несуществующего хеша должна вызвать ошибку валидации 400")
    def test_create_order_invalid_ingredient_hash(self, base_url, registered_user):
        login_payload = {
            "email": registered_user["email"],
            "password": registered_user["password"],
        }
        resp_login = requests.post(f"{base_url}/login", json=login_payload)
        auth_token = resp_login.json().get("token")

        with allure.step("Создаём заказ с некорректным хешем ингредиента"):
            resp = requests.post(
                f"{base_url}/orders",
                headers={"authorization": f"Bearer {auth_token}"},
                json={"ingredients": ["invalid-hash-123"]},
            )

        with allure.step("Ожидаем статус 400 Bad Request"):
            assert resp.status_code == 400

