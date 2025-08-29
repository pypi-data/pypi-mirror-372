// Python bindings using PyO3
use pyo3::prelude::*;
use pyo3::types::PyDict;

#[pyclass]
struct MicroRapidsClient {
    base_url: String,
}

#[pymethods]
impl MicroRapidsClient {
    #[new]
    fn new(base_url: String) -> Self {
        MicroRapidsClient { base_url }
    }

    fn health_check(&self) -> PyResult<String> {
        Ok(format!("Healthy: {}", self.base_url))
    }

    fn execute(&self, endpoint: &str, params: Option<&Bound<'_, PyDict>>) -> PyResult<String> {
        // Convert Python dict to Rust types if needed
        let mut query = String::new();
        if let Some(p) = params {
            for (key, value) in p.iter() {
                let k: String = key.extract()?;
                let v: String = value.extract()?;
                query.push_str(&format!("{}={}&", k, v));
            }
        }

        Ok(format!("Request: {}{}", self.base_url, endpoint))
    }

    fn __repr__(&self) -> String {
        format!("MicroRapidsClient('{}')", self.base_url)
    }
}

/// Python module definition
#[pymodule]
fn mrapids(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<MicroRapidsClient>()?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}

#[pyfunction]
fn version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}
