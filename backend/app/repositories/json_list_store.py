import json
import os
import tempfile
from pathlib import Path
from typing import Any


class DataFileError(Exception):
    """A data file can't be read or written."""


class DataFileMissingError(DataFileError):
    pass


class DataFileMalformedError(DataFileError):
    pass


class JsonListStore:
    """One JSON file whose top level is a list of records. Writes replace the file atomically."""

    def __init__(self, data_path: Path, *, is_missing_file_empty: bool = False) -> None:
        self.data_path = data_path
        self.is_missing_file_empty = is_missing_file_empty

    def load(self) -> list[dict[str, Any]]:
        try:
            text = self.data_path.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            if self.is_missing_file_empty:
                return []
            raise DataFileMissingError(f"Data file not found: {self.data_path}") from error

        try:
            records = json.loads(text)
        except json.JSONDecodeError as error:
            raise DataFileMalformedError(f"Data file is not valid JSON: {self.data_path}") from error

        if not isinstance(records, list):
            raise DataFileMalformedError(f"Data file must contain a list: {self.data_path}")
        return records

    def save(self, records: list[dict[str, Any]]) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        file_descriptor, temporary_name = tempfile.mkstemp(dir=self.data_path.parent, suffix=".tmp")
        try:
            with os.fdopen(file_descriptor, "w", encoding="utf-8") as temporary_file:
                json.dump(records, temporary_file, indent=2)
            os.replace(temporary_name, self.data_path)
        except BaseException:
            Path(temporary_name).unlink(missing_ok=True)
            raise
