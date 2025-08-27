from adaone_utils import Toolpath
from pathlib import Path
from tempfile import NamedTemporaryFile


def test_roundtrip():
    input_file = Path(__file__).parent / "cone.ada3dp"

    with NamedTemporaryFile(suffix=".ada3dp", delete=True) as temp:
        tp = Toolpath.from_file(input_file)
        
        tp.to_file(temp.name)
        out_bytes = Path(temp.name).read_bytes()

    assert input_file.read_bytes() == out_bytes
