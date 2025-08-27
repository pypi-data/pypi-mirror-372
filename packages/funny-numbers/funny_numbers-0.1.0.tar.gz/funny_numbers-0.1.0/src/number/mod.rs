mod list;
pub use list::CONST_FUNNY_NUMBERS_LIST;

use pyo3::prelude::*;

#[pyclass]
#[derive(Clone)]
pub struct FunnyNumber {
    #[pyo3(get)]
    pub number: f64,

    #[pyo3(get)]
    pub reason: String,
}

#[pymethods]
impl FunnyNumber {
    #[new]
    fn new(number: f64, reason: String) -> Self {
        FunnyNumber { number, reason }
    }

    fn __repr__(&self) -> String {
        format!("FunnyNumber({}, {})", self.number, self.reason)
    }
}

pub struct ConstFunnyNumber {
    pub number: f64,
    pub reason: &'static str,
}

impl From<ConstFunnyNumber> for FunnyNumber {
    fn from(cf: ConstFunnyNumber) -> Self {
        FunnyNumber {
            number: cf.number,
            reason: cf.reason.to_string(),
        }
    }
}

pub trait IntoFunnyVec {
    fn into_funny_vec(self) -> Vec<FunnyNumber>;
}

impl<const N: usize> IntoFunnyVec for [ConstFunnyNumber; N] {
    fn into_funny_vec(self) -> Vec<FunnyNumber> {
        self.into_iter().map(Into::into).collect()
    }
}
