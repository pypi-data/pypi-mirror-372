import polars as pl

class PyParameters:
    layer_height: float
    path_planning_strategy: int
    posi_axis1_val: float
    posi_axis2_val: float
    posi_axis1_dynamic: bool
    posi_axis2_dynamic: bool
    deposition_width: float
    deposition_rate_multiplier: float | None
    def __init__(
        self,
        layer_height: float,
        path_planning_strategy: int,
        posi_axis1_val: float,
        posi_axis2_val: float,
        posi_axis1_dynamic: bool,
        posi_axis2_dynamic: bool,
        deposition_width: float,
        deposition_rate_multiplier: float | None = None,
    ) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

def ada3dp_to_polars(filepath: str) -> tuple[pl.DataFrame, list[PyParameters]]: ...
def polars_to_ada3dp(
    df: pl.DataFrame,
    parameters: list[PyParameters],
    filepath: str,
) -> None: ...
