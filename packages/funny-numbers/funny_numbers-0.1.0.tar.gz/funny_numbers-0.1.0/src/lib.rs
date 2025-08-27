mod factory;
mod number;

use pyo3::prelude::*;

use crate::{
    factory::{DeterministicFunnyNumberFactory, RandomFunnyNumberFactory},
    number::FunnyNumber,
};

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<FunnyNumber>()?;
    m.add_class::<DeterministicFunnyNumberFactory>()?;
    m.add_class::<RandomFunnyNumberFactory>()?;
    Ok(())
}
