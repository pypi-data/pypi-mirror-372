# %%
from adaone_utils import Toolpath
from pathlib import Path

# Load input file
input_file = Path(__file__).parent / "Protobuff_doubleBeads_backside.ada3dp"
toolpath = Toolpath.from_file(input_file)

# Write to output file
output_file = input_file.with_stem("roundtrip")
toolpath.to_file(output_file)

# Load output file and compare
toolpath2 = Toolpath.from_file(output_file)

# %% compare
assert toolpath.data.equals(toolpath2.data)
assert len(toolpath.parameters) == len(toolpath2.parameters)
for p1, p2 in zip(toolpath.parameters, toolpath2.parameters):
    assert p1 == p2

# %%
