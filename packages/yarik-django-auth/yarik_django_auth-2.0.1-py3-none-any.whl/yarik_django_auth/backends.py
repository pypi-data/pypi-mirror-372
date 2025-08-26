import jwt
import urllib
import datetime
import requests
from typing import Optional
from base64 import b64decode
from django.contrib.auth.models import User
from cryptography.hazmat.primitives import serialization

from yarik_django_auth.conf.settings import (
    REALM_NAME,
    CLIENT_ID,
    KEYCLOAK_URL_BASE,
    CLIENT_SECRET,
    KEYCLOAK_AUDIENCE,
    KEYCLOAK_IS_CREATE,
    KEYCLOAK_SCOPES,
    KEYCLOAK_REDIRECT_URI,
    KEYCLOAK_CERT_FILENAME,
)

import logging

logger = logging.getLogger(__name__)


class KeycloakConfidentialBackend:
    @staticmethod
    def exchange_code_for_token(code: str) -> Optional[dict]:
        """Возвращает токен пользователя."""
        token_endpoint = (
            f"{KEYCLOAK_URL_BASE}realms/{REALM_NAME}/protocol/openid-connect/token"
        )

        payload = {
            "code": code,
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": KEYCLOAK_REDIRECT_URI,
            "scope": " ".join(KEYCLOAK_SCOPES),
        }

        response = requests.post(
            token_endpoint,
            data=urllib.parse.urlencode(payload, quote_via=urllib.parse.quote),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            verify=KEYCLOAK_CERT_FILENAME,
        )

        if response.status_code == 200:
            logger.debug(f"Ответ токеном: {response.json()}")
            return response.json()
        logger.info(f"Токен не получен: {response}")
        return None

    @property
    def public_key(self):
        """Возвращает публичный ключ из Keycloak."""
        r = requests.get(
            f"{KEYCLOAK_URL_BASE}realms/{REALM_NAME}/",
            verify=KEYCLOAK_CERT_FILENAME,
        )
        r.raise_for_status()
        key_der_base64 = r.json()["public_key"]
        key_der = b64decode(key_der_base64.encode())
        return serialization.load_der_public_key(key_der)

    def decode_token(self, data: dict) -> dict:
        """Возвращает декодированные данные из токена."""
        access_token = data["access_token"]

        logger.debug(f"Текущее время: {datetime.datetime.now()}")
        logger.debug(f"Публичный ключ: {self.public_key.public_numbers()}")

        decoded_token = jwt.decode(
            access_token,
            key=self.public_key,
            algorithms=["RS256"],
            audience=KEYCLOAK_AUDIENCE,
        )
        return decoded_token

    def authenticate(self, request, token: dict, **kwargs):
        logger.info(f"Токен: {token}")
        logger.info("Декодирование токена доступа")
        user_info = self.decode_token(token)
        logger.debug(f"Декодированный токен: {user_info}")
        logger.info("Токен успешно декодирован")
        logger.info("Проверка роли")
        if (
            CLIENT_ID not in user_info["resource_access"]
            or "access" not in user_info["resource_access"][CLIENT_ID]["roles"]
        ):
            logger.debug("Не назначена роль access")
            raise PermissionError("Не назначена роль access")
        logger.info("Роль успешно проверена, доступ получен")

        logger.info("Поиск пользователя в БД")
        user = self.get_user(user_info=user_info)

        if not user:
            logger.info("Пользователь не найден")

        return user

    def get_user(self, user_info: dict) -> Optional[User]:
        logger.debug(f"Метаданные пользователя Keycloak: {user_info}")
        user = User.objects.filter(
            username=user_info.get("preferred_username", "")
        ).first()
        user_roles = (
            user_info.get("resource_access", {}).get(CLIENT_ID, {}).get("roles", [])
        )
        if KEYCLOAK_IS_CREATE:
            if not user:
                # Создание пользователя
                logger.info(
                    "Данный пользователь не зарегистрирован в локальной БД: создание пользователя"
                )
                user = User.objects.create_user(
                    username=user_info.get("preferred_username"),
                    email=user_info.get("email"),
                    last_name=user_info.get("given_name"),
                    first_name=user_info.get("family_name"),
                    is_superuser="superuser" in user_roles,
                    is_staff="staff" in user_roles,
                )

                # Установка пустого пароля
                user.set_unusable_password()

                # Сохранение пользователя
                user.save()
            else:
                logger.info(
                    "Данный пользователь уже зарегистрирован в локальной БД: обновление информации"
                )
                user.email = user_info.get("email")
                user.last_name = user_info.get("given_name")
                user.first_name = user_info.get("family_name")
                user.is_superuser = "superuser" in user_roles
                user.is_staff = "staff" in user_roles
                user.save()
        return user
