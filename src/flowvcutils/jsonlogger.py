import datetime as dt
import json
import logging
import pathlib
import argparse

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


def settup_logging():
    config_file = pathlib.Path("logging_configs/config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
    logging.config.dictConfig(config)


class flowvcutilsJSONFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
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


def print_last_logs(num_lines):
    log_file = pathlib.Path("logs/flowvcutils.log.jsonl")
    with open(log_file, "r") as f:
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
