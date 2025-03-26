import logging
import re
from urllib.parse import urlparse, parse_qs
import json


class LogCaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self._logs: list[str] = []

    def emit(self, record) -> None:
        """Append formatted log record to internal storage"""
        try:
            self._logs.append(self.format(record))
        except Exception:
            self.handleError(record)

    def get_logs(self) -> list[str]:
        """Get captured logs"""
        return self._logs.copy()  # Return copy to prevent external modification

    def clear(self) -> None:
        """Clear captured logs"""
        self._logs.clear()


class LoggerFactory:
    root_logger_capture = LogCaptureHandler()

    @classmethod
    def get_logger(cls, name: str, level: int = logging.DEBUG) -> logging.Logger:
        """Get a configured logger with unified settings that also captures requests logs

        Args:
            name: Logger name
            level: Logging level (default: DEBUG)

        Returns:
            Configured logger instance
        """
        # Configure root logger first (to capture requests logs)
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # Configure named logger
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Avoid duplicate handlers
        if not cls.root_logger_capture in root_logger.handlers:
            # Create and configure console handler
            ch = logging.StreamHandler()
            ch.setLevel(level)
            formatter = logging.Formatter(
                "[%(levelname)s] %(asctime)s - %(name)s - %(message)s"
            )
            ch.setFormatter(formatter)

            # Configure capture handler
            cls.root_logger_capture.setFormatter(formatter)

            # Add handlers
            root_logger.addHandler(ch)
            root_logger.addHandler(cls.root_logger_capture)

        return logger

    @classmethod
    def get_root_logger_logs(cls) -> list[str]:
        """Get all captured logs from root logger"""
        return cls.root_logger_capture.get_logs()

    @classmethod
    def clear_root_logger_logs(cls) -> None:
        """Clear captured logs from root logger"""
        cls.root_logger_capture.clear()


class LogParser:
    @classmethod
    def parse_log_entries(cls, log_entries: list[str]) -> list[dict[str, str]]:
        results = []
        for entry in log_entries:
            # Skip entries without URLs
            if '"GET ' not in entry and '"POST ' not in entry:
                continue

            # Extract the URL part
            domain_match = re.search(r'(https?://[^\s"]+)', entry)
            url_match = re.search(r'"(?:GET|POST) ([^\s"]+)', entry)
            if not domain_match or not url_match:
                continue

            full_url = domain_match.group(1) + url_match.group(1)

            # Parse domain and parameters
            domain = None
            params = {}

            try:
                parsed = urlparse(full_url)
                # Extract domain without port
                domain = parsed.netloc.split(":")[0] if parsed.netloc else None
                if parsed.query:
                    params = parse_qs(parsed.query)
            except Exception as e:
                print(f"Error parsing URL {full_url}: {e}")
                continue
            timestamp = re.match(r"\[(.*?)\] (.*?) -", entry).group(2)
            level = re.match(r"\[(.*?)\] (.*?) -", entry).group(1)
            logger = re.match(r"\[(.*?)\] (.*?) - (.*?) -", entry).group(3)
            domain = domain
            path = parsed.path
            params = params
            raw_entry = entry

            results.append(
                {
                    "timestamp": timestamp,
                    "level": level,
                    "logger": logger,
                    "domain": domain,
                    "path": path,
                    "params": params,
                    "full_url": full_url,
                    "raw_entry": raw_entry,
                }
            )
        return results

    @classmethod
    def show_parsed_data(cls, parsed_data: list[dict[str, str]]) -> None:
        for entry in parsed_data:
            print(f"\nTimestamp: {entry['timestamp']}")
            print(f"Level: {entry['level']}")
            print(f"Domain: {entry['domain']}")
            print(f"Path: {entry['path']}")
            print("Parameters:")
            for param, values in entry["params"].items():
                print(f"  {param}: {values[0] if len(values) == 1 else values}")
            print("-" * 50)

    @classmethod
    def show_log_entries(cls, log_entries: list[str]) -> None:
        parsed_data = cls.parse_log_entries(log_entries)
        cls.show_parsed_data(parsed_data)

    @classmethod
    def get_params_from_parsed_data(cls, parsed_data: list[dict[str, str]]) -> dict:
        params = {}
        for entry in parsed_data:
            for param, values in entry["params"].items():
                if entry["domain"] not in params:
                    params[entry["domain"]] = {}
                params[entry["domain"]][param] = (
                    values[0] if len(values) == 1 else values
                )
        return params

    @classmethod
    def get_params_from_log_entries(cls, log_entries: list[str]) -> dict:
        parsed_data = cls.parse_log_entries(log_entries)
        return cls.get_params_from_parsed_data(parsed_data)

    @classmethod
    def save_params_from_parsed_data(
        cls, parsed_data: list[dict[str, str]], file_name: str = "output/params.json"
    ) -> dict:
        params = cls.get_params_from_parsed_data(parsed_data)
        with open(file_name, "w") as f:
            json.dump(params, f, indent=4)
        return params

    @classmethod
    def save_params_from_log_entries(
        cls, log_entries: list[str], file_name: str = "output/params.json"
    ) -> dict:
        parsed_data = cls.parse_log_entries(log_entries)
        return cls.save_params_from_parsed_data(parsed_data, file_name)
