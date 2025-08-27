#logger.py
import csv
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

SUMMARY_CSV_PATH = Path("amendment_results.csv")
FIELDS = ["timestamp", "amd_file", "row_idx", "law_id", "amendment", "result", "description"]

class SummaryCSVHandler(logging.Handler):
    def __init__(self, path: Path):
        super().__init__()
        self.path = path
        self.first_time = not path.exists()
        self.fp = path.open("a", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.fp, fieldnames=FIELDS)
        if self.first_time:
            self.writer.writeheader()

    def emit(self, record: logging.LogRecord):
        row = {key: "" for key in FIELDS}
        row.update(record.__dict__["csv_row"])
        row["timestamp"] = datetime.now(timezone.utc).astimezone().strftime("%d/%m/%y %H:%M:%S")
        self.writer.writerow(row)
        self.fp.flush()

def setup_summary_logger() -> logging.Logger:
    logger = logging.getLogger("summary_logger")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.handlers.clear()
    logger.addHandler(SummaryCSVHandler(SUMMARY_CSV_PATH))
    return logger

def log_amendment_result(
    logger: logging.Logger,
    amd_file: str,
    row_idx: int,
    law_id: str,
    amendment: int | str,
    success: bool,
    reason: str,
):
    logger.info(
        "Success" if success else "Failure",
        extra={
            "csv_row": {
                "amd_file": amd_file,
                "row_idx": row_idx,
                "law_id": law_id, 
                "amendment": amendment,
                "result": "success" if success else "failure",
                "description": reason,
            }
        },
    )
