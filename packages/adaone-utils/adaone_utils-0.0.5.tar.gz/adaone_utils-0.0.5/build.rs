
use std::io::Result;
fn main() -> Result<()> {
    prost_build::compile_protos(&["src/ada3dp.proto"], &["src/"])?;
    Ok(())
}
