import logging
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
from unicodedata import normalize
from colorama import Fore, Style, init
import traceback
import functools


init(autoreset=True)


class CustomJSONFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.LIGHTRED_EX,
        'CRITICAL': Fore.RED,
    }

    def __init__(
        self, use_colors: bool = False, db_insert_function=None, **kwargs
    ):
        super().__init__()
        self.use_colors = use_colors
        self.kwargs = kwargs
        self.db_insert_function = db_insert_function

    def format(self, record: logging.LogRecord) -> str:
        message = (
            normalize('NFKD', record.getMessage())
            .encode('ASCII', 'ignore')
            .decode('utf-8')
        )
        log_data: Dict[str, Any] = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'message': message,
            'file': record.filename,
            'line': record.lineno,
            'function': record.funcName,
        }

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        if self.db_insert_function:
            try:
                self.db_insert_function.insert(log_data)
            except Exception as e:
                print(f'Erro ao inserir no banco de dados: {e}')

        color = (
            self.COLORS.get(record.levelname, '') if self.use_colors else ''
        )
        formatted_message = (
            f"[{log_data['timestamp']}] "
            f"({color}{log_data['level']}{Style.RESET_ALL if self.use_colors else ''}) "
            f"{log_data['message']} | "
            f"{log_data['file']}(Line {log_data['line']}) | "
            f"Function: {log_data['function']}"
        )

        return formatted_message


class LogManager:
    def __init__(self, connection, rpa):
        self.connection = connection
        self.rpa = rpa

    def setup_logger(
        self,
        name: str = __name__,
        log_file: Optional[str] = None,
        level: int = logging.INFO,
        db_insert_function=None,
    ) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Limpa handlers para evitar duplicados
        logger.handlers.clear()

        # Configurando formatter e handlers
        console_formatter = CustomJSONFormatter(
            use_colors=True, db_insert_function=db_insert_function
        )
        file_formatter = CustomJSONFormatter(use_colors=False)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        return logger

    def exception(self, logger: logging.Logger):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    tb = traceback.extract_tb(e.__traceback__)
                    filename, lineno, function_name, _ = tb[-1]

                    log_message = (
                        f'An exception occurred...\n'
                        f'Type: {type(e).__name__}\n'
                        f'Message: {e}\n'
                        f'Location:\n'
                        f' - File: {filename}\n'
                        f' - Line: {lineno}\n'
                        f' - Function: {func.__name__}\n\n'
                    )

                    logger.error(log_message)

            return wrapper

        return decorator

    def get_logger(self, another_directory: str = None):
        day = datetime.now().strftime('%d_%m_%Y')
        date_path = Path(f'{another_directory if another_directory else 'logs'}/{day}')
        date_path.mkdir(parents=True, exist_ok=True)  # Cria o diretório da data se não existir

        # Formata a hora atual para o nome do arquivo
        time_stamp = datetime.now().strftime('%H_%M')
        log_file_path = date_path / f'{time_stamp}.log'

        # ilogger = self.setup_logger(
        #     name='insert_logger',
        #     log_file=str(log_file_path),
        #     level=logging.DEBUG,
        #     db_insert_function=RPALogRepository(self.connection, self.rpa, DetailLogger)
        # )
        logger = self.setup_logger(
            name='common_logger',
            log_file=str(log_file_path),
            level=logging.DEBUG,
        )

        return (logger, self.exception)

# Impantação, apenas sua classe de conexão, padrão que gerencie a conexão dentro do contexto ´with´
# ilogger, logger, exception = LogManager(DBConnectionHandler, rpa='x').get_logger()
