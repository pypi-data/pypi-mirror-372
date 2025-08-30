//! Collection executor that runs requests

use super::{
    condition::ConditionEvaluator,
    context::ExecutionContext,
    dependency::DependencyGraph,
    models::{Collection, CollectionRequest, CollectionSummary, RequestResult},
    reporter::Reporter,
};
use crate::core::{
    api::{run_operation, RunRequest},
    auth::AuthProfile,
    parser::UnifiedSpec,
};
use anyhow::{Context, Result};
use serde_json::Value;
use std::collections::{HashMap, HashSet};
use std::path::PathBuf;
use std::time::Instant;

/// Options for collection execution
#[derive(Debug, Clone, Default)]
pub struct ExecutionOptions {
    /// Continue execution even if a request fails
    pub continue_on_error: bool,

    /// Skip specific requests by name
    pub skip_requests: Vec<String>,

    /// Only run specific requests by name
    pub only_requests: Option<Vec<String>>,

    /// Override authentication profile
    pub auth_profile: Option<String>,

    /// Override variables
    pub variable_overrides: HashMap<String, Value>,

    /// Use environment variables
    pub use_env: bool,

    /// Path to .env file
    pub env_file: Option<PathBuf>,

    /// Save all responses to directory
    pub save_all: Option<PathBuf>,

    /// Save summary to file
    pub save_summary: Option<PathBuf>,
}

/// Simple response wrapper for collections
#[derive(Debug, Clone)]
pub struct ApiResponse {
    pub status_code: u16,
    pub body: Option<Value>,
    pub headers: http::HeaderMap,
}

/// Execution state for tracking request results
struct ExecutionState {
    /// Completed request names
    completed: HashSet<String>,

    /// Failed request names
    failed: HashSet<String>,

    /// Results by request name
    results: HashMap<String, RequestResult>,

    /// Whether a critical failure occurred
    critical_failure: bool,
}

/// Executor for running collections
pub struct CollectionExecutor {
    spec: UnifiedSpec,
    default_auth: Option<AuthProfile>,
}

impl CollectionExecutor {
    /// Create a new executor with API spec
    pub fn new(spec: UnifiedSpec, default_auth: Option<AuthProfile>) -> Self {
        Self { spec, default_auth }
    }

