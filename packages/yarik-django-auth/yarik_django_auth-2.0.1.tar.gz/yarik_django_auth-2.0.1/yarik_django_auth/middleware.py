import jwt
import urllib
import logging
import requests
import datetime
from asgiref.sync import iscoroutinefunction, markcoroutinefunction, sync_to_async


from django.http import (
    HttpRequest,
    JsonResponse,
)
from django.contrib.auth import logout
from django.shortcuts import render
from django.urls import reverse_lazy

from yarik_django_auth.conf.settings import (
    CLIENT_ID,
    CLIENT_SECRET,
    KEYCLOAK_CERT_FILENAME,
    KEYCLOAK_SCOPES,
    REALM_NAME,
    KEYCLOAK_URL_BASE,
    ERROR_PAGE_DOCUMENT,
)


logger = logging.getLogger(__name__)


def check_session(access_token):
    resp_status = 401
    try:
        userinfo_endpoint = (
            f"{KEYCLOAK_URL_BASE}realms/{REALM_NAME}/protocol/openid-connect/userinfo"
        )
        response = requests.get(
            userinfo_endpoint,
            headers={"Authorization": f"Bearer {access_token}"},
            verify=KEYCLOAK_CERT_FILENAME,
        )
        logger.debug("Выполнен запрос проверки актуальности сессии")
        resp_status = response.status_code
    except Exception as e:
        logger.debug(e)

    return resp_status


def update_token(refresh_token):
    resp_status = 401
    data = None
    try:
        token_endpoint = (
            f"{KEYCLOAK_URL_BASE}realms/{REALM_NAME}/protocol/openid-connect/token"
        )
        response = requests.post(
            token_endpoint,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            verify=KEYCLOAK_CERT_FILENAME,
            data=urllib.parse.urlencode(
                {
                    "client_id": CLIENT_ID,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "scope": " ".join(KEYCLOAK_SCOPES),
                    "client_secret": CLIENT_SECRET,
                },
                quote_via=urllib.parse.quote,
            ),
        )
        logger.debug("Выполнен запрос обновления токена")
        logger.debug(response.text)

        resp_status = response.status_code
        if resp_status == 200:
            data = response.json()
    except Exception as e:
        logger.debug(e)

    return (data, resp_status)


class AsyncMiddleware:
    async_capable = True
    sync_capable = False

    def __init__(self, get_response):
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    def get_403_response(self, request: HttpRequest):
        msg = "Ошибка при проверке актуальности сессии. Возможно токен не содержит scope openid."
        logger.error(msg)
        logout(request)
        return JsonResponse({"msg": msg}, status=403)

    async def __call__(self, request: HttpRequest):
        if "oidc_auth_token" in request.session:
            oidc_auth_token = request.session["oidc_auth_token"]
            access_token = oidc_auth_token.get("access_token")
            refresh_token = oidc_auth_token.get("refresh_token")
            logger.debug(f"Токен извлеченный из сессии = {oidc_auth_token}")
            logger.debug(f"Токен доступа = {access_token}")

            # 1. Проверяем актуальность токена
            logger.debug("Проверка актуальности токена доступа")
            decoded_token = jwt.decode(
                access_token, verify=False, options={"verify_signature": False}
            )
            if (
                datetime.datetime.fromtimestamp(decoded_token["exp"])
                < datetime.datetime.now()
            ):
                # Токен просрочен, надо обновить
                logger.debug("Токен устарел: обновление токена...")

                data_token, resp_status = update_token(refresh_token)

                logger.debug(f"Код ответа: {resp_status}")

                username = await sync_to_async(lambda request: request.user.username)(
                    request
                )

                if not data_token:
                    # Токен не получен, очистка сессии
                    logger.info(
                        f"Сессия очищена для пользователя {username}. Причина: не удалось обновить токен"
                    )
                    logout(request)
                    return await self.get_response(request)

                logger.debug("Сохранение токена в сессии...")
                request.session["oidc_auth_token"] = data_token

                access_token = data_token["access_token"]

            # 2. Проверяем актуальность сессии
            logger.debug("Выполнение запроса проверки актуальности сессии")

            resp_status = check_session(access_token)

            logger.debug(f"Код ответа: {resp_status}")

            if resp_status == 403:
                # В запросе не хватает данных
                return self.get_403_response(request)

            if resp_status != 200:
                # Сессия просрочена или refresh_token устарел, очистка сессии
                logger.info(
                    f"Сессия очищена для пользователя {request.user.username}. Причина: сессия в Keycloak была завершена"
                )
                logout(request)

        response = await self.get_response(request)

        return response


class SyncMiddleware:
    async_capable = False
    sync_capable = True

    def __init__(self, get_response):
        self.get_response = get_response

    def get_403_response(self, request: HttpRequest):
        logger.error(
            "Ошибка при проверке актуальности сессии. Возможно токен не содержит scope openid."
        )
        logout(request)
        return render(
            request,
            ERROR_PAGE_DOCUMENT,
            {
                "code": 403,
                "message": "Ошибка аутентификации в Keycloak, при проверке актуальности сессии произошла ошибка, обратитесь к администратору!",
                "header": "Ошибка аутентификации Keycloack",
                "button_text": "Вернуться к авторизации",
                "logout_url": reverse_lazy("yarik_django_auth:logout"),
            },
        )

    def __call__(self, request: HttpRequest):
        if "oidc_auth_token" in request.session:
            oidc_auth_token = request.session["oidc_auth_token"]
            access_token = oidc_auth_token.get("access_token")
            refresh_token = oidc_auth_token.get("refresh_token")
            logger.debug(f"Токен извлеченный из сессии = {oidc_auth_token}")
            logger.debug(f"Токен доступа = {access_token}")

            # 1. Проверяем актуальность токена
            logger.debug("Проверка актуальности токена доступа")
            decoded_token = jwt.decode(
                access_token, verify=False, options={"verify_signature": False}
            )
            if (
                datetime.datetime.fromtimestamp(decoded_token["exp"])
                < datetime.datetime.now()
            ):
                # Токен просрочен, надо обновить
                logger.debug("Токен устарел: обновление токена...")

                data_token, resp_status = update_token(refresh_token)

                logger.debug(f"Код ответа: {resp_status}")

                username = request.user.username

                if not data_token:
                    # Токен не получен, очистка сессии
                    logger.info(
                        f"Сессия очищена для пользователя {username}. Причина: не удалось обновить токен"
                    )
                    logout(request)
                    return self.get_response(request)

                logger.debug("Сохранение токена в сессии...")
                request.session["oidc_auth_token"] = data_token

                access_token = data_token["access_token"]

            # 2. Проверяем актуальность сессии
            logger.debug("Выполнение запроса проверки актуальности сессии")

            resp_status = check_session(access_token)

            logger.debug(f"Код ответа: {resp_status}")

            if resp_status == 403:
                # В запросе не хватает данных
                return self.get_403_response(request)

            if resp_status != 200:
                # Сессия просрочена или refresh_token устарел, очистка сессии
                logger.info(
                    f"Сессия очищена для пользователя {request.user.username}. Причина: сессия в Keycloak была завершена"
                )
                logout(request)

        response = self.get_response(request)

        return response
