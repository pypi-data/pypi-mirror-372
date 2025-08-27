# %%
from adaone_utils import Toolpath
from pathlib import Path

input_file = Path(__file__).parent / "Protobuff_doubleBeads_backside.ada3dp"
# %%
# %%timeit
toolpath = Toolpath.from_file(input_file)

# %%
toolpath = Toolpath.from_file(input_file)
print(toolpath.data.head())
toolpath.data.head()
# %%
# %%timeit
toolpath.to_file(input_file.with_stem("test"))

# %%
toolpath2 = Toolpath.from_file(input_file.with_stem("test"))
print(toolpath2.data.head())

# %%
