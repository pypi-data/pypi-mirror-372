from enum import Enum, IntEnum


ENQ = b'\x05'  # Запрос (Enquiry)
STX = b'\x02'  # Начало текста (Start of Text)
ACK = b'\x06'  # Подтверждение (Acknowledge)
NAK = b'\x15'  # Отрицательное подтверждение (Negative Acknowledge)

class KKTCommand(IntEnum):
    REQUEST_DUMP = 0x01  # Запрос дампа
    REQUEST_DATA = 0x02  # Запрос данных
    INTERRUPT_DATA_OUTPUT = 0x03  # Прерывание выдачи данных
    SHORT_KKT_STATUS_REQUEST = 0x10  # Короткий запрос состояния ККТ
    KKT_STATUS_REQUEST = 0x11  # Запрос состояния ККТ
    PRINT_BOLD_STRING_FONT2 = 0x12  # Печать жирной строки (шрифт 2)
    BEEP = 0x13  # Гудок
    SET_EXCHANGE_PARAMETERS = 0x14  # Установка параметров обмена
    READ_EXCHANGE_PARAMETERS = 0x15  # Чтение параметров обмена
    TECHNOLOGICAL_RESET = 0x16  # Технологическое обнуление
    PRINT_STANDARD_STRING_FONT1 = 0x17  # Печать стандартной строки (шрифт 1)
    PRINT_DOCUMENT_HEADER = 0x18  # Печать заголовка документа
    TEST_RUN = 0x19  # Тестовый прогон
    REQUEST_CASH_REGISTER = 0x1A  # Запрос денежного регистра
    REQUEST_OPERATIONAL_REGISTER = 0x1B  # Запрос операционного регистра
    WRITE_TABLE = 0x1E  # Запись таблицы
    READ_TABLE = 0x1F  # Чтение таблицы
    PROGRAM_TIME = 0x21  # Программирование времени
    PROGRAM_DATE = 0x22  # Программирование даты
    CONFIRM_DATE_PROGRAMMING = 0x23  # Подтверждение программирования даты
    INITIALIZE_TABLES = 0x24  # Инициализация таблиц начальными значениями
    CUT_RECEIPT = 0x25  # Отрезка чека
    READ_FONT_PARAMETERS = 0x26  # Прочитать параметры шрифта
    GENERAL_RESET = 0x27  # Общее гашение
    OPEN_CASH_DRAWER = 0x28  # Открыть денежный ящик
    FEED_PAPER = 0x29  # Протяжка
    INTERRUPT_TEST_RUN = 0x2B  # Прерывание тестового прогона
    GET_OPERATIONAL_REGISTER_READINGS = 0x2C  # Снятие показаний операционных регистров
    REQUEST_TABLE_STRUCTURE = 0x2D  # Запрос структуры таблицы
    REQUEST_FIELD_STRUCTURE = 0x2E  # Запрос структуры поля
    PRINT_STRING_WITH_FONT = 0x2F  # Печать строки данным шрифтом
    DAILY_REPORT_NO_RESET = 0x40  # Суточный отчет без гашения
    DAILY_REPORT_WITH_RESET = 0x41  # Суточный отчет с гашением - закрытие сменыы
    PRINT_GRAPHICS_512_SCALED = 0x4D  # Печать графики-512 с масштабированием
    UPLOAD_GRAPHICS_512 = 0x4E  # Загрузка графики-512
    PRINT_GRAPHICS_SCALED = 0x4F  # Печать графики с масштабированием
    DEPOSIT = 0x50  # Внесение
    PAYOUT = 0x51  # Выплата
    PRINT_CLICHE = 0x52  # Печать клише
    END_DOCUMENT = 0x53  # Конец документа
    PRINT_AD_TEXT = 0x54  # Печать рекламного текста
    RETURN_ERROR_NAME = 0x6B  # Возврат названия ошибки
    SALE = 0x80  # Продажа
    PURCHASE = 0x81  # Покупка
    RETURN_SALE = 0x82  # Возврат продажи
    RETURN_PURCHASE = 0x83  # Возврат покупки
    CLOSE_RECEIPT = 0x85  # Закрытие чека
    ANNUL_RECEIPT = 0x88  # Аннулирование чека
    RECEIPT_SUBTOTAL = 0x89  # Подытог чека
    PRINT_RECEIPT_COPY = 0x8C  # Печать копии чека (Повтор документа)
    OPEN_RECEIPT = 0x8D  # Открыть чек
    CLOSE_RECEIPT_EXTENDED = 0x8E  # Закрытие чека расширенное
    CONTINUE_PRINTING = 0xB0  # Продолжение печати
    UPLOAD_GRAPHICS = 0xC0  # Загрузка графики
    PRINT_GRAPHICS = 0xC1  # Печать графики
    PRINT_EAN13_BARCODE = 0xC2  # Печать штрих-кода EAN-13
    PRINT_EXTENDED_GRAPHICS = 0xC3  # Печать расширенной графики
    UPLOAD_EXTENDED_GRAPHICS = 0xC4  # Загрузка расширенной графики
    PRINT_GRAPHIC_LINE = 0xC5  # Печать графической линии (одномерный штрихкод)
    DAILY_REPORT_WITH_RESET_TO_BUFFER = 0xC6  # Суточный отчет с гашением в буфер
    PRINT_BARCODE_PRINTER_MEANS = 0xCB  # Печать штрих-кода средствами принтера
    PRINTER_STATUS_REQUEST_LONG = 0xD0  # Запрос состояния принтера длинное
    PRINTER_STATUS_REQUEST_SHORT = 0xD1  # Запрос состояния принтера короткое
    UPLOAD_DATA = 0xDD  # Загрузка данных
    PRINT_MULTIDIMENSIONAL_BARCODE = 0xDE  # Печать многомерного штрих-кода
    OPEN_SHIFT = 0xE0  # Открыть смену
    EXTENDED_REQUEST = 0xF7  # Расширенный запрос
    GET_DEVICE_TYPE = 0xFC  # Получить тип устройства
    FN_STATUS_REQUEST = 0xFF01  # Запрос статуса ФН
    FN_NUMBER_REQUEST = 0xFF02  # Запрос номера ФН
    FN_EXPIRATION_DATE_REQUEST = 0xFF03  # Запрос срока действия ФН
    FN_VERSION_REQUEST = 0xFF04  # Запрос версии ФН
    START_KKT_REGISTRATION_REPORT = 0xFF05  # Начать отчет о регистрации ККТ
    GENERATE_KKT_REGISTRATION_REPORT = 0xFF06  # Сформировать отчёт о регистрации ККТ
    RESET_FN_STATE = 0xFF07  # Сброс состояния ФН
    CANCEL_DOCUMENT_IN_FN = 0xFF08  # Отменить документ в ФН
    REQUEST_LAST_FISCALIZATION_TOTALS = 0xFF09  # Запрос итогов последней фискализации (перерегистрации)
    FIND_FISCAL_DOCUMENT_BY_NUMBER = 0xFF0A  # Найти фискальный документ по номеру
    OPEN_SHIFT_IN_FN = 0xFF0B  # Открыть смену в ФН
    TRANSFER_ARBITRARY_TLV_STRUCTURE = 0xFF0C  # Передать произвольную TLV структуру
    DISCOUNT_SURCHARGE_OPERATION = 0xFF0D  # Операция со скидками и надбавками
    REQUEST_FN_OPENING_PARAMETER = 0xFF0E  # Запрос параметра открытия ФН
    REQUEST_BUFFER_DATA_AVAILABILITY = 0xFF30  # Запросить о наличие данных в буфере
    READ_DATA_BLOCK_FROM_BUFFER = 0xFF31  # Прочитать блок данных из буфера
    START_WRITE_DATA_TO_BUFFER = 0xFF32  # Начать запись данных в буфер
    WRITE_DATA_BLOCK_TO_BUFFER = 0xFF33  # Записать блок данных в буфер
    GENERATE_KKT_REREGISTRATION_REPORT = 0xFF34  # Сформировать отчёт о перерегистрации ККТ
    START_CORRECTION_RECEIPT_FORMATION = 0xFF35  # Начать формирование чека коррекции
    GENERATE_CORRECTION_RECEIPT_FF36H = 0xFF36  # Сформировать чек коррекции FF36H
    START_REPORT_ON_SETTLEMENT_STATUS = 0xFF37  # Начать формирование отчёта о состоянии расчётов
    GENERATE_REPORT_ON_SETTLEMENT_STATUS = 0xFF38  # Сформировать отчёт о состоянии расчётов
    GET_INFORMATION_EXCHANGE_STATUS = 0xFF39  # Получить статус информационного обмена
    REQUEST_FISCAL_DOCUMENT_IN_TLV = 0xFF3A  # Запросить фискальный документ в TLV формате
    READ_TLV_FISCAL_DOCUMENT = 0xFF3B  # Чтение TLV фискального документа
    REQUEST_RECEIPT_FOR_OFD_DATA = 0xFF3C  # Запрос квитанции о получении данных в ОФД по номеру документа
    START_FISCAL_MODE_CLOSING = 0xFF3D  # Начать закрытие фискального режима
    CLOSE_FISCAL_MODE = 0xFF3E  # Закрыть фискальный режим
    REQUEST_FD_WITHOUT_RECEIPT_COUNT = 0xFF3F  # Запрос количества ФД на которые нет квитанции
    REQUEST_CURRENT_SHIFT_PARAMETERS = 0xFF40  # Запрос параметров текущей смены
    START_SHIFT_OPENING = 0xFF41  # Начать открытие смены
    START_SHIFT_CLOSING = 0xFF42  # Начать закрытие смены
    CLOSE_RECEIPT_EXTENDED_VARIANT2 = 0xFF45  # Закрытие чека расширенное вариант №2
    OPERATION_V2 = 0xFF46  # Операция V21211
    GENERATE_CORRECTION_RECEIPT_V2 = 0xFF4A  # Сформировать чек коррекции V2
    DISCOUNT_SURCHARGE_RECEIPT_ROSNEFT = 0xFF4B  # Скидка, надбавка на чек для Роснефти
    REQUEST_FISCALIZATION_TOTALS_V2 = 0xFF4C  # Запрос итогов фискализации (перерегистрации) V2
    TRANSFER_ARBITRARY_TLV_STRUCTURE_TO_OPERATION = 0xFF4D  # Передать произвольную TLV структуру привязанную к операции
    WRITE_FR_FIRMWARE_BLOCK_TO_SD = 0xFF4E  # Запись блока данных прошивки ФР на SD карту
    ONLINE_PAYMENT = 0xFF50  # Онлайн платёж
    ONLINE_PAYMENT_STATUS = 0xFF51  # Статус онлайн платёжа
    GET_LAST_ONLINE_PAYMENT_REQUISITE = 0xFF52  # Получить реквизит последнего онлайн платёжа
    REQUEST_FISCALIZATION_PARAMETER = 0xFF60  # Запрос параметра фискализации
    CHECK_MARKED_GOODS = 0xFF61  # Проверка маркированного товара
    SYNCHRONIZE_REGISTERS_WITH_FN_COUNTER = 0xFF62  # Синхронизировать регистры со счётчиком ФН
    REQUEST_FN_FREE_MEMORY_RESOURCE = 0xFF63  # Запрос ресурса свободной памяти в ФН
    TRANSFER_TLV_TO_FN_FROM_BUFFER = 0xFF64  # Передача в ФН TLV из буфера
    GET_RANDOM_SEQUENCE = 0xFF65  # Получить случайную последовательность
    AUTHORIZE = 0xFF66  # Авторизоваться
    LINK_MARKED_GOODS_TO_POSITION = 0xFF67  # Привязка маркированного товара к позиции
    GET_MARKED_GOODS_NOTIFICATION_STATUS = 0xFF68  # Получить состояние по передаче уведомлений о реализации маркированных товаров
    ACCEPT_REJECT_MARKING_CODE = 0xFF69  # Принять или отвергнуть введенный код маркировки
    REQUEST_MARKING_CODE_STATUS = 0xFF70  # Запрос статуса по работе с кодами маркировки
    START_MARKED_GOODS_UNLOADING = 0xFF71  # Начать выгрузку уведомлений о реализации маркированных товаров (в автономном режиме)
    READ_NOTIFICATION_BLOCK = 0xFF72  # Прочитать блок уведомления (в автономном режиме)
    CONFIRM_NOTIFICATION_UNLOADING = 0xFF73  # Подтвердить выгрузку уведомления (в автономном режиме)
    FN_EXECUTION_REQUEST = 0xFF74  # Запрос исполнения ФН
    REQUEST_TOTAL_DOCUMENT_SIZE_IN_FN = 0xFF75  # Запрос общего размера данных документа в ФН

