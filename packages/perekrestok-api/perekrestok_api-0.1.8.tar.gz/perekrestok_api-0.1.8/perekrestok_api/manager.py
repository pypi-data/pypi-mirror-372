from __future__ import annotations

import json
import urllib.parse
from typing import Any

import hrequests
from requests import Request
from dataclasses import dataclass, field
import os

from .endpoints.advertising import ClassAdvertising
from .endpoints.catalog     import ClassCatalog
from .endpoints.general     import ClassGeneral
from .endpoints.geolocation import ClassGeolocation

# ---------------------------------------------------------------------------
# Константы
# ---------------------------------------------------------------------------
CATALOG_VERSION = "1.4.1.0"
MAIN_SITE_URL = "https://www.perekrestok.ru"
CATALOG_URL = f"{MAIN_SITE_URL}/api/customer/{CATALOG_VERSION}"
# ---------------------------------------------------------------------------
# Главный клиент
# ---------------------------------------------------------------------------
def _pick_https_proxy() -> str | None:
    """Возвращает прокси из HTTPS_PROXY/https_proxy (если заданы)."""
    return os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

@dataclass
class PerekrestokAPI:
    """Клиент Перекрёстка.

    Attributes
    ----------
    Geolocation : ClassGeolocation
        Клиент геолокации.
    Catalog : ClassCatalog
        Методы каталога.
    Advertising : ClassAdvertising
        Методы рекламы.
    General : ClassGeneral
        Общие методы (например, для формы обратной связи).
    """

    timeout: float          = 15.0
    browser: str            = "firefox"
    headless: bool          = True
    proxy: str | None       = field(default_factory=_pick_https_proxy)
    browser_opts: dict[str, Any] = field(default_factory=dict)

    # будет создана в __post_init__
    session: hrequests.Session = field(init=False, repr=False)

    # ───── lifecycle ─────
    def __post_init__(self) -> None:
        self.session = hrequests.Session(
            self.browser,
            timeout=self.timeout,
            proxy=self.proxy,         # ← автоподхват из env, если есть
        )
        self.access_token = self.access_token  # применит setter

        self.Geolocation = ClassGeolocation(self, CATALOG_URL)
        self.Catalog     = ClassCatalog(self, CATALOG_URL)
        self.Advertising = ClassAdvertising(self, CATALOG_URL)
        self.General     = ClassGeneral(self, CATALOG_URL)

    def __enter__(self):
        """Вход в контекстный менеджер с автоматическим прогревом сессии."""
        self._warmup()
        return self

    def __exit__(self, *exc):
        """Выход из контекстного менеджера с закрытием сессии."""
        self.close()

    def close(self):
        """Закрыть HTTP-сессию и освободить ресурсы."""
        self.session.close()

    # property setget access_token
    @property
    def access_token(self) -> str | None:
        """Токен доступа, который будет использоваться в запросах."""
        token = self.session.headers.get("Auth", None)
        if token:
            if not token.startswith("Bearer "):
                raise ValueError("Access token must start with 'Bearer '.")
            token = token.removeprefix("Bearer ")
        return token
    @access_token.setter
    def access_token(self, token: str | None) -> None:
        """Установить токен доступа для использования в запросах."""
        if token is not None and not isinstance(token, str):
            raise TypeError("Access token must be a string or None.")

        if token is None:
            self.session.headers.pop("Auth", None)
        else:
            self.session.headers.update({ # токен пойдёт в каждый запрос
                "Auth": f"Bearer {token}"
            })

    # Прогрев сессии (headless ➜ cookie `session` ➜ accessToken)
    def _warmup(self) -> None:
        """Прогрев сессии через браузер для получения токена доступа.
        
        Открывает главную страницу сайта в headless браузере, получает cookie сессии
        и извлекает из неё access token для последующих API запросов.
        """
        if self.access_token is None:
            with hrequests.BrowserSession(
                session=self.session,
                browser=self.browser,
                headless=self.headless,
                **self.browser_opts,
            ) as page:
                page.goto(MAIN_SITE_URL)
                page.awaitSelector("#app", timeout=self.timeout)

            if "session" not in self.session.cookies:
                raise RuntimeError("Cookie 'session' not found after warmup.")

            raw = urllib.parse.unquote(self.session.cookies["session"])
            clean = json.loads(raw.removeprefix("j:"))
            self.access_token = clean['accessToken']

    def _request(
        self,
        method: str,
        url: str,
        *,
        json_body: Any | None = None,
    ) -> hrequests.Response:
        """Выполнить HTTP-запрос через внутреннюю сессию.
        
        Единая точка входа для всех HTTP-запросов библиотеки.
        Добавляет к ответу объект Request для совместимости.
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE и т.д.)
            url: URL для запроса
            json_body: Тело запроса в формате JSON (опционально)
        """
        # Единая точка входа в чужую библиотеку для удобства
        resp = self.session.request(method.upper(), url, json=json_body, timeout=self.timeout)
        if hasattr(resp, "request"):
            raise RuntimeError(
                "Response object does have `request` attribute. "
                "This may indicate an update in `hrequests` library."
            )
        
        resp.request = Request(
            method=method.upper(),
            url=url,
            json=json_body,
        )
        return resp
