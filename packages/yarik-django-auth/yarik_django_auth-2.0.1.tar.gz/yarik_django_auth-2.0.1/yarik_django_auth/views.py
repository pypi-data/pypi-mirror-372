import jwt
import logging

from django.http import (
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
    HttpRequest,
    JsonResponse,
)
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.middleware.csrf import get_token

from yarik_django_auth.utils import clear_previos_sessions
from yarik_django_auth.conf.settings import (
    AUTH_PAGE_DOCUMENT,
    CACHE_CALLBACK,
    CLEAR_CACHE_CALLBACK,
    DEFAULT_REDIRECT_URI,
    KEYCLOAK_POST_LOGOUT_URL,
    USE_KEYCLOAK,
    REALM_NAME,
    CLIENT_ID,
    KEYCLOAK_URL_BASE_CLIENT,
    KEYCLOAK_SCOPES,
    KEYCLOAK_REDIRECT_URI,
    VERSION_TAG,
    ERROR_PAGE_DOCUMENT,
)
from .backends import KeycloakConfidentialBackend
from .forms import LoginForm

logger = logging.getLogger(__name__)


def index(request: HttpRequest):
    return redirect(reverse_lazy("yarik_django_auth:login"))


def login_view(
    request: HttpRequest,
) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    if USE_KEYCLOAK:
        if request.user and request.user.is_authenticated:
            return redirect(request.GET.get("next", DEFAULT_REDIRECT_URI))
        redirect_url = (
            f"{KEYCLOAK_URL_BASE_CLIENT}realms/{REALM_NAME}/protocol/openid-connect/auth"
            f"?client_id={CLIENT_ID}&response_type=code&scope={'%20'.join(KEYCLOAK_SCOPES)}&redirect_uri={KEYCLOAK_REDIRECT_URI}"
        )

        return redirect(redirect_url)
    else:
        msg = None
        if request.method == "POST":
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get("username")
                password = login_form.cleaned_data.get("password")
                user = authenticate(username=username, password=password)
                if user is not None:
                    if request.user:
                        logout(request)
                    login(request, user)

                    logger.info("Очистка устаревших сессий...")
                    clear_previos_sessions(request)

                    next = None
                    if CACHE_CALLBACK:
                        next = CACHE_CALLBACK(request)

                    logger.info(f"Пользователь {username} авторизован")
                    return redirect(
                        request.GET.get("next", next or DEFAULT_REDIRECT_URI)
                    )
                else:
                    logger.warning(
                        f"Пользователь {username} ввёл неверные учётные данные"
                    )
                    msg = "Неправильный логин или пароль"
            else:
                logger.info("Форма авторизации не прошла проверку")
                msg = "Некорректный ввод"
        else:
            user = request.user
            if user and user.is_authenticated:
                logger.info(f"Пользователь {user.get_username()} уже авторизован.")
                return redirect(request.GET.get("next", DEFAULT_REDIRECT_URI))

        form = LoginForm(request.POST or None)
        return render(
            request,
            AUTH_PAGE_DOCUMENT,
            context={
                "app_name": "authentication",
                "title": "Вход",
                "center": True,
                "msg": msg,
                "version": VERSION_TAG,
                "form": form,
            },
        )


