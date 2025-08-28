# shadowstep/logging/shadowstep_logcat.py
from __future__ import annotations

import contextlib
import logging
import threading
import time
from collections.abc import Callable

from appium.webdriver.webdriver import WebDriver
from selenium.common import WebDriverException
from websocket import WebSocket, WebSocketConnectionClosedException, create_connection

logger = logging.getLogger(__name__)


class ShadowstepLogcat:

    def __init__(
            self,
            driver_getter: Callable[[], 'WebDriver'],  # функция, возвращающая актуальный driver
            poll_interval: float = 1.0
    ):
        self._driver_getter = driver_getter
        self._poll_interval = poll_interval

        self._thread: threading.Thread | None = None
        self._stop_evt = threading.Event()
        self._filename: str | None = None
        self._ws: WebSocket | None = None  # <-- храним текущее соединение

    def __del__(self):
        self.stop()

    def start(self, filename: str) -> None:
        if self._thread and self._thread.is_alive():
            logger.info("Logcat already running")
            return

        self._stop_evt.clear()
        self._filename = filename
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="ShadowstepLogcat"
        )
        self._thread.start()
        logger.info(f"Started logcat to '{filename}'")

    def stop(self) -> None:
        # 1) даём флаг потоку, чтобы он корректно вышел из цикла
        self._stop_evt.set()

        # 2) закрываем WebSocket, чтобы прервать blocking recv()
        if self._ws:
            with contextlib.suppress(Exception):
                self._ws.close()

        # 3) отправляем команду остановить broadcast
        try:
            driver = self._driver_getter()
            driver.execute_script("mobile: stopLogsBroadcast")
        except WebDriverException as e:
            logger.warning(f"Failed to stop broadcast: {e!r}")

        # 4) ждём, пока фоновый поток действительно завершится и файл закроется
        if self._thread:
            self._thread.join()
            self._thread = None
            self._filename = None

        logger.info("Logcat thread terminated, file closed")

    def _run(self):  # noqa: C901
        if not self._filename:
            logger.error("No filename specified for logcat")
            return

        try:
            f = open(self._filename, "a", buffering=1, encoding="utf-8")
        except Exception as e:
            logger.error(f"Cannot open logcat file '{self._filename}': {e!r}")
            return

        try:
            while not self._stop_evt.is_set():
                try:
                    # 1) Запускаем broadcast
                    driver = self._driver_getter()
                    driver.execute_script("mobile: startLogsBroadcast")

                    # 2) Формируем базовый ws:// URL
                    session_id = driver.session_id
                    
                    http_url = self._get_http_url(driver)
                    scheme, rest = http_url.split("://", 1)
                    ws_scheme = "ws" if scheme == "http" else "wss"
                    base_ws = f"{ws_scheme}://{rest}".rstrip("/wd/hub")

                    # 3) Пробуем оба эндпоинта
                    endpoints = [
                        f"{base_ws}/ws/session/{session_id}/appium/logcat",
                        f"{base_ws}/ws/session/{session_id}/appium/device/logcat",
                    ]
                    ws = None
                    for url in endpoints:
                        try:
                            ws = create_connection(url, timeout=5)
                            logger.info(f"Logcat WebSocket connected: {url}")
                            break
                        except Exception as ex:
                            logger.debug(f"Cannot connect to {url}: {ex!r}")
                    if not ws:
                        raise RuntimeError("Cannot connect to any logcat WS endpoint")

                    # сохраним ws, чтобы stop() мог его закрыть
                    self._ws = ws

                    # 4) Читаем до stop_evt
                    while not self._stop_evt.is_set():
                        try:
                            line = ws.recv()
                            if isinstance(line, bytes):
                                line = line.decode(errors="ignore", encoding='utf-8')
                            f.write(line + "\n")
                        except WebSocketConnectionClosedException:
                            break  # переподключимся
                        except Exception as ex:
                            logger.debug(f"Ignoring recv error: {ex!r}")
                            continue

                    # очистить ссылку и закрыть сокет
                    try:
                        ws.close()
                    except Exception:
                        pass
                    finally:
                        self._ws = None

                    # пауза перед переподключением
                    time.sleep(self._poll_interval)

                except Exception as inner:
                    logger.error(f"Logcat stream error, retry in {self._poll_interval}s: {inner!r}", exc_info=True)
                    time.sleep(self._poll_interval)

        finally:
            with contextlib.suppress(Exception):
                f.close()
            logger.info("Logcat thread terminated, file closed")

    def _get_http_url(self, driver: WebDriver) -> str:
        http_url = getattr(driver.command_executor, "_url", None)
        if not http_url:
            http_url = getattr(driver.command_executor, "_client_config", None)
            if http_url:
                http_url = getattr(driver.command_executor._client_config, "remote_server_addr", "")
            else:
                http_url = ""
        return http_url