# Перечисление кодов устройств для команды Запрос дампа (01h)
class DeviceCode(Enum):
    CLOCK = 0x03  # Часы
    NON_VOLATILE_MEMORY = 0x04  # Энергонезависимая память
    KKT_PROGRAM_MEMORY = 0x06  # Память программ ККТ
    KKT_RAM = 0x07  # Оперативная память ККТ
    FILE_SYSTEM_IMAGE = 0x08  # Образ файловой системы
    ULINUX_IMAGE = 0x09  # Образ uLinux
    EXECUTABLE_SOFTWARE_FILE = 0x0A  # Исполняемый файл ПО
    KY_PROGRAM_MEMORY = 0x86  # Память программ КЯ

# Константы для флагов ККТ (битовое поле)
class KKTFlags:
    OPERATIONAL_JOURNAL_ROLL_EXISTS = 0x01  # Бит 0: Рулон операционного журнала (контрольной ленты) (0 – нет, 1 – есть)
    RECEIPT_TAPE_ROLL_EXISTS = 0x02  # Бит 1: Рулон чековой ленты (0 – нет, 1 – есть)
    OPERATIONAL_JOURNAL_OPTICAL_SENSOR = 0x40  # Бит 6: Оптический датчик операционного журнала (контрольной ленты) (0 – бумаги нет, 1 – бумага есть)
    RECEIPT_TAPE_OPTICAL_SENSOR = 0x80  # Бит 7: Оптический датчик чековой ленты (0 – бумаги нет, 1 – бумага есть)
    CONTROL_TAPE_THERMAL_HEAD_LEVER = 0x100  # Бит 8: Рычаг термоголовки контрольной ленты (0 – поднят, 1 – опущен)
    RECEIPT_TAPE_THERMAL_HEAD_LEVER = 0x200  # Бит 9: Рычаг термоголовки чековой ленты (0 – поднят, 1 – опущен)
    KKT_HOUSING_COVER = 0x400  # Бит 10: Крышка корпуса ККТ (0 – опущена, 1 – поднята)
    CASH_DRAWER = 0x800  # Бит 11: Денежный ящик (0 – закрыт, 1 – окрыт)
    KKT_HOUSING_CONTROL_TAPE_COVER = 0x1000  # Бит 12: Крышка корпуса ККТ контрольной ленты (0 – опущена, 1 – поднята)

