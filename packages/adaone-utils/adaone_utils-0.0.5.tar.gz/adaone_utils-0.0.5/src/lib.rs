use ada3dp::{
    EventData, FanData, Parameters, PathSegment, Point, Quaternion, ToolPathData, ToolPathGroup,
    Vector3D,
};
use polars::prelude::*;
use prost::Message;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3_polars::PyDataFrame;
use smallvec::SmallVec;
use std::error::Error;
use std::fs::File;
use std::io::{BufReader, Cursor, Read, Write};
use std::vec;
pub mod ada3dp {
    include!(concat!(env!("OUT_DIR"), "/ada3_dp.rs"));
}

#[pyclass]
#[derive(Clone, PartialEq)]
struct PyParameters {
    #[pyo3(get, set)]
    layer_height: f64,
    #[pyo3(get, set)]
    path_planning_strategy: i32,
    #[pyo3(get, set)]
    posi_axis1_val: f64,
    #[pyo3(get, set)]
    posi_axis2_val: f64,
    #[pyo3(get, set)]
    posi_axis1_dynamic: bool,
    #[pyo3(get, set)]
    posi_axis2_dynamic: bool,
    #[pyo3(get, set)]
    deposition_width: f64,
}

#[pymethods]
impl PyParameters {
    #[new]
    #[pyo3(
        text_signature = "(layer_height, path_planning_strategy, posi_axis1_val, posi_axis2_val, posi_axis1_dynamic, posi_axis2_dynamic, deposition_width)"
    )]
    fn new(
        layer_height: f64,
        path_planning_strategy: i32,
        posi_axis1_val: f64,
        posi_axis2_val: f64,
        posi_axis1_dynamic: bool,
        posi_axis2_dynamic: bool,
        deposition_width: f64,
    ) -> Self {
        PyParameters {
            layer_height,
            path_planning_strategy,
            posi_axis1_val,
            posi_axis2_val,
            posi_axis1_dynamic,
            posi_axis2_dynamic,
            deposition_width,
        }
    }

    fn __str__(&self) -> String {
        format!(
            "PyParameters(layer_height={}, path_planning_strategy={}, posi_axis1_val={}, posi_axis2_val={}, posi_axis1_dynamic={}, posi_axis2_dynamic={}, deposition_width={})",
            self.layer_height,
            self.path_planning_strategy,
            self.posi_axis1_val,
            self.posi_axis2_val,
            self.posi_axis1_dynamic,
            self.posi_axis2_dynamic,
            self.deposition_width
        )
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }
}

// Utility function to handle missing `Vector3D`
fn extract_vector3d(v: Option<&Vector3D>) -> (f64, f64, f64) {
    match v {
        Some(vec) => (vec.x, vec.y, vec.z),
        None => (f64::NAN, f64::NAN, f64::NAN),
    }
}

// Utility function to handle missing `Quaternion`
fn extract_quaternion(q: Option<&Quaternion>) -> (f64, f64, f64, f64) {
    match q {
        Some(ori) => (ori.x, ori.y, ori.z, ori.w),
        None => (f64::NAN, f64::NAN, f64::NAN, f64::NAN),
    }
}

// Extract FanData as (Vec<i32>, Vec<i32>)
fn extract_fans_data(fans: &[FanData]) -> (Vec<i32>, Vec<i32>) {
    fans.iter().map(|fan| (fan.num, fan.speed)).unzip()
}

// Extract User Events as Vec<i32>
fn extract_user_events(events: &[EventData]) -> Vec<i32> {
    events.iter().map(|event| event.num).collect()
}

