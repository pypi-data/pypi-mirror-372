"""
    from logery import get_logger

    logger = get_logger("mylogger", level="DEBUG")
    logger.debug("Your log works")
"""
# ruff: noqa: E501
import argparse
import json
import textwrap
from pathlib import Path

from rich import print as rprint


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logery",
        description=textwrap.dedent("""\
            logery configures python standard logging library for you
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dotenv",
        type=Path,
        metavar="FILEPATH",
        help="Create or append to a .env file with logging config variables.",
    )

    parser.add_argument(
        "--json",
        type=Path,
        metavar="FILEPATH",
        help="Create or overwrite a logging JSON config file.",
    )

    return parser


def write_file(
    path: Path, data: str, mode: str = "r", encoding: str | None = "utf8"
) -> None:
    with path.open(mode, encoding=encoding) as file:
        file.write(data)


def write_dotenv(path: Path, json_file_name: str = "logging.conf.json") -> None:
    path = path.resolve()

    data = textwrap.dedent(f"""\

    # Logery
    # Configurações dos logs
    # Se eu mudar o caminho da pasta de logs, devo lembrar de mudar no arquivo
    # logging.conf.json.
    LOGS_DIR=logs
    # Arquivo de configuração do logging em JSON que será convertido em dict
    # e usado com dictConfig
    LOGGING_CONFIG_JSON='{json_file_name}'

    # Nome do logger usado dentro da configuração do logging do Python.
    SETUP_LOGGER_NAME='config_setup'
    # Level do logger usado dentro da configuração do logging do Python.
    # Dica: Subir para WARNING vai desativar os logs relacionado à configuração
    # do logging
    SETUP_LOGGER_LEVEL='WARNING'

    # Configuração de nível (level) padrão para todos os loggers criados com
    # get_logger
    DEFAULT_LOGGER_LEVEL='WARNING'
    # END OF Logery

    """)

    write_file(
        path=path,
        mode="a",
        data=data,
    )

    rprint(f"\nWROTE .env data to file: {path}\n")
    rprint(data)


def write_json(path: Path) -> Path:
    path = path.resolve()
    data = json.dumps(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "file": {
                    "format": "%(levelname)s | %(name)s | %(asctime)s | %(message)s | %(filename)s:%(lineno)d | %(funcName)s | %(module)s | %(process)d:%(processName)s | %(thread)d:%(threadName)s"
                },
                "json": {
                    "()": "logery.JSONLogFormatter",
                    "include_keys": [
                        "created",
                        "message",
                        "levelname",
                        "name",
                        "filename",
                        "module",
                        "exc_info",
                        "lineno",
                        "threadName",
                        "processName",
                        "taskName",
                        "args",
                        "context",
                    ],
                },
                "console": {"format": "%(message)s", "datefmt": "[%X]"},
            },
            "filters": {
                "max_level_info": {"()": "logery.MaxLevelFilter", "max_level": "INFO"}
            },
            "handlers": {
                "queue": {
                    "class": "logging.handlers.QueueHandler",
                    "handlers": ["file"],
                    "respect_handler_level": True,
                },
                "console": {
                    "()": "logery.MyRichHandler",
                    "formatter": "console",
                    "rich_tracebacks": True,
                    "tracebacks_show_locals": False,
                    "show_time": True,
                    "show_level": True,
                    "omit_repeated_times": False,
                    "markup": False,
                    "enable_link_path": True,
                    "show_path": True,
                    "file": "stdout",
                    "level": "DEBUG",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "file",
                    "filename": "logs/logery.log",
                    "maxBytes": 5242880,
                    "backupCount": 5,
                    "encoding": "utf-8",
                },
            },
            "root": {"handlers": ["console", "queue"]},
        },
        indent=2,
    )

    write_file(
        path=path,
        mode="w",
        data=data,
    )

    rprint(f"\nWROTE JSON data to file: {path}\n")
    rprint(data)

    return path


def run(dotenv_name = '.env', json_conf = 'json_config.json') -> None:
    import os
    from pathlib import Path

    BASEDIR = Path(os.getcwd())
    DOTENV_PATH = BASEDIR / dotenv_name
    JSON_PATH = BASEDIR / json_conf

    json_file = write_json(JSON_PATH)
    write_dotenv(DOTENV_PATH, json_file_name=json_file.name)

    rprint("\n✅ Everything is ready, try running\n")
    rprint(">>> from logery import get_logger\n")
    rprint('>>> logger = get_logger("mylogger", level="DEBUG")')
    rprint('>>> logger.debug("Your log works")\n')
