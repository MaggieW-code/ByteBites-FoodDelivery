import json
from pathlib import Path

import pytest

from backend.app.repositories.json_list_store import DataFileMalformedError, DataFileMissingError, JsonListStore


def test_save_then_load_round_trips(tmp_path: Path) -> None:
    store = JsonListStore(tmp_path / "records.json")

    store.save([{"id": "rec_0001"}])

    assert store.load() == [{"id": "rec_0001"}]


def test_save_leaves_no_temporary_files(tmp_path: Path) -> None:
    JsonListStore(tmp_path / "records.json").save([{"id": "rec_0001"}])

    assert [path.name for path in tmp_path.iterdir()] == ["records.json"]


def test_failed_save_keeps_the_old_file(tmp_path: Path) -> None:
    data_file = tmp_path / "records.json"
    data_file.write_text(json.dumps([{"id": "rec_0001"}]), encoding="utf-8")

    with pytest.raises(TypeError):
        JsonListStore(data_file).save([{"id": object()}])

    assert json.loads(data_file.read_text(encoding="utf-8")) == [{"id": "rec_0001"}]
    assert [path.name for path in tmp_path.iterdir()] == ["records.json"]


def test_missing_file_raises_unless_allowed(tmp_path: Path) -> None:
    with pytest.raises(DataFileMissingError):
        JsonListStore(tmp_path / "records.json").load()

    assert JsonListStore(tmp_path / "records.json", is_missing_file_empty=True).load() == []


@pytest.mark.parametrize("contents", ["not json", '{"id": 1}'], ids=["invalid-json", "not-a-list"])
def test_malformed_file_raises(tmp_path: Path, contents: str) -> None:
    data_file = tmp_path / "records.json"
    data_file.write_text(contents, encoding="utf-8")

    with pytest.raises(DataFileMalformedError):
        JsonListStore(data_file).load()
