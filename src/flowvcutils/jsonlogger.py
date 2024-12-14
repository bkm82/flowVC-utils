import datetime as dt
import json
import logging
import logging.config
import pathlib
import argparse
from typing import Dict, Optional
from flowvcutils.utils import get_project_root
import os


LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class flowvcutilsJSONFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        fmt_keys: Optional[Dict[str, str]] = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: (
                msg_val
                if (msg_val := always_fields.pop(val, None)) is not None
                else getattr(record, val)
            )
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


project_root = get_project_root()
log_file = os.path.join(project_root, "logs", "flowvcutils.log")
json_file = os.path.join(project_root, "logs", "flowvcutils.log.jsonl")


def settup_logging():
    current_dir = pathlib.Path(__file__).parent
    project_root = current_dir.parent

    config_file = current_dir / "logging_configs" / "config.json"
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    if not config_file.exists():
        raise FileNotFoundError(f"logging configuration not found:{config_file}")

    with open(config_file) as f_in:
        config = json.load(f_in)

    #    for handler_name, handler in config["handlers"].items():
    for handler_name, handler in config["handlers"].items():
        if "filename" in handler:
            handler["filename"] = str(logs_dir / pathlib.Path(handler["filename"]).name)

    # Manually ensure
    config["formatters"]["json"]["()"] = flowvcutilsJSONFormatter

    logging.config.dictConfig(config)


def print_last_logs(num_lines):
    project_root = get_project_root()
    json_file_name = "flowvcutils.log.jsonl"
    json_log_file_path = os.path.join(project_root, "logs", json_file_name)
    # log_file = pathlib.Path("logs/flowvcutils.log.jsonl")
    with open(json_log_file_path, "r") as f:
        lines = f.readlines()
        last_n_lines = lines[-num_lines:]
        for line in last_n_lines:
            try:
                log_entry = json.loads(line)
                print(json.dumps(log_entry, indent=4))
            except json.JSONDecodeError as e:
                print(f"Error printing log {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Print the last n lines form the JSON log file"
    )
    parser.add_argument(
        "num_lines",
        type=int,
        nargs="?",
        default=10,
        help="The number of logs to print (default 10)",
    )

    args = parser.parse_args()
    print_last_logs(args.num_lines)


if __name__ == "__main__":
    main()
