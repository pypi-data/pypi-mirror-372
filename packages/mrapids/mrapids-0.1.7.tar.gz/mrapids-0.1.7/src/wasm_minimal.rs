use wasm_bindgen::prelude::*;
use serde::{Deserialize, Serialize};
use web_sys::console;

#[wasm_bindgen]
pub struct MicroRapidsClient {
    base_url: String,
}

#[derive(Serialize, Deserialize)]
pub struct RequestOptions {
    pub method: String,
    pub headers: Option<std::collections::HashMap<String, String>>,
    pub body: Option<String>,
}

#[wasm_bindgen]
impl MicroRapidsClient {
    #[wasm_bindgen(constructor)]
    pub fn new(base_url: String) -> MicroRapidsClient {
        console::log_1(&"MicroRapids WASM client initialized".into());
        MicroRapidsClient { base_url }
    }

    #[wasm_bindgen(js_name = healthCheck)]
    pub fn health_check(&self) -> String {
        format!("Healthy: {}", self.base_url)
    }

    #[wasm_bindgen(js_name = executeRequest)]
    pub async fn execute_request(&self, endpoint: &str, options_json: Option<String>) -> Result<String, JsValue> {
        let url = format!("{}{}", self.base_url, endpoint);
        
        let window = web_sys::window().ok_or("No window object")?;
        let resp_value = wasm_bindgen_futures::JsFuture::from(
            window.fetch_with_str(&url)
        ).await?;
        
        let resp: web_sys::Response = resp_value.dyn_into()?;
        let text = wasm_bindgen_futures::JsFuture::from(resp.text()?).await?;
        
        Ok(text.as_string().unwrap_or_default())
    }
    
    #[wasm_bindgen(getter)]
    pub fn version(&self) -> String {
        env!("CARGO_PKG_VERSION").to_string()
    }

    #[wasm_bindgen(js_name = parseOpenAPI)]
    pub fn parse_openapi(&self, spec_json: &str) -> Result<String, JsValue> {
        match serde_json::from_str::<serde_json::Value>(spec_json) {
            Ok(spec) => {
                let info = spec.get("info")
                    .and_then(|i| i.get("title"))
                    .and_then(|t| t.as_str())
                    .unwrap_or("Unknown API");
                Ok(format!("Parsed OpenAPI: {}", info))
            }
            Err(e) => Err(JsValue::from_str(&format!("Parse error: {}", e)))
        }
    }
}

#[wasm_bindgen(start)]
pub fn init() {
    console::log_1(&"MicroRapids WASM module loaded".into());
}