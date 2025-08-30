//! Example demonstrating API and Policy integration

use mrapids::core::api::{run_operation, RunRequest};
use mrapids::core::parser::parse_spec;
use mrapids::core::policy::{
    explain_decision, load_policy_from_file, EvaluationContext, PolicyEngine, PolicyExplanation,
    PolicySet,
};
use std::path::PathBuf;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("MicroRapid Policy Integration Example");
    println!("=====================================\n");

    // Load policy from file
    let policy_path = PathBuf::from("examples/.mrapids/policy.yaml");
    let policy = load_policy_from_file(&policy_path)?;

    println!(
        "Loaded policy: {}",
        policy
            .metadata
            .as_ref()
            .map(|m| m.name.as_str())
            .unwrap_or("Unnamed")
    );

    // Create policy engine
    let engine = PolicyEngine::new(policy.clone())?;

    // Example 1: Allowed operation
    println!("\n--- Example 1: Allowed Operation ---");
    test_operation(
        &engine,
        "getUser",
        "api.public.com/users/123",
        Some("default"),
        "GET",
        &policy,
    );

    // Example 2: Denied operation (wrong method)
    println!("\n--- Example 2: Denied Operation (Wrong Method) ---");
    test_operation(
        &engine,
        "createUser",
        "api.public.com/users",
        Some("default"),
        "POST",
        &policy,
    );

    // Example 3: Denied operation (no auth)
    println!("\n--- Example 3: Denied Operation (No Auth) ---");
    test_operation(
        &engine,
        "getUser",
        "api.public.com/users/123",
        None,
        "GET",
        &policy,
    );

    // Example 4: Blocked payment operation
    println!("\n--- Example 4: Blocked Payment Operation ---");
    test_operation(
        &engine,
        "processPayment",
        "api.example.com/payment/process",
        Some("default"),
        "POST",
        &policy,
    );

    // Example 5: GitHub operation with proper auth
    println!("\n--- Example 5: GitHub Operation ---");
    test_operation(
        &engine,
        "listRepos",
        "api.github.com/users/octocat/repos",
        Some("github-readonly"),
        "GET",
        &policy,
    );

    Ok(())
}

fn test_operation(
    engine: &PolicyEngine,
    operation_id: &str,
    url: &str,
    auth_profile: Option<&str>,
    method: &str,
    policy: &PolicySet,
) {
    // Create request
    let request = RunRequest {
        operation_id: operation_id.to_string(),
        auth_profile: auth_profile.map(|s| s.to_string()),
        parameters: None,
        body: None,
        spec_path: None,
        env: None,
    };

    // Create evaluation context
    let context = EvaluationContext {
        method: Some(method.to_string()),
        tags: None,
        source_ip: None,
        timestamp: chrono::Utc::now(),
    };

    // Evaluate policy
    let decision = engine.evaluate(&request, url, &context);

    // Get explanation
    let explanation = explain_decision(&decision, &request, url, &context, Some(policy));

    // Print results
    println!("Operation: {} ({})", operation_id, method);
    println!("URL: {}", url);
    println!("Auth: {}", auth_profile.unwrap_or("none"));
    println!("{}", explanation);

    // In a real implementation, you would proceed with the API call if allowed
    if decision.is_allowed() {
        println!("→ Would proceed with API call");
    } else {
        println!("→ API call blocked by policy");
    }
}

// Helper function to demonstrate full integration
async fn execute_with_policy(
    request: RunRequest,
    spec_content: &str,
    policy: PolicySet,
) -> Result<String, Box<dyn std::error::Error>> {
    // Parse the OpenAPI spec
    let spec = parse_spec(spec_content)?;

    // Create policy engine
    let engine = PolicyEngine::new(policy)?;

    // Build URL (simplified)
    let operation = spec
        .operations
        .iter()
        .find(|op| op.operation_id == request.operation_id)
        .ok_or("Operation not found")?;

    let url = format!("{}{}", spec.base_url, operation.path);

    // Create evaluation context
    let context = EvaluationContext {
        method: Some(operation.method.clone()),
        tags: None,
        source_ip: None,
        timestamp: chrono::Utc::now(),
    };

    // Evaluate policy
    let decision = engine.evaluate(&request, &url, &context);

    if !decision.is_allowed() {
        let explanation = explain_decision(&decision, &request, &url, &context, None);
        return Err(format!("Policy denied: {}", explanation.summary).into());
    }

    // If allowed, proceed with the API call
    // Note: This would use the actual implementation once complete
    let _response = run_operation(request, &spec, None).await?;

    Ok("Operation completed successfully".to_string())
}
