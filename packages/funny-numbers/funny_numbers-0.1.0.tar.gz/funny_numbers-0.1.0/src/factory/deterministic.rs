use pyo3::prelude::*;

use crate::number::FunnyNumber;

#[pyclass]
pub struct DeterministicFunnyNumberFactory {
    #[pyo3(get)]
    funny_number: FunnyNumber,
}

#[pymethods]
impl DeterministicFunnyNumberFactory {
    #[new]
    fn new(funny_number: FunnyNumber) -> Self {
        DeterministicFunnyNumberFactory { funny_number }
    }

    fn get_one(&self) -> FunnyNumber {
        self.funny_number.clone()
    }

    fn get_many(&self, count: usize) -> Vec<FunnyNumber> {
        let mut values: Vec<FunnyNumber> = Vec::with_capacity(count);

        for _ in 0..count {
            values.push(self.funny_number.clone());
        }

        values
    }

    #[getter]
    fn min(&self) -> FunnyNumber {
        self.funny_number.clone()
    }

    #[getter]
    fn max(&self) -> FunnyNumber {
        self.funny_number.clone()
    }

    #[getter]
    fn mean(&self) -> f64 {
        self.funny_number.number
    }

    #[getter]
    fn variance(&self) -> f64 {
        0_f64
    }

    fn __len__(&self) -> usize {
        1_usize
    }

    fn __repr__(&self) -> String {
        "DeterministicFunnyNumberFactory(1)".to_string()
    }
}
