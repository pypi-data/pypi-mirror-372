# %% imports
import polars as pl
import numpy as np
from scipy.interpolate import interp1d
import plotly.express as px
from pathlib import Path
from adaone_utils import Toolpath


input_file = Path(__file__).parent / "Protobuff_doubleBeads_backside.ada3dp"
toolpath = Toolpath.from_file(input_file)
df = toolpath.data
df.head()

df = df.with_columns(pl.col("externalAxes").list.get(0).alias("externalAxes_first"))
first_row = df.head(1)

# Drop unnecessary columns for analysis
df = df.drop(
    [
        "direction.x",
        "direction.y",
        "direction.z",
        "orientation.x",
        "orientation.y",
        "orientation.z",
        "orientation.w",
        "fans.num",
        "fans.speed",
        "userEvents.num",
        "externalAxes",
    ]
)

# %% Compute distance and duration

df = df.with_columns(
    pl.sum_horizontal(
        [
            (pl.col(col) - pl.col(col).shift(1)).cast(pl.Float64).pow(2)
            for col in ["position.x", "position.y", "position.z"]
        ]
    )
    .sqrt()
    .alias("length")
)

df = df.with_columns((pl.col("length") / pl.col("speed")).alias("duration"))
df.head()

# layer length plot
df.group_by("layerIndex", maintain_order=True).agg(
    pl.col("length").sum().alias("total_length"),
    pl.col("duration").sum().alias("total_duration"),
).plot.line("layerIndex", "total_length")

for seg in df.filter(df["layerIndex"] == df["layerIndex"].min()).partition_by(
    "segmentID"
):
    seg.plot.line("time", "length")

px.line_3d(
    df.filter(df["layerIndex"] == df["layerIndex"].min()),
    x="position.x",
    y="position.y",
    z="position.z",
    color="segment_type",
    line_group="segmentID",
    hover_name="segmentID",
)

df = df.with_columns(
    pl.col("length").cum_sum().alias("total_length"),
    pl.col("duration").cum_sum().alias("total_duration"),
)

data = df.filter((df["segmentID"] == 1)).to_numpy()


def resample_points(df: pl.DataFrame, step: float = 5.0) -> pl.DataFrame:
    # Get min and max as floats - use item() to get scalar values
    min_len = float(df["total_length"].min())  # type: ignore
    max_len = float(df["total_length"].max())  # type: ignore
    # Define the new total_length values at uniform 5mm intervals
    new_total_len = np.linspace(
        min_len,
        max_len,
        int((max_len - min_len) / step) + 2,
    )

    # Convert to Pandas for interpolation
    df_pd = df.to_pandas()

    # Interpolation functions for all numeric columns
    interp_funcs = {
        col: interp1d(
            df_pd["total_length"], df_pd[col], kind="linear", fill_value="extrapolate"
        )
        for col in df_pd.select_dtypes(include=[np.float64]).columns
        if col != "total_length"
    }

    # Compute new values for all columns
    new_data = {col: interp_funcs[col](new_total_len) for col in interp_funcs}
    new_data["total_length"] = new_total_len

    # now smooth the x/y/z/ values using moving average
    window_size = 5
    for coord in ["x", "y", "z"]:
        pos = new_data[f"position.{coord}"]
        pos[2:-2] = np.convolve(pos, np.ones(window_size) / window_size, mode="valid")
        new_data[f"position.{coord}"] = pos

    copy_first_value_for_columns = [
        "speedTCP",
        "segment_type",
        "layerIndex",
        "processOnDelay",
        "processOffDelay",
        "startDelay",
        "processHeadID",
        "toolID",
        "materialID",
        "segmentID",
    ]

    for col in copy_first_value_for_columns:
        new_data[col] = df_pd[col].iloc[0]

    # sort columns to match the original dataframe
    new_data = {k: new_data[k] for k in df_pd.columns}

    # Create a new Polars DataFrame with resampled points
    new_df = pl.DataFrame(new_data)

    return new_df


# %% Apply resampling for wall segments
segments = []
for seg in df.filter((df["segmentID"] < 20)).partition_by("segmentID"):
    if seg["segment_type"].first() == "WALL_OUTER":
        segments.append(resample_points(seg, step=4.0))
    elif seg["segment_type"].first() == "WALL_INNER":
        segments.append(resample_points(seg, step=10.0))
    else:
        segments.append(seg)

resampled_df = pl.concat(segments)
print(resampled_df)

px.line_3d(
    resampled_df,
    x="position.x",
    y="position.y",
    z="position.z",
    color="segment_type",
    line_group="segmentID",
    hover_name="segmentID",
)

# add all the columns in the original df to the resampled dataframe
for col_name in set(first_row.columns) - set(resampled_df.columns):
    resampled_df = resampled_df.with_columns(
        pl.lit(first_row[col_name].first())
        .cast(first_row[col_name].dtype)
        .alias(col_name)
    )
# now copy the value from resampled_df["externalAxes_first"] intonthe first position of the list externalAxes (list[f64])

# set the first value of externalAxes to the value of externalAxes_first
resampled_df = resampled_df.with_columns(
    pl.struct(["externalAxes", "externalAxes_first"])
    .map_elements(
        lambda s: [s["externalAxes_first"]] + s["externalAxes"][1:]
        if len(s["externalAxes"]) > 0
        else [s["externalAxes_first"]],
        return_dtype=pl.List(pl.Float64),
    )
    .alias("externalAxes")
)

# %% Create a new toolpath with the resampled data and original parameters
resampled_toolpath = Toolpath(data=resampled_df, parameters=toolpath.parameters)
resampled_toolpath.to_file(input_file.with_stem("resampled"))

# %%
