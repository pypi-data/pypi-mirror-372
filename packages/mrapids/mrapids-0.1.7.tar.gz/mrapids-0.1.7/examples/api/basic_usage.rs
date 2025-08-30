//! Basic usage example of the core API module

use mrapids::core::api::{RunRequest, ListRequest};
use std::path::PathBuf;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("MicroRapid Core API Example");
    println!("==========================\n");
    
    // Example: Create a run request
    let run_request = RunRequest {
        operation_id: "getUser".to_string(),
        parameters: None,
        body: None,
        spec_path: Some(PathBuf::from("examples/openapi.yaml")),
        env: Some("development".to_string()),
        auth_profile: Some("default".to_string()),
    };
    
    println!("Created run request:");
    println!("{:#?}", run_request);
    
    // Example: Create a list request
    let list_request = ListRequest {
        filter: None,
        spec_path: Some(PathBuf::from("examples/openapi.yaml")),
    };
    
    println!("\nCreated list request:");
    println!("{:#?}", list_request);
    
    // NOTE: Actual API execution would happen here once the implementation is complete
    println!("\n✅ API module successfully compiled and types are working!");
    
    Ok(())
}