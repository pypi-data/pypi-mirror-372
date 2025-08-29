// WASM bindings for MicroRapids
use wasm_bindgen::prelude::*;

// When the `wee_alloc` feature is enabled, use `wee_alloc` as the global allocator.
#[cfg(feature = "wee_alloc")]
#[global_allocator]
static ALLOC: wee_alloc::WeeAlloc = wee_alloc::WeeAlloc::INIT;

#[wasm_bindgen]
pub struct MicroRapidsClient {
    base_url: String,
}

#[wasm_bindgen]
impl MicroRapidsClient {
    #[wasm_bindgen(constructor)]
    pub fn new(base_url: String) -> MicroRapidsClient {
        // Set panic hook for better error messages in browser
        #[cfg(feature = "console_error_panic_hook")]
        console_error_panic_hook::set_once();

        MicroRapidsClient { base_url }
    }

    #[wasm_bindgen(js_name = healthCheck)]
    pub fn health_check(&self) -> String {
        format!("Healthy: {}", self.base_url)
    }

    #[wasm_bindgen(js_name = executeRequest)]
    pub fn execute_request(&self, endpoint: &str, params: Option<String>) -> String {
        let params_str = params.unwrap_or_default();
        format!(
            "Request to {}{}{}",
            self.base_url,
            endpoint,
            if params_str.is_empty() { "" } else { "?" }
        )
    }

    #[wasm_bindgen(getter)]
    pub fn version(&self) -> String {
        env!("CARGO_PKG_VERSION").to_string()
    }
}

// Initialize the WASM module
#[wasm_bindgen(start)]
pub fn init() {
    // Set up any initialization here
}