    /// Execute a collection with dependency resolution and conditional execution
    pub async fn execute_with_dependencies(
        &self,
        collection: &Collection,
        options: ExecutionOptions,
        reporter: &mut dyn Reporter,
    ) -> Result<CollectionSummary> {
        // Initialize execution context and state
        let mut context = self.create_context(collection, &options)?;
        let mut state = ExecutionState {
            completed: HashSet::new(),
            failed: HashSet::new(),
            results: HashMap::new(),
            critical_failure: false,
        };

        // Build dependency graph
        let filtered_requests = self.filter_requests(collection, &options);
        let owned_requests: Vec<CollectionRequest> =
            filtered_requests.iter().map(|r| (*r).clone()).collect();
        let dependency_graph = DependencyGraph::build(&owned_requests)?;
        let execution_groups = dependency_graph.get_parallel_groups();

        // Start execution
        reporter.on_start(&collection.name, filtered_requests.len());
        let start_time = Instant::now();

        // Execute requests in dependency order
        for group in execution_groups {
            // Check for critical failure
            if state.critical_failure && !self.should_run_always(&group, &owned_requests) {
                break;
            }

            // Execute requests in the group (could be parallel in future)
            for request_name in group {
                let request = owned_requests
                    .iter()
                    .find(|r| r.name == request_name)
                    .unwrap();

                // Check if should execute
                if !self
                    .should_execute_request(request, &state, &context, &options)
                    .await?
                {
                    continue;
                }

                // Execute with retry logic
                let result = self
                    .execute_request_with_retry(
                        request,
                        &mut context,
                        &options,
                        collection,
                        reporter,
                    )
                    .await;

                // Update state
                match result {
                    Ok((response, duration_ms)) => {
                        state.completed.insert(request.name.clone());

                        // Save response if requested
                        if let Some(save_as) = &request.save_as {
                            if let Some(body) = &response.body {
                                context.save_response(save_as.clone(), body.clone());
                            }
                        }

                        // Save to file if requested
                        if let Some(dir) = &options.save_all {
                            self.save_response_to_file(dir, &request.name, &response)?;
                        }

                        let result = RequestResult {
                            name: request.name.clone(),
                            operation: request.operation.clone(),
                            status: response.status_code,
                            body: response.body.clone(),
                            headers: response
                                .headers
                                .iter()
                                .map(|(k, v)| (k.to_string(), v.to_str().unwrap_or("").to_string()))
                                .collect(),
                            duration_ms,
                            error: None,
                            test_result: None,
                        };

                        state.results.insert(request.name.clone(), result);
                    }
                    Err(e) => {
                        state.failed.insert(request.name.clone());

                        if request.critical {
                            state.critical_failure = true;
                        }

                        let result = RequestResult {
                            name: request.name.clone(),
                            operation: request.operation.clone(),
                            status: 0,
                            body: None,
                            headers: Default::default(),
                            duration_ms: 0,
                            error: Some(e.to_string()),
                            test_result: None,
                        };

                        state.results.insert(request.name.clone(), result);

                        // Stop on failure if not continue_on_error
                        if !options.continue_on_error && !request.run_always {
                            state.critical_failure = true;
                        }
                    }
                }
            }
        }

        // Execute run_always requests
        for request in &owned_requests {
            if request.run_always && !state.results.contains_key(&request.name) {
                let result = self
                    .execute_request_with_retry(
                        request,
                        &mut context,
                        &options,
                        collection,
                        reporter,
                    )
                    .await;

                match result {
                    Ok((response, duration_ms)) => {
                        let result = RequestResult {
                            name: request.name.clone(),
                            operation: request.operation.clone(),
                            status: response.status_code,
                            body: response.body.clone(),
                            headers: response
                                .headers
                                .iter()
                                .map(|(k, v)| (k.to_string(), v.to_str().unwrap_or("").to_string()))
                                .collect(),
                            duration_ms,
                            error: None,
                            test_result: None,
                        };
                        state.results.insert(request.name.clone(), result);
                    }
                    Err(e) => {
                        let result = RequestResult {
                            name: request.name.clone(),
                            operation: request.operation.clone(),
                            status: 0,
                            body: None,
                            headers: Default::default(),
                            duration_ms: 0,
                            error: Some(e.to_string()),
                            test_result: None,
                        };
                        state.results.insert(request.name.clone(), result);
                    }
                }
            }
        }

        // Build summary
        let results: Vec<RequestResult> = owned_requests
            .iter()
            .filter_map(|r| state.results.get(&r.name).cloned())
            .collect();

        let successful = results.iter().filter(|r| r.error.is_none()).count();
        let failed = results.iter().filter(|r| r.error.is_some()).count();
        let skipped = owned_requests.len() - results.len();

        let summary = CollectionSummary {
            name: collection.name.clone(),
            total_requests: owned_requests.len(),
            successful,
            failed,
            skipped,
            total_duration_ms: start_time.elapsed().as_millis() as u64,
            results,
            test_summary: None,
        };

        reporter.on_complete(&summary);

        // Save summary if requested
        if let Some(path) = &options.save_summary {
            self.save_summary(&summary, path)?;
        }

        Ok(summary)
    }

    /// Check if any requests in the group should run_always
    fn should_run_always(&self, group: &[&str], requests: &[CollectionRequest]) -> bool {
        group.iter().any(|name| {
            requests
                .iter()
                .find(|r| r.name == *name)
                .map(|r| r.run_always)
                .unwrap_or(false)
        })
    }

