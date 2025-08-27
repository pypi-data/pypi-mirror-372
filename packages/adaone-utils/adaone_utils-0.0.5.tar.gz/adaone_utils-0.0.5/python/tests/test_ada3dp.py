import pytest
from pathlib import Path
from polars import DataFrame
from adaone_utils import Toolpath, Parameters

TEST_FILE_PATH = Path(__file__).parent / "test.ada3dp"
OUTPUT_FILE_PATH = Path(__file__).parent / "test_output.ada3dp"


def test_read_ada3dp() -> None:
    toolpath = Toolpath.from_file(TEST_FILE_PATH)
    assert isinstance(toolpath.data, DataFrame)
    assert not toolpath.data.is_empty()
    assert isinstance(toolpath.parameters[0], Parameters)


def test_write_ada3dp() -> None:
    toolpath = Toolpath.from_file(TEST_FILE_PATH)
    toolpath.to_file(OUTPUT_FILE_PATH)
    assert OUTPUT_FILE_PATH.exists()


def test_roundtrip_ada3dp() -> None:
    original_toolpath = Toolpath.from_file(TEST_FILE_PATH)
    original_toolpath.to_file(OUTPUT_FILE_PATH)
    roundtrip_toolpath = Toolpath.from_file(OUTPUT_FILE_PATH)
    assert original_toolpath.data.equals(roundtrip_toolpath.data)
    assert original_toolpath.parameters == roundtrip_toolpath.parameters


if __name__ == "__main__":
    pytest.main()
