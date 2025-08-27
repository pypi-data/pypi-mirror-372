from ._internal import ada3dp_to_polars, polars_to_ada3dp
from ._internal import PyParameters as _Parameters
from pathlib import Path
import polars as pl
from enum import Enum
from dataclasses import dataclass

__all__ = [
    "ada3dp_to_polars",
    "polars_to_polars",
    "Parameters",
    "PathPlanningStrategy",
    "TrackParameters",
]


class PathPlanningStrategy(Enum):
    PLANAR_HORIZONTAL = 0
    PLANAR_ANGLED = 1
    PLANAR_ALONG_GUIDE_CURVE = 2
    REVOLVED_SURFACE = 3
    RADIAL = 4
    NON_PLANAR_SURFACE = 5
    GEODESIC = 6
    CONICAL_FIELDS = 7
    RADIAL_360 = 8
    CLADDING = 9
    HEAT = 10
    CURVE_CONVERSION = 11
    DRILLING = 12
    SURFACE_FINISHING = 13
    CUTOUT = 14
    RASTER_SCANNING = 15
    SURFACE_SCANNING = 16
    ABANICO = 17
    PLANAR_FACING = 18
    HORIZONTAL_CLEARING = 19


class SegmentType(Enum):
    NONE = 0
    WALL_OUTER = 1
    WALL_INNER = 2
    INFILL = 3
    BRIM = 4
    TRAVEL = 5
    RAFT = 6
    START_APPROACH = 7
    END_RETRACT = 8
    PREHEAT = 9
    DEPOSITION_START_ZONE = 10
    DEPOSITION_END_ZONE = 11
    PURGE = 12
    WALL_MIDST = 13
    ENGAGE = 14
    DISENGAGE = 15
    UNKNOWN_1 = 16
    UNKNOWN_2 = 17


segment_type_enum = pl.Enum(SegmentType.__members__.keys())


@dataclass
class Parameters:
    layer_height: float
    path_planning_strategy: PathPlanningStrategy
    posi_axis1_val: float
    posi_axis2_val: float
    posi_axis1_dynamic: bool
    posi_axis2_dynamic: bool
    deposition_width: float

    def to_internal_parameters(self) -> _Parameters:
        internal_parameters = _Parameters(
            layer_height=self.layer_height,
            path_planning_strategy=self.path_planning_strategy.value,
            posi_axis1_val=self.posi_axis1_val,
            posi_axis2_val=self.posi_axis2_val,
            posi_axis1_dynamic=self.posi_axis1_dynamic,
            posi_axis2_dynamic=self.posi_axis2_dynamic,
            deposition_width=self.deposition_width,
        )
        return internal_parameters

    @classmethod
    def from_internal_parameters(cls, internal_parameters: _Parameters) -> "Parameters":
        return cls(
            layer_height=internal_parameters.layer_height,
            path_planning_strategy=PathPlanningStrategy(
                internal_parameters.path_planning_strategy
            ),
            posi_axis1_val=internal_parameters.posi_axis1_val,
            posi_axis2_val=internal_parameters.posi_axis2_val,
            posi_axis1_dynamic=internal_parameters.posi_axis1_dynamic,
            posi_axis2_dynamic=internal_parameters.posi_axis2_dynamic,
            deposition_width=internal_parameters.deposition_width,
        )


@dataclass
class TrackParameters:
    """Machine-specific track parameters for ELX calculations."""

    track_length: float = 14425  # mm
    x_0: float = -60  # mm
    y_0: float = 2000  # mm
    trailing_distance: float = 2800  # mm, approximate value derived from data


class Toolpath:
    """A class representing an AdaOne toolpath."""

    data: pl.DataFrame
    parameters: list[Parameters]

    def __init__(self, data: pl.DataFrame, parameters: Parameters | list[Parameters]):
        """
        Initialize a Toolpath object.

        Parameters:
            data (pl.DataFrame): The toolpath data
            parameters (Parameters | list[Parameters]): The toolpath parameter(s)
        """
        self.data = data
        self.parameters = (
            [parameters] if isinstance(parameters, Parameters) else parameters
        )

    @classmethod
    def from_file(cls, file_path: str | Path) -> "Toolpath":
        """
        Read a toolpath from a *.ada3dp file.

        Parameters:
            file_path (str | Path): Path to the *.ada3dp file

        Returns:
            Toolpath: A new Toolpath object
        """
        file_path = Path(file_path).resolve(strict=False)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        df: pl.DataFrame
        internal_parameters: list[_Parameters]
        df, internal_parameters = ada3dp_to_polars(str(file_path))
        # Cast segment_type to SegmentType enum
        df = df.with_columns(
            pl.col("segment_type").cast(pl.UInt32).cast(segment_type_enum)
        )
        parameters = [
            Parameters.from_internal_parameters(p) for p in internal_parameters
        ]
        return cls(df, parameters)

    def to_file(self, file_path: str | Path) -> None:
        """
        Write the toolpath to a *.ada3dp file.

        Parameters:
            file_path (str | Path): Path where to save the *.ada3dp file

        Raises:
            ValueError: If the DataFrame is missing required columns
        """
        required_columns = [
            "position.x",
            "position.y",
            "position.z",
            "direction.x",
            "direction.y",
            "direction.z",
            "orientation.x",
            "orientation.y",
            "orientation.z",
            "orientation.w",
            "deposition",
            "speed",
            "speedTCP",
            "segment_type",
            "layerIndex",
            "processOn",
            "processOnDelay",
            "processOffDelay",
            "startDelay",
            "processHeadID",
            "toolID",
            "materialID",
            "segmentID",
            "fans.num",
            "fans.speed",
            "userEvents.num",
            "externalAxes"
        ]
        optional_columns = [
              "depositionRateMultiplier",  #
        ]

        file_path = Path(file_path).resolve(strict=False)
        if not file_path.parent.exists():
            raise FileNotFoundError(f"Parent directory not found: {file_path.parent}")

        missing_columns = [
            col for col in required_columns if col not in self.data.columns
        ]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        superfluous_columns = [
            col for col in self.data.columns if col not in required_columns + optional_columns
        ]   
        if superfluous_columns:
            raise UserWarning(f"Superfluous columns wil be ignored. Found: {', '.join(superfluous_columns)}")
        
        # Convert the SegmentType enum back to integers
        df = self.data.clone()
        df = df.with_columns(pl.col("segment_type").cast(pl.UInt32).cast(pl.Int32))

        polars_to_ada3dp(
            df,
            [p.to_internal_parameters() for p in self.parameters],
            str(file_path),
        )
