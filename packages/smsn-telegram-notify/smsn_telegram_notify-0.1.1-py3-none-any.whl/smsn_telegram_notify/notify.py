"""Helper module for sending Telegram notifications."""

from __future__ import annotations

import os
import queue
import threading
import time
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter, Retry

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for Python<3.11
    import tomli as tomllib  # type: ignore

try:  # Optional dependency for image support
    import cv2
    HAS_CV2 = True
except ImportError:  # pragma: no cover - OpenCV not installed
    HAS_CV2 = False


class TelegramNotify:
    def __init__(self, token: str | None = None, chat_id: str | None = None, config_path: str | None = None):
        """Initialize Telegram notification sender.

        Parameters
        ----------
        token: str | None
            Bot token from Telegram.
        chat_id: str | None
            Destination chat ID.
        config_path: str | None
            Optional path to a TOML config file containing
            ``smsn_telegram_notify.token`` and ``smsn_telegram_notify.chat_id``.
        """

        if config_path:
            with open(config_path, "rb") as f:
                config = tomllib.load(f).get("smsn_telegram_notify", {})
            token = token or config.get("token")
            chat_id = chat_id or config.get("chat_id")
            self.TG_TIME_INTERVAL = config.get("notify_interval_sec", 5)
        else:
            self.TG_TIME_INTERVAL = 5  # 🕒 Global default interval (sec)

        self.TG_TOKEN = token
        self.CHAT_ID = chat_id

        self.last_send_time = {
            'text': 0,
            'image': 0,
            'file': 0,
            'frame': 0,
            'video': 0
        }

        self.send_queue = queue.Queue(maxsize=100)
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

        # ✅ Session + Retry
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _safe_telegram_post(self, url, data=None, files=None, timeout=30):
        try:
            response = self.session.post(url, data=data, files=files, timeout=timeout)
            if response.status_code == 200:
                result = response.json()
                if result.get("ok", False):
                    return True
                else:
                    print(f"❌ Telegram ตอบกลับผิดพลาด: {result}")
            else:
                print(f"❌ HTTP Error: {response.status_code} | {response.text}")
        except requests.exceptions.SSLError as e:
            print(f"❌ SSL Error: {e}")
        except Exception as e:
            print(f"❌ General Exception: {e}")
        return False

    def _process_queue(self) -> None:
        while True:
            try:
                func, args = self.send_queue.get()
                func(*args)
                self.send_queue.task_done()
            except Exception as e:  # pragma: no cover - logging only
                print(f"❌ Error in queue processor: {e}")

    def _should_send(self, key: str, time_interval: float | None = None) -> bool:
        now = time.time()
        interval = time_interval if time_interval is not None else self.TG_TIME_INTERVAL
        if now - self.last_send_time[key] >= interval:
            self.last_send_time[key] = now
            return True
        return False

    def _enqueue(self, func, *args) -> None:
        try:
            self.send_queue.put((func, args), timeout=1)
        except queue.Full:
            print(f"⚠️ Send queue is full. Skipping {func.__name__}.")

    def _encode_image(self, image) -> bytes | None:
        if not HAS_CV2:
            print("❌ OpenCV not installed. Cannot encode image.")
            return None
        try:
            ret, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 80])
        except Exception as e:  # pragma: no cover - encoding error
            print(f"❌ Image encoding failed: {e}")
            return None
        return buffer.tobytes() if ret else None

    def _send_file(self, endpoint: str, file_field: str, path_file: str, caption: str, mime: str = None) -> None:
        if not os.path.exists(path_file):
            print(f"❌ File not found: {path_file}")
            return
        filename = os.path.basename(path_file)
        url = f"https://api.telegram.org/bot{self.TG_TOKEN}/{endpoint}"
        with open(path_file, 'rb') as myfile:
            files = {file_field: (filename, myfile, mime)}
            data = {'chat_id': self.CHAT_ID, 'caption': caption}
            self._safe_telegram_post(url, files=files, data=data)

    # ========== Actual Send Methods ==========
    def tg_send_text(self, msg: str) -> None:
        url = f"https://api.telegram.org/bot{self.TG_TOKEN}/sendMessage"
        data = {'chat_id': self.CHAT_ID, 'text': msg}
        self._safe_telegram_post(url, data=data)

    def tg_send_image(self, msg: str, image) -> None:
        img_bytes = self._encode_image(image)
        if not img_bytes:
            return
        url = f"https://api.telegram.org/bot{self.TG_TOKEN}/sendPhoto"
        files = {'photo': ('image.jpg', img_bytes, 'image/jpeg')}
        data = {'chat_id': self.CHAT_ID, 'caption': msg}
        self._safe_telegram_post(url, files=files, data=data)

    def tg_byte_send_file(self, msg: str, bytes_data: bytes, filename: str | None = None) -> None:
        filename = filename or f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        url = f"https://api.telegram.org/bot{self.TG_TOKEN}/sendDocument"
        files = {'document': (filename, bytes_data, 'image/jpeg')}
        data = {'chat_id': self.CHAT_ID, 'caption': msg}
        self._safe_telegram_post(url, files=files, data=data)

    def tg_frame_send_file(self, msg: str, frame) -> None:
        img_bytes = self._encode_image(frame)
        if not img_bytes:
            return
        filename = f"frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        self.tg_byte_send_file(msg, img_bytes, filename)

    def tg_send_file(self, msg: str, path_file: str) -> None:
        self._send_file('sendDocument', 'document', path_file, msg)

    def tg_send_video(self, msg: str, path_file: str) -> None:
        self._send_file('sendVideo', 'video', path_file, msg)

    # ========== Public Send Methods ==========
    def start_send_text(self, msg: str, time_interval: float | None = None) -> None:
        if self._should_send('text', time_interval):
            self._enqueue(self.tg_send_text, msg)

    def start_send_image(self, msg: str, image, time_interval: float | None = None) -> None:
        if self._should_send('image', time_interval):
            self._enqueue(self.tg_send_image, msg, image)

    def start_bytes_send_file(self, msg: str, bytes_data: bytes, time_interval: float | None = None) -> None:
        if self._should_send('file', time_interval):
            self._enqueue(self.tg_byte_send_file, msg, bytes_data)

    def start_frame_send_file(self, msg: str, frame, time_interval: float | None = None) -> None:
        if self._should_send('frame', time_interval):
            self._enqueue(self.tg_frame_send_file, msg, frame)

    def start_send_file(self, msg: str, path_file: str, time_interval: float | None = None) -> None:
        if self._should_send('file', time_interval):
            self._enqueue(self.tg_send_file, msg, path_file)

    def start_send_video(self, msg: str, path_file: str, time_interval: float | None = None) -> None:
        if self._should_send('video', time_interval):
            self._enqueue(self.tg_send_video, msg, path_file)
