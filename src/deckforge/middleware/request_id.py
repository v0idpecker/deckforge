import logging
import time
import uuid

from starlette.types import ASGIApp, Receive, Scope, Send

from deckforge.logging_setup import set_request_id

logger = logging.getLogger(__name__)

class RequestIdMiddleware:
    """Генерирует/принимает X-Request-ID, кладёт в contextvars и в ответ.

    Должен быть добавлен последним в app.add_middleware — тогда он
    срабатывает первым и request_id доступен всем нижестоящим слоям.
    """

    def __init__(self, app: ASGIApp):
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        incoming = headers.get(b"x-request-id", b"").decode()
        request_id = incoming or uuid.uuid4().hex
        set_request_id(request_id)

        start = time.perf_counter()
        status: int | None = None

        async def send_wrapper(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                response_headers = list(message.get("headers", []))
                response_headers.append((b"x-request-id", request_id.encode()))
                message["headers"] = response_headers
            await send(message)

        try:
            await self._app(scope, receive, send_wrapper)
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "%s %s -> %s (%.1f ms)",
                scope.get("method", "-"),
                scope.get("path", "-"),
                status,
                elapsed_ms,
            )