    /// Check if a request should be executed based on conditions and dependencies
    async fn should_execute_request(
        &self,
        request: &CollectionRequest,
        state: &ExecutionState,
        context: &ExecutionContext,
        options: &ExecutionOptions,
    ) -> Result<bool> {
        // Check if already executed
        if state.results.contains_key(&request.name) {
            return Ok(false);
        }

        // Check if explicitly skipped
        if options.skip_requests.contains(&request.name) {
            return Ok(false);
        }

        // Check dependencies
        if let Some(deps) = &request.depends_on {
            for dep in deps {
                if state.failed.contains(dep) && !request.run_always {
                    return Ok(false);
                }
                if !state.completed.contains(dep) && !state.failed.contains(dep) {
                    // Dependency not yet executed
                    return Ok(false);
                }
            }
        }

        // Build condition context
        let mut condition_context = HashMap::new();

        // Add variables
        for (k, v) in &context.variables {
            condition_context.insert(k.clone(), v.clone());
        }

        // Add saved responses
        for (k, v) in &context.saved_responses {
            condition_context.insert(k.clone(), v.clone());
        }

        // Add environment variables
        for (k, v) in &context.environment {
            condition_context.insert(k.clone(), Value::String(v.clone()));
        }

        // Add execution results
        for (name, result) in &state.results {
            let mut result_value = serde_json::Map::new();
            result_value.insert("success".to_string(), Value::Bool(result.error.is_none()));
            result_value.insert("status".to_string(), Value::Number(result.status.into()));
            if let Some(body) = &result.body {
                result_value.insert("body".to_string(), body.clone());
            }
            condition_context.insert(name.clone(), Value::Object(result_value));
        }

        // Check skip condition
        if let Some(skip_expr) = &request.skip {
            if ConditionEvaluator::evaluate(skip_expr, &condition_context)? {
                return Ok(false);
            }
        }

        // Check if condition
        if let Some(if_expr) = &request.if_condition {
            if !ConditionEvaluator::evaluate(if_expr, &condition_context)? {
                return Ok(false);
            }
        }

        Ok(true)
    }

    /// Execute a request with retry logic
    async fn execute_request_with_retry(
        &self,
        request: &CollectionRequest,
        context: &mut ExecutionContext,
        options: &ExecutionOptions,
        collection: &Collection,
        reporter: &mut dyn Reporter,
    ) -> Result<(ApiResponse, u64)> {
        let retry_config = request.retry.as_ref();
        let max_attempts = retry_config.map(|r| r.attempts).unwrap_or(1);
        let retry_delay = retry_config.map(|r| r.delay).unwrap_or(1000);
        let backoff = retry_config.map(|r| r.backoff).unwrap_or_default();

        let mut last_error = None;

        for attempt in 0..max_attempts {
            if attempt > 0 {
                // Calculate delay with backoff
                let delay = match backoff {
                    super::models::BackoffStrategy::Linear => retry_delay * attempt as u64,
                    super::models::BackoffStrategy::Exponential => {
                        retry_delay * 2u64.pow(attempt - 1)
                    }
                };

                tokio::time::sleep(tokio::time::Duration::from_millis(delay)).await;
            }

            match self
                .execute_request(request, context, options, collection)
                .await
            {
                Ok(result) => {
                    reporter.on_request_complete(request, &result.0, result.1);
                    return Ok(result);
                }
                Err(e) => {
                    last_error = Some(e);
                    if attempt < max_attempts - 1 {
                        reporter.on_request_error(request, last_error.as_ref().unwrap());
                    }
                }
            }
        }

        let error = last_error.unwrap();
        reporter.on_request_error(request, &error);
        Err(error)
    }

    /// Execute a collection with given options
    pub async fn execute(
        &self,
        collection: &Collection,
        options: ExecutionOptions,
        reporter: &mut dyn Reporter,
    ) -> Result<CollectionSummary> {
        // Use the new dependency-aware execution
        self.execute_with_dependencies(collection, options, reporter)
            .await
    }