fn _ada3dp_to_polars(file_path: &str) -> Result<(DataFrame, Vec<PyParameters>), Box<dyn Error>> {
    let file = File::open(file_path)?;
    let mut reader = BufReader::new(file);
    let mut buf = Vec::new();
    reader.read_to_end(&mut buf)?;

    let tool_path_data = ToolPathData::decode(&mut Cursor::new(&buf))?;

    let mut pos_x = Vec::new();
    let mut pos_y = Vec::new();
    let mut pos_z = Vec::new();
    let mut dir_x = Vec::new();
    let mut dir_y = Vec::new();
    let mut dir_z = Vec::new();
    let mut ori_x = Vec::new();
    let mut ori_y = Vec::new();
    let mut ori_z = Vec::new();
    let mut ori_w = Vec::new();
    let mut external_axes = Vec::new();
    let mut deposition = Vec::new();
    let mut speed = Vec::new();
    let mut fans_num = Vec::new();
    let mut fans_speed = Vec::new();
    let mut user_events = Vec::new();
    let mut speed_tcp = Vec::new();
    let mut segment_type = Vec::new();
    let mut layer_index = Vec::new();
    let mut process_on_delay = Vec::new();
    let mut process_off_delay = Vec::new();
    let mut start_delay = Vec::new();
    let mut process_head_id = Vec::new();
    let mut tool_id = Vec::new();
    let mut material_id = Vec::new();
    let mut segment_id = Vec::new();
    let mut process_on = Vec::new();
    let mut deposition_rate_multiplier = Vec::new();

    let mut segment_counter = 0;

    for group in tool_path_data.tool_path_groups.iter() {
        for segment in &group.path_segments {
            for point in &segment.points {
                let (px, py, pz) = extract_vector3d(point.position.as_ref());
                let (dx, dy, dz) = extract_vector3d(point.direction.as_ref());
                let (ox, oy, oz, ow) = extract_quaternion(point.orientation.as_ref());

                pos_x.push(px);
                pos_y.push(py);
                pos_z.push(pz);
                dir_x.push(dx);
                dir_y.push(dy);
                dir_z.push(dz);
                ori_x.push(ox);
                ori_y.push(oy);
                ori_z.push(oz);
                ori_w.push(ow);

                external_axes.push(SmallVec::<[f64; 10]>::from_slice(&point.external_axes));
                deposition.push(point.deposition);
                speed.push(point.speed);

                let (fan_nums, fan_speeds) = extract_fans_data(&point.fans);
                fans_num.push(fan_nums);
                fans_speed.push(fan_speeds);

                user_events.push(extract_user_events(&point.user_events));

                speed_tcp.push(segment.speed_tcp);
                segment_type.push(segment.r#type);
                layer_index.push(group.layer_index);
                process_on_delay.push(segment.process_on_delay);
                process_off_delay.push(segment.process_off_delay);
                start_delay.push(segment.start_delay);
                process_head_id.push(segment.process_head_id);
                tool_id.push(segment.tool_id);
                material_id.push(segment.material_id);
                segment_id.push(segment_counter);
                process_on.push(segment.process_on);
                deposition_rate_multiplier
                    .push(point.deposition_rate_multiplier.unwrap_or(f64::NAN));
            }
            segment_counter += 1;
        }
    }

    let mut columns = vec![
        Series::new("position.x".into(), pos_x).into(),
        Series::new("position.y".into(), pos_y).into(),
        Series::new("position.z".into(), pos_z).into(),
        Series::new("direction.x".into(), dir_x).into(),
        Series::new("direction.y".into(), dir_y).into(),
        Series::new("direction.z".into(), dir_z).into(),
        Series::new("orientation.x".into(), ori_x).into(),
        Series::new("orientation.y".into(), ori_y).into(),
        Series::new("orientation.z".into(), ori_z).into(),
        Series::new("orientation.w".into(), ori_w).into(),
        Series::new("deposition".into(), deposition).into(),
        Series::new("speed".into(), speed).into(),
        Series::new("speedTCP".into(), speed_tcp).into(),
        Series::new("segment_type".into(), segment_type).into(),
        Series::new("layerIndex".into(), layer_index).into(),
        Series::new("processOnDelay".into(), process_on_delay).into(),
        Series::new("processOffDelay".into(), process_off_delay).into(),
        Series::new("startDelay".into(), start_delay).into(),
        Series::new("processHeadID".into(), process_head_id).into(),
        Series::new("toolID".into(), tool_id).into(),
        Series::new("materialID".into(), material_id).into(),
        Series::new("segmentID".into(), segment_id).into(),
        Series::new("processOn".into(), process_on).into(),
        Series::new(
            "fans.num".into(),
            ListChunked::from_iter(fans_num.into_iter().map(|v| Series::new("".into(), v))),
        )
        .into(),
        Series::new(
            "fans.speed".into(),
            ListChunked::from_iter(fans_speed.into_iter().map(|v| Series::new("".into(), v))),
        )
        .into(),
        Series::new(
            "userEvents.num".into(),
            ListChunked::from_iter(user_events.into_iter().map(|v| Series::new("".into(), v))),
        )
        .into(),
        Series::new(
            "externalAxes".into(),
            ListChunked::from_iter(external_axes.into_iter().map(|v| Series::new("".into(), v))),
        )
        .into(),
    ];
    // Add depositionRateMultiplier only if it contains non-NaN values

    if !deposition_rate_multiplier.iter().all(|&v| v.is_nan()) {
        columns.push(
            Series::new(
                "depositionRateMultiplier".into(),
                deposition_rate_multiplier,
            )
            .into(),
        );
    }

    let df = DataFrame::new(columns)?;

    let parameters: Vec<PyParameters> = tool_path_data
        .parameters
        .iter()
        .map(|params| PyParameters {
            layer_height: params.layer_height,
            deposition_width: params.deposition_width,
            posi_axis1_val: params.posi_axis1_val,
            posi_axis2_val: params.posi_axis2_val,
            posi_axis1_dynamic: params.posi_axis1_dynamic,
            posi_axis2_dynamic: params.posi_axis2_dynamic,
            path_planning_strategy: params.path_planning_strategy,
        })
        .collect();

    // If no parameters were found, provide a default one
    let parameters = if parameters.is_empty() {
        vec![PyParameters {
            layer_height: 0.0,
            deposition_width: 0.0,
            posi_axis1_val: 0.0,
            posi_axis2_val: 0.0,
            posi_axis1_dynamic: false,
            posi_axis2_dynamic: false,
            path_planning_strategy: 0,
        }]
    } else {
        parameters
    };

    Ok((df, parameters))
}

/// Converts the result of _ada3dp_to_polars into a Python DataFrame, mapping any errors to PyValueError
#[pyfunction(signature = (file_path))]
fn ada3dp_to_polars(file_path: &str) -> PyResult<(PyDataFrame, Vec<PyParameters>)> {
    _ada3dp_to_polars(file_path)
        .map_err(|e| {
            PyErr::new::<PyValueError, _>(format!("Error converting to Polars DataFrame: {}", e))
        })
        .map(|(df, params)| (PyDataFrame(df), params))
}

fn _polars_to_ada3dp(
    df: DataFrame,
    parameters: Vec<PyParameters>,
) -> Result<Vec<u8>, Box<dyn Error>> {
    let mut tool_path_data = ToolPathData {
        tool_path_groups: Vec::new(),
        parameters: parameters
            .into_iter()
            .map(|p| Parameters {
                layer_height: p.layer_height,
                deposition_width: p.deposition_width,
                posi_axis1_val: p.posi_axis1_val,
                posi_axis2_val: p.posi_axis2_val,
                posi_axis1_dynamic: p.posi_axis1_dynamic,
                posi_axis2_dynamic: p.posi_axis2_dynamic,
                path_planning_strategy: p.path_planning_strategy,
            })
            .collect(),
    };

    let has_deposition_rate_multiplier = df
        .get_column_names()
        .iter()
        .any(|&col| col == "depositionRateMultiplier");
    // Ensure the "layerIndex" column exists
    if !df.get_column_names().iter().any(|&col| col == "layerIndex") {
        return Err(Box::new(PolarsError::ColumnNotFound(
            "layerIndex column not found".into(),
        )));
    }

    let grouped_layers = df.partition_by_stable(["layerIndex"], true)?;
    for layer_df in grouped_layers {
        let layer_index = layer_df.column("layerIndex")?.i32()?.get(0).unwrap_or(0);

        let mut group = ToolPathGroup {
            layer_index,
            path_segments: Vec::new(),
        };

        let grouped_segments = layer_df.partition_by_stable(["segmentID"], false)?;
        for segment_df in grouped_segments {
            let mut path_segment = PathSegment {
                points: Vec::new(),
                process_on: segment_df
                    .column("processOn")?
                    .bool()?
                    .get(0)
                    .unwrap_or(false),
                r#type: segment_df
                    .column("segment_type")?
                    .i32()?
                    .get(0)
                    .unwrap_or(0),
                process_on_delay: segment_df
                    .column("processOnDelay")?
                    .f32()?
                    .get(0)
                    .unwrap_or(0.0),
                process_off_delay: segment_df
                    .column("processOffDelay")?
                    .f32()?
                    .get(0)
                    .unwrap_or(0.0),
                start_delay: segment_df
                    .column("startDelay")?
                    .f32()?
                    .get(0)
                    .unwrap_or(0.0),
                end_delay: 0.0,
                speed_tcp: segment_df.column("speedTCP")?.i32()?.get(0).unwrap_or(0),
                process_head_id: segment_df
                    .column("processHeadID")?
                    .i32()?
                    .get(0)
                    .unwrap_or(0),
                tool_id: segment_df.column("toolID")?.i32()?.get(0).unwrap_or(0),
                material_id: segment_df.column("materialID")?.i32()?.get(0).unwrap_or(0),
                deposition_rate_multiplier: if has_deposition_rate_multiplier {
                    segment_df.column("depositionRateMultiplier")?.f64()?.get(0)
                } else {
                    None
                },
            };

            let mut columns = vec![
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
            ];

            // add "depositionRateMultiplier" if it exists
            if has_deposition_rate_multiplier {
                columns.push("depositionRateMultiplier")
            }
            // handling the list[Float64] column is a pain. So we collect it first into a simple Vec<Vec<f64>>
            let list_column = segment_df.column("externalAxes")?;
            let chunked_array = list_column.list()?;
            let collected_data: Vec<Vec<f64>> = chunked_array
                .into_iter()
                .map(|opt_list| {
                    opt_list
                        .map(|list| {
                            list.f64()
                                .unwrap()
                                .into_iter()
                                .map(|opt_f| opt_f.unwrap_or(0.0))
                                .collect()
                        })
                        .unwrap_or_else(Vec::new)
                })
                .collect();

            let mut iters = columns
                .iter()
                .map(|&col| segment_df.column(col)?.f64().map(|s| s.into_iter()))
                .collect::<Result<Vec<_>, PolarsError>>()?;

            // Collect fan data
            let fans_num_column = segment_df.column("fans.num")?.list()?;
            let fans_speed_column = segment_df.column("fans.speed")?.list()?;
            let fans_num_data: Vec<Vec<i32>> = fans_num_column
                .into_iter()
                .map(|opt_list| {
                    opt_list
                        .map(|list| {
                            list.i32()
                                .unwrap()
                                .into_iter()
                                .map(|opt_i| opt_i.unwrap_or(0))
                                .collect()
                        })
                        .unwrap_or_else(Vec::new)
                })
                .collect();
            let fans_speed_data: Vec<Vec<i32>> = fans_speed_column
                .into_iter()
                .map(|opt_list| {
                    opt_list
                        .map(|list| {
                            list.i32()
                                .unwrap()
                                .into_iter()
                                .map(|opt_i| opt_i.unwrap_or(0))
                                .collect()
                        })
                        .unwrap_or_else(Vec::new)
                })
                .collect();

            // Collect user event data
            let user_events_column = segment_df.column("userEvents.num")?.list()?;
            let user_events_data: Vec<Vec<i32>> = user_events_column
                .into_iter()
                .map(|opt_list| {
                    opt_list
                        .map(|list| {
                            list.i32()
                                .unwrap()
                                .into_iter()
                                .map(|opt_i| opt_i.unwrap_or(0))
                                .collect()
                        })
                        .unwrap_or_else(Vec::new)
                })
                .collect();

            for i in 0..segment_df.height() {
                let point = Point {
                    position: Some(Vector3D {
                        x: iters[0].next().flatten().unwrap_or(f64::NAN),
                        y: iters[1].next().flatten().unwrap_or(f64::NAN),
                        z: iters[2].next().flatten().unwrap_or(f64::NAN),
                    }),
                    direction: Some(Vector3D {
                        x: iters[3].next().flatten().unwrap_or(f64::NAN),
                        y: iters[4].next().flatten().unwrap_or(f64::NAN),
                        z: iters[5].next().flatten().unwrap_or(f64::NAN),
                    }),
                    orientation: Some(Quaternion {
                        x: iters[6].next().flatten().unwrap_or(f64::NAN),
                        y: iters[7].next().flatten().unwrap_or(f64::NAN),
                        z: iters[8].next().flatten().unwrap_or(f64::NAN),
                        w: iters[9].next().flatten().unwrap_or(f64::NAN),
                    }),
                    deposition: iters[10].next().flatten().unwrap_or(f64::NAN),
                    speed: iters[11].next().flatten().unwrap_or(f64::NAN),
                    external_axes: collected_data[i].clone(),
                    fans: fans_num_data[i]
                        .iter()
                        .zip(&fans_speed_data[i])
                        .map(|(&num, &speed)| FanData { num, speed })
                        .collect(),
                    user_events: user_events_data[i]
                        .iter()
                        .map(|&num| EventData { num })
                        .collect(),
                    deposition_rate_multiplier: if has_deposition_rate_multiplier {
                        iters[12].next().flatten()
                    } else {
                        None
                    },
                };

                path_segment.points.push(point);
            }

            group.path_segments.push(path_segment);
        }

        tool_path_data.tool_path_groups.push(group);
    }

    let mut buf = Vec::new();
    tool_path_data.encode(&mut buf)?;
    Ok(buf)
}

#[pyfunction]
fn polars_to_ada3dp(
    df: PyDataFrame,
    parameters: Vec<PyParameters>,
    file_path: &str,
) -> PyResult<()> {
    let df: DataFrame = df.into();
    let serialized_data = _polars_to_ada3dp(df, parameters).map_err(|e| {
        PyErr::new::<PyValueError, _>(format!(
            "Error converting Polars DataFrame to ToolPathData: {}",
            e
        ))
    })?;

    let mut file = File::create(file_path).map_err(|e| {
        PyErr::new::<PyValueError, _>(format!("Error creating file {}: {}", file_path, e))
    })?;
    file.write_all(&serialized_data).map_err(|e| {
        PyErr::new::<PyValueError, _>(format!("Error writing to file {}: {}", file_path, e))
    })?;

    Ok(())
}

#[pymodule(name = "_internal")]
fn adaone_utils(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(ada3dp_to_polars, m)?)?;
    m.add_function(wrap_pyfunction!(polars_to_ada3dp, m)?)?;
    m.add_class::<PyParameters>()?;
    Ok(())
}
