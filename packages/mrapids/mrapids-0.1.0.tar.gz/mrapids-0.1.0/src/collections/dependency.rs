//! Dependency resolution for collection requests

use super::models::CollectionRequest;
use anyhow::{bail, Result};
use std::collections::{HashMap, HashSet, VecDeque};

/// Dependency graph for collection requests
#[derive(Debug)]
pub struct DependencyGraph<'a> {
    /// Map of request name to request
    requests: HashMap<&'a str, &'a CollectionRequest>,

    /// Adjacency list of dependencies
    dependencies: HashMap<&'a str, Vec<&'a str>>,

    /// Reverse dependencies (who depends on this)
    dependents: HashMap<&'a str, Vec<&'a str>>,
}

impl<'a> DependencyGraph<'a> {
    /// Build a dependency graph from collection requests
    pub fn build(requests: &'a [CollectionRequest]) -> Result<Self> {
        let mut graph = Self {
            requests: HashMap::new(),
            dependencies: HashMap::new(),
            dependents: HashMap::new(),
        };

        // First pass: collect all request names
        for request in requests {
            graph.requests.insert(&request.name, request);
            graph.dependencies.insert(&request.name, Vec::new());
            graph.dependents.insert(&request.name, Vec::new());
        }

        // Second pass: build dependency relationships
        for request in requests {
            if let Some(deps) = &request.depends_on {
                for dep in deps {
                    // Validate dependency exists
                    if !graph.requests.contains_key(dep.as_str()) {
                        bail!(
                            "Request '{}' depends on '{}', which doesn't exist",
                            request.name,
                            dep
                        );
                    }

                    // Add to adjacency lists
                    graph
                        .dependencies
                        .get_mut(request.name.as_str())
                        .unwrap()
                        .push(dep.as_str());

                    graph
                        .dependents
                        .get_mut(dep.as_str())
                        .unwrap()
                        .push(request.name.as_str());
                }
            }
        }

        // Validate no circular dependencies
        graph.validate_no_cycles()?;

        Ok(graph)
    }

    /// Check for circular dependencies
    fn validate_no_cycles(&self) -> Result<()> {
        let mut visited = HashSet::new();
        let mut rec_stack = HashSet::new();

        for name in self.requests.keys() {
            if !visited.contains(name) {
                if self.has_cycle_dfs(name, &mut visited, &mut rec_stack)? {
                    bail!("Circular dependency detected in collection");
                }
            }
        }

        Ok(())
    }

    /// DFS helper for cycle detection
    fn has_cycle_dfs(
        &self,
        node: &'a str,
        visited: &mut HashSet<&'a str>,
        rec_stack: &mut HashSet<&'a str>,
    ) -> Result<bool> {
        visited.insert(node);
        rec_stack.insert(node);

        if let Some(deps) = self.dependencies.get(node) {
            for dep in deps {
                if !visited.contains(dep) {
                    if self.has_cycle_dfs(dep, visited, rec_stack)? {
                        return Ok(true);
                    }
                } else if rec_stack.contains(dep) {
                    return Ok(true);
                }
            }
        }

        rec_stack.remove(node);
        Ok(false)
    }

    /// Get execution order using topological sort
    pub fn get_execution_order(&self) -> Vec<&'a str> {
        let mut in_degree = HashMap::new();
        let mut queue = VecDeque::new();
        let mut result = Vec::new();

        // Calculate in-degrees (number of dependencies each node has)
        for (name, deps) in &self.dependencies {
            in_degree.insert(*name, deps.len());
        }

        // Find nodes with no dependencies
        for (name, &degree) in &in_degree {
            if degree == 0 {
                queue.push_back(*name);
            }
        }

        // Process queue
        while let Some(node) = queue.pop_front() {
            result.push(node);

            // For each node that depends on the current node
            if let Some(dependents) = self.dependents.get(node) {
                for dependent in dependents {
                    let degree = in_degree.get_mut(dependent).unwrap();
                    *degree -= 1;
                    if *degree == 0 {
                        queue.push_back(dependent);
                    }
                }
            }
        }

        result
    }

    /// Get requests that can be executed in parallel
    pub fn get_parallel_groups(&self) -> Vec<Vec<&'a str>> {
        let mut groups = Vec::new();
        let mut remaining: HashSet<&str> = self.requests.keys().copied().collect();
        let mut completed = HashSet::new();

        while !remaining.is_empty() {
            let mut current_group = Vec::new();

            for name in remaining.clone() {
                let can_run = if let Some(deps) = self.dependencies.get(name) {
                    deps.iter().all(|dep| completed.contains(dep))
                } else {
                    true
                };

                if can_run {
                    current_group.push(name);
                    remaining.remove(name);
                }
            }

            if current_group.is_empty() {
                // This shouldn't happen if we validated no cycles
                break;
            }

            for name in &current_group {
                completed.insert(*name);
            }

            groups.push(current_group);
        }

        groups
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::collections::models::CollectionRequest;

    fn create_request(name: &str, depends_on: Option<Vec<String>>) -> CollectionRequest {
        CollectionRequest {
            name: name.to_string(),
            operation: "test".to_string(),
            params: None,
            body: None,
            save_as: None,
            expect: None,
            depends_on,
            if_condition: None,
            skip: None,
            run_always: false,
            critical: false,
            retry: None,
        }
    }

    #[test]
    fn test_simple_dependency() {
        let requests = vec![
            create_request("a", None),
            create_request("b", Some(vec!["a".to_string()])),
            create_request("c", Some(vec!["b".to_string()])),
        ];

        let graph = DependencyGraph::build(&requests).unwrap();
        let order = graph.get_execution_order();

        assert_eq!(order, vec!["a", "b", "c"]);
    }

    #[test]
    fn test_parallel_execution() {
        let requests = vec![
            create_request("a", None),
            create_request("b", None),
            create_request("c", Some(vec!["a".to_string(), "b".to_string()])),
            create_request("d", Some(vec!["c".to_string()])),
        ];

        let graph = DependencyGraph::build(&requests).unwrap();
        let groups = graph.get_parallel_groups();

        assert_eq!(groups.len(), 3);
        assert_eq!(groups[0].len(), 2); // a and b in parallel
        assert!(groups[0].contains(&"a"));
        assert!(groups[0].contains(&"b"));
        assert_eq!(groups[1], vec!["c"]);
        assert_eq!(groups[2], vec!["d"]);
    }

    #[test]
    fn test_circular_dependency() {
        let requests = vec![
            create_request("a", Some(vec!["c".to_string()])),
            create_request("b", Some(vec!["a".to_string()])),
            create_request("c", Some(vec!["b".to_string()])),
        ];

        let result = DependencyGraph::build(&requests);
        assert!(result.is_err());
        assert!(result
            .unwrap_err()
            .to_string()
            .contains("Circular dependency"));
    }

    #[test]
    fn test_missing_dependency() {
        let requests = vec![
            create_request("a", None),
            create_request("b", Some(vec!["nonexistent".to_string()])),
        ];

        let result = DependencyGraph::build(&requests);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("doesn't exist"));
    }
}