    /// Create execution context with variables
    fn create_context(
        &self,
        collection: &Collection,
        options: &ExecutionOptions,
    ) -> Result<ExecutionContext> {
        // Start with collection variables (lowest precedence)
        let mut context = ExecutionContext::with_variables(collection.variables.clone());

        // Load .env file if specified (higher precedence than collection vars)
        if let Some(env_file) = &options.env_file {
            context.load_env_file(env_file)?;
            // Merge environment variables into main variables
            for (key, value) in context.environment.clone() {
                context.set_variable(key, Value::String(value));
            }
        }

        // Load environment variables if requested (higher precedence than .env)
        if options.use_env {
            context.load_environment();
            // Merge environment variables into main variables
            for (key, value) in context.environment.clone() {
                context.set_variable(key, Value::String(value));
            }
        }

        // Apply CLI variable overrides last (highest precedence)
        for (key, value) in &options.variable_overrides {
            context.set_variable(key.clone(), value.clone());
        }

        Ok(context)
    }

    /// Filter requests based on execution options
    fn filter_requests<'a>(
        &self,
        collection: &'a Collection,
        options: &ExecutionOptions,
    ) -> Vec<&'a CollectionRequest> {
        let mut requests: Vec<&CollectionRequest> = collection.requests.iter().collect();

        // Filter by only_requests if specified
        if let Some(only) = &options.only_requests {
            requests.retain(|r| only.contains(&r.name));
        }

        requests
    }

    /// Execute a single request
    async fn execute_request(
        &self,
        request: &CollectionRequest,
        context: &mut ExecutionContext,
        options: &ExecutionOptions,
        collection: &Collection,
    ) -> Result<(ApiResponse, u64)> {
        let start = Instant::now();

        // Resolve variables in operation ID
        let resolved_operation = context.resolve_string(&request.operation)?;

        // Resolve variables in parameters
        let resolved_params = if let Some(params) = &request.params {
            Some(context.resolve_params(params)?)
        } else {
            None
        };

        // Resolve variables in body
        let resolved_body = if let Some(body) = &request.body {
            Some(context.resolve_value(body)?)
        } else {
            None
        };

        // Determine auth to use
        let auth = if let Some(_profile_name) = &options.auth_profile {
            // Use override auth profile
            // TODO: Load auth profile by name
            self.default_auth.clone()
        } else if let Some(_profile_name) = &collection.auth_profile {
            // Use collection auth profile
            // TODO: Load auth profile by name
            self.default_auth.clone()
        } else {
            self.default_auth.clone()
        };

        // Create run request
        let run_request = RunRequest {
            operation_id: resolved_operation,
            parameters: resolved_params,
            body: resolved_body,
            spec_path: None,
            env: None,
            auth_profile: None, // Auth is handled separately
        };

        // Execute the request
        let run_response = run_operation(run_request, &self.spec, auth)
            .await
            .with_context(|| format!("Failed to execute request '{}'", request.name))?;

        // Convert RunResponse to ApiResponse
        let status_code = run_response.meta.status_code;

        // Convert headers from HashMap<String, String> to HeaderMap
        let mut header_map = http::HeaderMap::new();
        if let Some(headers) = run_response.meta.headers {
            for (key, value) in headers {
                if let Ok(header_name) = http::HeaderName::from_bytes(key.as_bytes()) {
                    if let Ok(header_value) = http::HeaderValue::from_str(&value) {
                        header_map.insert(header_name, header_value);
                    }
                }
            }
        }

        let api_response = ApiResponse {
            status_code,
            body: run_response.data,
            headers: header_map,
        };

        let duration_ms = start.elapsed().as_millis() as u64;

        Ok((api_response, duration_ms))
    }

    /// Save response to file
    fn save_response_to_file(
        &self,
        dir: &PathBuf,
        request_name: &str,
        response: &ApiResponse,
    ) -> Result<()> {
        std::fs::create_dir_all(dir)?;

        let filename = format!("{}.json", request_name);
        let path = dir.join(filename);

        let content = serde_json::json!({
            "status": response.status_code,
            "headers": response.headers.iter()
                .map(|(k, v)| (k.to_string(), v.to_str().unwrap_or("").to_string()))
                .collect::<HashMap<_, _>>(),
            "body": response.body,
        });

        std::fs::write(path, serde_json::to_string_pretty(&content)?)?;

        Ok(())
    }

    /// Save execution summary
    fn save_summary(&self, summary: &CollectionSummary, path: &PathBuf) -> Result<()> {
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }

        std::fs::write(path, serde_json::to_string_pretty(summary)?)?;

        Ok(())
    }

    /// Execute a collection as tests with assertions
    pub async fn execute_as_tests(
        &self,
        collection: &Collection,
        options: ExecutionOptions,
    ) -> Result<crate::collections::testing::TestResults> {
        use crate::collections::testing::{
            evaluate_expectations, TestResult, TestResults, TestStatus,
        };

        // Initialize execution context
        let mut context = self.create_context(collection, &options)?;

        // Filter requests based on options
        let requests_to_run = self.filter_requests(collection, &options);

        let mut test_results = Vec::new();
        let mut passed = 0;
        let mut failed = 0;
        let mut skipped = 0;
        let start_time = Instant::now();

        // Execute each request as a test
        for request in &requests_to_run {
            let should_skip = options.skip_requests.contains(&request.name);

            if should_skip {
                test_results.push(TestResult {
                    name: request.name.clone(),
                    operation: request.operation.clone(),
                    passed: false,
                    status: TestStatus::Skipped,
                    duration_ms: 0,
                    assertions: vec![],
                    error: Some("Skipped by user".to_string()),
                });
                skipped += 1;
                continue;
            }

            // Execute request
            match self
                .execute_request(request, &mut context, &options, collection)
                .await
            {
                Ok((response, duration_ms)) => {
                    // Convert ApiResponse to RequestResult for assertions
                    let request_result = RequestResult {
                        name: request.name.clone(),
                        operation: request.operation.clone(),
                        status: response.status_code,
                        body: response.body.clone(),
                        headers: response
                            .headers
                            .iter()
                            .map(|(k, v)| (k.to_string(), v.to_str().unwrap_or("").to_string()))
                            .collect(),
                        duration_ms,
                        error: None,
                        test_result: None,
                    };

                    // Evaluate assertions
                    let assertions = evaluate_expectations(request, &request_result);
                    let test_passed = assertions.is_empty() || assertions.iter().all(|a| a.passed);

                    if test_passed {
                        passed += 1;
                    } else {
                        failed += 1;
                    }

                    // Save response if requested
                    if let Some(save_as) = &request.save_as {
                        if let Some(body) = &response.body {
                            context.save_response(save_as.clone(), body.clone());
                        }
                    }

                    test_results.push(TestResult {
                        name: request.name.clone(),
                        operation: request.operation.clone(),
                        passed: test_passed,
                        status: if test_passed {
                            TestStatus::Passed
                        } else {
                            TestStatus::Failed
                        },
                        duration_ms,
                        assertions,
                        error: None,
                    });

                    if !test_passed && !options.continue_on_error {
                        break;
                    }
                }
                Err(e) => {
                    test_results.push(TestResult {
                        name: request.name.clone(),
                        operation: request.operation.clone(),
                        passed: false,
                        status: TestStatus::Failed,
                        duration_ms: 0,
                        assertions: vec![],
                        error: Some(e.to_string()),
                    });

                    failed += 1;

                    if !options.continue_on_error {
                        break;
                    }
                }
            }
        }

        let total_duration_ms = start_time.elapsed().as_millis() as u64;
        let total_tests = test_results.len();
        let all_passed = failed == 0 && total_tests > 0;

        Ok(TestResults {
            name: collection.name.clone(),
            total_tests,
            passed,
            failed,
            skipped,
            all_passed,
            test_results,
            total_duration_ms,
        })
    }
}
