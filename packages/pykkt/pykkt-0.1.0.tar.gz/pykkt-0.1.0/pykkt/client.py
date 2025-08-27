import logging
import time
from typing import Union

from .connections import KKTConnection
from .constants import \
    ACK, STX, NAK, ENQ, KKTCommand
from .utils import build_message, compute_lrc

logger = logging.getLogger(__name__)


class KKTClient:
    """
    Основной класс клиента для работы с ККТ по протоколу v.A.2.0.
    """

    def __init__(self,
                 password: Union[int, bytes] = b"",
                 connection: KKTConnection = None
                 ):
        self.connection = connection

        if isinstance(password, int):
            self.password = password.to_bytes(4, 'little')
        elif isinstance(password, bytes) and len(self.password) == 4:
            self.password = password
        else:
            raise ValueError("Password must be int or 4 bytes")

    def send_enq(self):
        """
        Send ENQ and wait for response (ACK/NAK).
        Returns: 'ready' if NAK, 'preparing' if ACK, 'no_response' if timeout.
        """
        self.connection.send(ENQ)
        try:
            time.sleep(0.06)
            response = self.connection.read(1)
            if response == NAK:
                return 'ready'
            elif response == ACK:
                return 'preparing'
        except TimeoutError:
            return 'no_response'

    def send_command(self, command_code: int, params: Union[list[int], bytes] = b''):
        """
        Отправляет команду, обрабатывает подтверждения (ACK/NAK) и возвращает ответ.
        """
        # print(build_message(command_code, params))
        # return
        self.connection.connect()
        print(self.send_enq())
        # self.connection.send(bytes([ENQ]))
        # print(self.connection.read(1))
        try:
            packet = build_message(command_code, params)
            # packet = b'\x02\x05\x10\x1E\x00\x00\x00\x0B'
            print(f"-> Отправка: {packet.hex(' ').upper()}")
            for byte in packet:
                self.connection.send(byte.to_bytes(1))
                # time.sleep(0.15)
                # confirmation = self.connection.read(1)
                # print(confirmation)

            # time.sleep(0.1)
            # Ожидаем подтверждение ACK от ККТ
            confirmation = self.connection.read(1)[0].to_bytes()
            if confirmation != ACK:
                raise IOError(f"Не получено подтверждение ACK. Получено: {confirmation}")
            print("<- Получен ACK на команду.")

            # Читаем ответ от ККТ
            stx = self.connection.read(1)[0].to_bytes()
            if stx != STX:
                raise IOError(f"Неверный стартовый байт ответа. Получено: {stx.hex() if stx else 'пусто'}")

            length_byte = self.connection.read(1)
            if not length_byte:
                raise IOError("Не удалось прочитать байт длины ответа.")

            response_body = self.connection.read(length_byte[0])

            # Проверяем контрольную сумму ответа
            if (not (lrc_byte := self.connection.read(1))
                    or lrc_byte[0] != compute_lrc(list(length_byte + response_body))):
                # В случае ошибки нужно отправить NAK
                self.connection.send(NAK)
                raise ValueError("Контрольная сумма ответа не совпадает.")

            # 4. Отправляем ACK в подтверждение корректного приема ответа
            self.connection.send(ACK)

            print("-> Отправлен ACK на ответ.")
            print(f"<- Получен ответ: {response_body.hex(' ').upper()}")
            return response_body

        finally:
            self.connection.disconnect()

    def send_print_bold_string(self, flags, text, fixed_length=False):
        """
        Send the print bold string command (0x12).
        - password: int (will be converted to 4 little-endian bytes) or bytes (must be 4 bytes)
        - flags: int (0-255)
        - text: str, the text to print, encoded in cp1251
        - fixed_length: bool, if True, pad string to 20 bytes with \0
        Returns: True if ACK received for the message.
        """
        if not 0 <= flags <= 255:
            raise ValueError("Flags must be 0-255")
        flags_byte = bytes([flags])

        try:
            string_bytes = text.encode('cp1251')
        except UnicodeEncodeError:
            raise ValueError("Text must be encodable in WIN1251 (cp1251)")

        if fixed_length:
            if len(string_bytes) > 20:
                string_bytes = string_bytes[:20]
            string_bytes += b'\0' * (20 - len(string_bytes))
        return self.send_with_password_command(0x12, flags_byte + string_bytes)

    def send_with_password_command(self, cmd: int, params: Union[list[int], bytes] = b''):
        return self.send_command(cmd, self.password + params)

    def send_cut_receipt(self, cut_type: int):
        """
        Send the cut receipt command (0x25).
        - password: int (will be converted to 4 little-endian bytes) or bytes (must be 4 bytes)
        - cut_type: int (0 for full cut, 1 for partial cut)
        Returns: True if ACK received for the message.
        """
        if cut_type not in (0, 1):
            raise ValueError("Cut type must be 0 (full) or 1 (partial)")
        return self.send_with_password_command(KKTCommand.CUT_RECEIPT, bytes([cut_type]))

    def open_receipt(self, type: int = 0):
        """
        Тип документа (1 байт):
        «0» – продажа
        «1» – покупка
        «2» – возврат продажи
        «3» – возврат покупки
        """
        return self.send_with_password_command(KKTCommand.OPEN_RECEIPT, type.to_bytes(1, 'little'))

    def add_position(self, op_type, quantity, price, amount, tax, tax_rate, department, payment_method,
                     item_type, item_name):
        """
        Send the Operation V2 command (FF46h).
        - op_type: int (1-4: 1=Sale, 2=Sale Refund, 3=Purchase, 4=Purchase Refund)
        - quantity: float or int (6 bytes, 6 decimal places)
        - price: int (5 bytes, in kopecks)
        - amount: int (5 bytes, in kopecks, or 0xFFFFFFFFFF to calculate)
        - tax: int (5 bytes, in kopecks, or 0xFFFFFFFFFF if not specified)
        - tax_rate: int (e.g., 0x01 for 20% VAT, see protocol)
        - department: int (0-16, 0 for no department)
        - payment_method: int (1 byte, as per protocol)
        - item_type: int (1 byte, as per protocol)
        - item_name: str (0-128 bytes, WIN1251 encoded)
        Returns: True if ACK received for the message.
        """
        if op_type not in (1, 2, 3, 4):
            raise ValueError("Operation type must be 1-4")
        op_type_byte = bytes([op_type])

        # Quantity: convert to 6 bytes (6 decimal places, e.g., 123.456789 -> 123456789)
        quantity_int = int(round(quantity * 1000000))
        quantity_bytes = quantity_int.to_bytes(6, 'little', signed=False)

        # Price: 5 bytes, in kopecks
        if not 0 <= price <= 0xFFFFFFFFFF:
            raise ValueError("Price must be 0 to 2^40-1")
        price_bytes = price.to_bytes(5, 'little')

        # Amount: 5 bytes, in kopecks or 0xFFFFFFFFFF
        if not 0 <= amount <= 0xFFFFFFFFFF:
            raise ValueError("Amount must be 0 to 2^40-1")
        amount_bytes = amount.to_bytes(5, 'little')

        # Tax: 5 bytes, in kopecks or 0xFFFFFFFFFF
        if not 0 <= tax <= 0xFFFFFFFFFF:
            raise ValueError("Tax must be 0 to 2^40-1")
        tax_bytes = tax.to_bytes(5, 'little')

        # Tax rate: as per protocol
        valid_tax_rates = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x81, 0x82, 0x84, 0x88}
        if tax_rate not in valid_tax_rates:
            tax_rate = 0x08  # Default to "No VAT" (6)
        tax_rate_byte = bytes([tax_rate])

        # Department: 0-16
        if not 0 <= department <= 16:
            raise ValueError("Department must be 0-16")
        department_byte = bytes([department])

        # Payment method and item type: 1 byte each
        payment_method_byte = bytes([payment_method])
        item_type_byte = bytes([item_type])

        # Item name: 0-128 bytes, WIN1251
        try:
            item_name_bytes = item_name.encode('cp1251')[:128]
        except UnicodeEncodeError:
            raise ValueError("Item name must be encodable in WIN1251 (cp1251)")
        if len(item_name_bytes) > 128:
            raise ValueError("Item name must not exceed 128 bytes")

        params = (op_type_byte + quantity_bytes + price_bytes +
                  amount_bytes + tax_bytes + tax_rate_byte + department_byte +
                  payment_method_byte + item_type_byte + item_name_bytes)

        if not 32 <= len(params) + 2 <= 160:  # +2 for cmd code FF46h
            raise ValueError("Message length must be 32-160 bytes including command code")

        return self.send_with_password_command(KKTCommand.OPERATION_V2, params)

    def close_receipt(self, cash=0, payment_2=0, payment_3=0, payment_4=0, payment_5=0, payment_6=0, payment_7=0,
                      payment_8=0, payment_9=0, payment_10=0, payment_11=0, payment_12=0, payment_13=0, payment_14=0,
                      payment_15=0, payment_16=0, rounding=0, vat_20=0, vat_10=0, vat_0=0, no_vat=0, calc_vat_20_120=0,
                      calc_vat_10_110=0, tax_system=0, text="", vat_5=0, vat_7=0, calc_vat_5_105=0, calc_vat_7_107=0):
        """
        Send the Close Check V2 command (FF45h).
        - cash, payment_2 to payment_16: int (5 bytes, payment amounts in kopecks)
        - rounding: int (1 byte, rounding to rubles in kopecks)
        - vat_20, vat_10, vat_0, no_vat, calc_vat_20_120, calc_vat_10_110: int (5 bytes, tax amounts in kopecks)
        - tax_system: int (1 byte, tax system flags, only one bit set)
        - text: str (0-64 bytes, WIN1251 encoded, padded to 64 bytes if 202-byte message)
        - vat_5, vat_7, calc_vat_5_105, calc_vat_7_107: int (5 bytes, optional for 202-byte message)
        Returns: True if ACK received for the message.
        """

        # Convert payment amounts to 5-byte little-endian
        payments = [cash, payment_2, payment_3, payment_4, payment_5, payment_6, payment_7,
                    payment_8, payment_9, payment_10, payment_11, payment_12, payment_13,
                    payment_14, payment_15, payment_16]
        if any(not 0 <= x <= 0xFFFFFFFFFF for x in payments):
            raise ValueError("Payment amounts must be 0 to 2^40-1")
        payment_bytes = b''.join(x.to_bytes(5, 'little') for x in payments)
        # Rounding: 1 byte
        if not 0 <= rounding <= 255:
            raise ValueError("Rounding must be 0-255")
        rounding_byte = bytes([rounding])

        # Taxes: 5 bytes each
        taxes = [vat_20, vat_10, vat_0, no_vat, calc_vat_20_120, calc_vat_10_110]
        if any(not 0 <= x <= 0xFFFFFFFFFF for x in taxes):
            raise ValueError("Tax amounts must be 0 to 2^40-1")
        tax_bytes = b''.join(x.to_bytes(5, 'little') for x in taxes)

        # Tax system: only one bit should be set
        valid_tax_systems = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20}
        if tax_system not in valid_tax_systems:
            raise ValueError("Tax system must have exactly one bit set (0x01, 0x02, 0x04, 0x08, 0x10, 0x20)")
        tax_system_byte = bytes([tax_system])

        # Text: 0-64 bytes, WIN1251 encoded, padded to 64 bytes for 202-byte message
        try:
            text_bytes = text.encode('cp1251')[:64]
        except UnicodeEncodeError:
            raise ValueError("Text must be encodable in WIN1251 (cp1251)")
        if len(text_bytes) > 64:
            raise ValueError("Text must not exceed 64 bytes")

        # Optional taxes for 202-byte message
        optional_taxes = [vat_5, vat_7, calc_vat_5_105, calc_vat_7_107]
        include_optional = any(x != 0 for x in optional_taxes)
        if include_optional:
            if any(not 0 <= x <= 0xFFFFFFFFFF for x in optional_taxes):
                raise ValueError("Optional tax amounts must be 0 to 2^40-1")
            # For 202-byte message, text must be exactly 64 bytes
            text_bytes = text_bytes + b'\x00' * (64 - len(text_bytes))
            optional_tax_bytes = b''.join(x.to_bytes(5, 'little') for x in optional_taxes)
        else:
            optional_tax_bytes = b''

        params = (payment_bytes + rounding_byte + tax_bytes +
                  tax_system_byte + text_bytes + optional_tax_bytes)

        expected_length = 202 if include_optional else len(params) + 2 + 4  # +2 for cmd code FF45h
        if not 118 <= expected_length <= 182 and expected_length != 202:
            raise ValueError("Message length must be 118-182 bytes or 202 bytes including command code")
        return self.send_with_password_command(KKTCommand.CLOSE_RECEIPT_EXTENDED_VARIANT2, params)
