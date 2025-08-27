# connections.py

import logging
import socket
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class KKTConnection(ABC):
    """Абстрактный базовый класс для синхронных соединений с ККТ."""

    @abstractmethod
    def connect(self):
        """Устанавливает соединение."""
        pass

    @abstractmethod
    def disconnect(self):
        """Закрывает соединение."""
        pass

    @abstractmethod
    def send(self, data: bytes):
        """Отправляет данные."""
        pass

    @abstractmethod
    def read(self, num_bytes: int) -> bytes:
        """Читает указанное количество байт."""
        pass


class TCPConnection(KKTConnection):
    """Класс для управления синхронным TCP-соединением с ККТ."""

    def __init__(self, host: str, port: int, timeout: float = 5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket = None

    def connect(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.host, self.port))
            logger.info(f"TCP-соединение установлено с {self.host}:{self.port}")
        except socket.error as e:
            logger.error(f"Ошибка TCP-соединения: {e}")
            self._socket = None
            raise ConnectionError(f"Не удалось установить TCP-соединение: {e}")

    def disconnect(self):
        try:
            self._socket.close()
        except socket.error as e:
            logger.error(f"Ошибка при закрытии TCP-соединения: {e}")
        finally:
            self._socket = None
            logger.debug("TCP-соединение закрыто.")

    def send(self, data: bytes):
        self._socket.send(data)

    def read(self, num_bytes: int) -> bytes:
        return self._socket.recv(num_bytes)