# Константы для флагов статуса обновления ключей (Короткий запрос состояния ККТ)
class KeyUpdateStatusFlags:
    UPDATE_REQUIRED = 0x01  # Бит 0: требуется обновление
    URGENT_UPDATE_REQUIRED = 0x02  # Бит 1: требуется срочное обновление
    UPDATED_KEYS_COUNT_MASK = 0xFC  # Биты 2-7: количество обновленных ключей (0-63)

# Перечисление результатов последней печати
class LastPrintResult(Enum):
    PRINT_SUCCESSFUL = 0  # печать завершена успешно
    PAPER_BREAK = 1  # произошел обрыв бумаги
    PRINTER_ERROR = 2  # ошибка принтера (перегрев головки, другая ошибка)
    PRINTING_IN_PROGRESS = 5  # идет печать

# Константы для портов ККТ
class KKTPort:
    COM_PORTS_START = 0  # COM-порты от 0 до 127
    COM_PORTS_END = 127
    TCP_SOCKET = 128  # TCP сокет
    RESERVED_START = 129  # Зарезервировано от 129 до 255
    RESERVED_END = 255

# Перечисление кодов скорости обмена
class ExchangeSpeedCode(Enum):
    BAUD_2400 = 0  # 2400 бод
    BAUD_4800 = 1  # 4800 бод
    BAUD_9600 = 2  # 9600 бод
    BAUD_19200 = 3  # 19200 бод
    BAUD_38400 = 4  # 38400 бод
    BAUD_57600 = 5  # 57600 бод
    BAUD_115200 = 6  # 115200 бод
    BAUD_230400 = 7  # 230400 бод
    BAUD_460800 = 8  # 460800 бод
    BAUD_921600 = 9  # 921600 бод

