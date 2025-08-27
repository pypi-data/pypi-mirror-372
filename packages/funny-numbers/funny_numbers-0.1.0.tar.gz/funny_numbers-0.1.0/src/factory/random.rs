use pyo3::{exceptions::PyValueError, prelude::*};
use rand::{prelude::IndexedRandom, rngs::StdRng, SeedableRng};
use std::sync::Mutex;

use crate::number::{FunnyNumber, IntoFunnyVec, CONST_FUNNY_NUMBERS_LIST};

#[pyclass]
pub struct RandomFunnyNumberFactory {
    #[pyo3(get)]
    funny_numbers: Vec<FunnyNumber>,

    #[pyo3(get)]
    max: FunnyNumber,

    #[pyo3(get)]
    min: FunnyNumber,

    #[pyo3(get)]
    mean: f64,

    #[pyo3(get)]
    variance: f64,

    rng: Mutex<StdRng>,
}

#[pymethods]
impl RandomFunnyNumberFactory {
    #[new]
    #[pyo3(signature = (funny_numbers=None))]
    fn new(funny_numbers: Option<Vec<FunnyNumber>>) -> PyResult<Self> {
        let funny_numbers = match funny_numbers {
            Some(nums) => nums,
            None => CONST_FUNNY_NUMBERS_LIST.into_funny_vec(),
        };

        if funny_numbers.is_empty() {
            return Err(PyErr::new::<PyValueError, _>(
                "funny_numbers cannot be empty",
            ));
        }

        let min = funny_numbers
            .iter()
            .min_by(|a, b| a.number.partial_cmp(&b.number).unwrap())
            .unwrap()
            .clone();

        let max = funny_numbers
            .iter()
            .max_by(|a, b| a.number.partial_cmp(&b.number).unwrap())
            .unwrap()
            .clone();

        let mean = funny_numbers.iter().map(|f| f.number).sum::<f64>() / funny_numbers.len() as f64;

        let variance = funny_numbers
            .iter()
            .map(|f| {
                let diff = f.number - mean;
                diff * diff
            })
            .sum::<f64>()
            / funny_numbers.len() as f64;

        Ok(RandomFunnyNumberFactory {
            funny_numbers,
            rng: Mutex::new(StdRng::from_rng(&mut rand::rng())),
            min,
            max,
            mean,
            variance,
        })
    }

    fn get_one(&self) -> PyResult<FunnyNumber> {
        let mut rng = self.rng.lock().unwrap();

        self.funny_numbers.choose(&mut rng).cloned().ok_or_else(|| {
            PyErr::new::<PyValueError, _>("No funny numbers available in the factory")
        })
    }

    fn get_many(&self, count: usize) -> PyResult<Vec<FunnyNumber>> {
        if self.funny_numbers.is_empty() {
            return Err(PyErr::new::<PyValueError, _>(
                "No funny numbers available in the factory",
            ));
        }

        let mut rng = self.rng.lock().unwrap();
        let values = (0..count)
            .map(|_| self.funny_numbers.choose(&mut rng).cloned().unwrap())
            .collect();

        Ok(values)
    }

    fn get_many_unique(&self, count: usize) -> PyResult<Vec<FunnyNumber>> {
        if count > self.funny_numbers.len() {
            return Err(PyErr::new::<PyValueError, _>(
                "Not enough funny numbers available in the factory",
            ));
        }

        if self.funny_numbers.is_empty() {
            return Err(PyErr::new::<PyValueError, _>(
                "No funny numbers available in the factory",
            ));
        }

        let mut rng = self.rng.lock().unwrap();
        let values = self
            .funny_numbers
            .choose_multiple(&mut rng, count)
            .cloned()
            .collect();

        Ok(values)
    }

    fn __len__(&self) -> usize {
        self.funny_numbers.len()
    }

    fn __repr__(&self) -> String {
        format!("RandomFunnyNumberFactory({})", self.funny_numbers.len())
    }
}