def keycloak_callback(request: HttpRequest):
    logger.info("Обратный вызов из Keycloak")
    try:
        code = request.GET["code"]
    except Exception as e:
        return render(
            request,
            ERROR_PAGE_DOCUMENT,
            {
                "code": 500,
                "message": "Ошибка аутентификации в Keycloak, обратный вызов не вернул код, пожалуйста, обратитесь к администратору!",
                "header": "Ошибка аутентификации Keycloak",
                "button_text": "Вернуться к авторизации",
                "logout_url": reverse_lazy("yarik_django_auth:login"),
            },
        )
    logger.info("Авторизационный код получен")
    logger.debug(f"Код: {code}")

    backend = KeycloakConfidentialBackend()
    logger.info("Обмен кода на токен")
    data_token = backend.exchange_code_for_token(code)

    if not data_token:
        logger.warning("Ошибка: токен не получен")
        return render(
            request,
            ERROR_PAGE_DOCUMENT,
            {
                "code": 500,
                "message": "Ошибка аутентификации в Keycloak, не удалось получить токен, пожалуйста, обратитесь к администратору!",
                "header": "Ошибка аутентификации Keycloak",
                "button_text": "Вернуться к авторизации",
                "logout_url": reverse_lazy("yarik_django_auth:login"),
            },
        )

    logger.info("Токен получен")
    logger.info("Начало аутентификации")

    try:
        user = backend.authenticate(request, token=data_token)
    except jwt.exceptions.ImmatureSignatureError:
        logger.error(
            "Ошибка проверки подписи токена, токен предоставляет время в будущем, синхронизируйте системное время"
        )
        return render(
            request,
            ERROR_PAGE_DOCUMENT,
            {
                "code": 500,
                "message": "Токен не прошёл проверку, пожалуйста обратитесь к администратору!",
                "header": "Ошибка аутентификации в Keycloak",
                "button_text": "Выход",
                "logout_url": f"{KEYCLOAK_URL_BASE_CLIENT}realms/{REALM_NAME}/protocol/openid-connect/logout"
                f"?client_id={CLIENT_ID}&post_logout_redirect_uri={KEYCLOAK_POST_LOGOUT_URL}",
            },
        )
    except PermissionError as e:
        logger.error("У клиента нет доступа к интерфейсу")
        return render(
            request,
            ERROR_PAGE_DOCUMENT,
            {
                "code": 403,
                "message": "У данного пользователя нет доступа к интерфейсу, пожалуйста обратитесь к администратору!",
                "header": "Ошибка аутентификации в Keycloak",
                "button_text": "Выход",
                "logout_url": f"{KEYCLOAK_URL_BASE_CLIENT}realms/{REALM_NAME}/protocol/openid-connect/logout"
                f"?client_id={CLIENT_ID}&post_logout_redirect_uri={KEYCLOAK_POST_LOGOUT_URL}",
            },
        )
    except Exception as e:
        logger.error("Неизвестная ошибка при декодировании токена")
        logger.debug(e.args)
        return render(
            request,
            ERROR_PAGE_DOCUMENT,
            {
                "code": 520,
                "message": "Неизвестная ошибка, пожалуйста обратитесь к администратору!",
                "header": "Ошибка аутентификации в Keycloak",
                "button_text": "Выход",
                "logout_url": f"{KEYCLOAK_URL_BASE_CLIENT}realms/{REALM_NAME}/protocol/openid-connect/logout"
                f"?client_id={CLIENT_ID}&post_logout_redirect_uri={KEYCLOAK_POST_LOGOUT_URL}",
            },
        )

    if user is not None:
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        logger.info("Очистка устаревших сессий...")
        clear_previos_sessions(request)
        next = None
        if CACHE_CALLBACK:
            next = CACHE_CALLBACK(request)

        logger.info(f"Пользователь {user.username} авторизован.")
        request.session["oidc_auth_token"] = data_token
        return redirect(request.GET.get("next", next or DEFAULT_REDIRECT_URI))
    else:
        return render(
            request,
            ERROR_PAGE_DOCUMENT,
            {
                "code": 404,
                "message": "Аутентификация в Keycloak прошла, однако данного пользователя не существует в системе, пожалуйста обратитесь к администратору!",
                "header": "Ошибка авторизации",
                "button_text": "Выход",
                "logout_url": f"{KEYCLOAK_URL_BASE_CLIENT}realms/{REALM_NAME}/protocol/openid-connect/logout"
                f"?client_id={CLIENT_ID}&post_logout_redirect_uri={KEYCLOAK_POST_LOGOUT_URL}",
            },
        )


@login_required(login_url=reverse_lazy("yarik_django_auth:login"))
def logout_view(request: HttpRequest) -> HttpResponseRedirect:
    user = request.user
    if CLEAR_CACHE_CALLBACK:
        CLEAR_CACHE_CALLBACK(user)
    logout(request)
    logger.info(f"Пользователь {user.get_username()} вышел из системы")
    if USE_KEYCLOAK:
        redirect_url = (
            f"{KEYCLOAK_URL_BASE_CLIENT}realms/{REALM_NAME}/protocol/openid-connect/logout"
            f"?client_id={CLIENT_ID}&post_logout_redirect_uri={KEYCLOAK_POST_LOGOUT_URL}"
        )

        return redirect(redirect_url)
    else:
        return redirect(reverse_lazy("yarik_django_auth:login"))


@login_required(login_url=reverse_lazy("yarik_django_auth:login"))
def get_new_csrftoken(request: HttpRequest):
    token = get_token(request)
    return JsonResponse({"token": token})