# Перечисление типов отчетов о регистрации ККТ
class RegistrationReportType(Enum):
    KKT_REGISTRATION_REPORT = 0x00  # Отчет о регистрации ККТ
    KKT_REG_CHANGE_FN_REPLACEMENT = 0x01  # Отчет об изменении параметров регистрации ККТ, в связи с заменой ФН
    KKT_REG_CHANGE_NO_FN_REPLACEMENT = 0x02  # Отчет об изменении параметров регистрации ККТ без замены ФН

# Константы для флагов кодов налогообложения (битовое поле)
class TaxationCodeFlags:
    OSN = 0x01  # Бит 0: ОСН (Общая система налогообложения)
    USN_INCOME = 0x02  # Бит 1: УСН доход (Упрощенная система налогообложения доход)
    USN_INCOME_MINUS_EXPENSE = 0x04  # Бит 2: УСН доход минус расход (Упрощенная система налогообложения доход минус расход)
    ENVD = 0x08  # Бит 3: ЕНВД (Единый налог на вмененный доход)
    ESP = 0x10  # Бит 4: ЕСП (Единая сельскохозяйственная система налогообложения)
    PSN = 0x20  # Бит 5: ПСН (Патентная система налогообложения)

# Константы для флагов режима работы ККТ (битовое поле)
class OperationModeFlags:
    ENCRYPTION = 0x01  # Бит 0: Шифрование
    AUTONOMOUS_MODE = 0x02  # Бит 1: Автономный режим
    AUTOMATIC_MODE = 0x04  # Бит 2: Автоматический режим
    SERVICES_SECTOR = 0x08  # Бит 3: Применение в сфере услуг
    BSO_MODE = 0x10  # Бит 4: Режим БСО (Бланк строгой отчетности)
    INTERNET_APPLICATION = 0x20  # Бит 5: Применение в Интернет
    PUBLIC_CATERING = 0x40  # Бит 6: Применение ККТ в общественном питании
    WHOLESALE_TRADE = 0x80  # Бит 7: Применение ККТ в оптовой торговле с организациями и индивидуальными предпринимателями

# Перечисление типов программного обеспечения ФН
class FNSoftwareType(Enum):
    DEBUG_VERSION = 0  # Отладочная версия
    SERIAL_VERSION = 1  # Серийная версия

# Перечисление типов документа для команды Открыть чек (8Dh)
class OpenCheckDocumentType(Enum):
    SALE = 0  # Продажа
    PURCHASE = 1  # Покупка
    RETURN_SALE = 2  # Возврат продажи
    RETURN_PURCHASE = 3  # Возврат покупки