import ast
import inspect
import json
import logging
import os
import re
import uuid

try:
    from logstash_async.formatter import LogstashFormatter
    from logstash_async.handler import AsynchronousLogstashHandler

    LOGSTASH_AVAILABLE = True
except ImportError:
    LOGSTASH_AVAILABLE = False


class SmartLogger(logging.Logger):
    uuid_pattern = re.compile(r"UUID\(['\"]([0-9a-fA-F\-]+)['\"]\)")

    def _pretty_format(self, msg):
        if isinstance(msg, str):
            cleaned = self.uuid_pattern.sub(r'"\1"', msg)

            # Try to locate and replace *every* JSON-like dict/list structure
            # in the string
            def replace_all_json_structures(text):
                pattern = re.compile(
                    r"""
                    (
                        \{
                            [^{}]+
                            (?:\{[^{}]*\}[^{}]*)*
                        \}
                        |
                        \[
                            [^\[\]]+
                            (?:\[[^\[\]]*\][^\[\]]*)*
                        \]
                    )
                """,
                    re.VERBOSE | re.DOTALL,
                )

                def try_parse_and_pretty(m):
                    raw = m.group(0)
                    try:
                        parsed = ast.literal_eval(raw)
                        pretty = json.dumps(
                            parsed, indent=2, ensure_ascii=False
                        )
                        return pretty
                    except Exception:
                        return raw

                return re.sub(pattern, try_parse_and_pretty, text)

            return replace_all_json_structures(cleaned)

        elif isinstance(msg, (dict, list)):

            def sanitize(obj):
                if isinstance(obj, dict):
                    return {
                        k: sanitize(str(v) if isinstance(v, uuid.UUID) else v)
                        for k, v in obj.items()
                    }
                elif isinstance(obj, list):
                    return [sanitize(v) for v in obj]
                else:
                    return str(obj) if isinstance(obj, uuid.UUID) else obj

            try:
                return json.dumps(sanitize(msg), indent=2, ensure_ascii=False)
            except Exception:
                return str(msg)

        return str(msg)

    def _log_with_format_option(
        self, level, msg, args, format=False, **kwargs
    ):
        if format:
            msg = self._pretty_format(msg)
        super()._log(level, msg, args, **kwargs)

    def info(self, msg, *args, format=False, **kwargs):
        self._log_with_format_option(
            logging.INFO, msg, args, format=format, **kwargs
        )

    def debug(self, msg, *args, format=False, **kwargs):
        self._log_with_format_option(
            logging.DEBUG, msg, args, format=format, **kwargs
        )

    def warning(self, msg, *args, format=False, **kwargs):
        self._log_with_format_option(
            logging.WARNING, msg, args, format=format, **kwargs
        )

    def error(self, msg, *args, format=False, **kwargs):
        self._log_with_format_option(
            logging.ERROR, msg, args, format=format, **kwargs
        )

    def critical(self, msg, *args, format=False, **kwargs):
        self._log_with_format_option(
            logging.CRITICAL, msg, args, format=format, **kwargs
        )


class Logger:
    def __init__(
        self,
        logger_name: str = None,
        log_file: str = None,
        log_level: int = getattr(
            logging, os.getenv("LOG_LEVEL", "INFO").upper()
        ),
        log_format: str = "\n%(levelname)s: (%(name)s) == %(message)s "
        " [%(asctime)s]",
        logstash_host: str = None,
        logstash_port: int = 5959,
        logstash_database_path: str = None,
    ):
        try:
            logstash_port = (
                int(logstash_port) if logstash_port is not None else None
            )
        except ValueError:
            raise ValueError(f"Invalid logstash_port: {logstash_port}")

        if logger_name is None:
            for frame_info in inspect.stack():
                module = inspect.getmodule(frame_info.frame)
                if module and not module.__name__.startswith("oguild.logs"):
                    logger_name = module.__name__
                    break
            else:
                logger_name = "__main__"

        logging.setLoggerClass(SmartLogger)
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level)
        self.logger.propagate = False

        if not self.logger.handlers:
            formatter = logging.Formatter(log_format)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            if log_file:
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)

            if logstash_host and LOGSTASH_AVAILABLE:
                try:
                    logstash_handler = AsynchronousLogstashHandler(
                        host=logstash_host,
                        port=logstash_port,
                        database_path=logstash_database_path,
                    )
                    logstash_handler.setFormatter(LogstashFormatter())
                    self.logger.addHandler(logstash_handler)
                except Exception as e:
                    self.logger.error(
                        f"Failed to initialize Logstash handler: {e}"
                    )

    def get_logger(self):
        return self.logger


logger = Logger().get_logger()
