//! Retry logic with exponential backoff

use serde::{Deserialize, Serialize};
use std::time::Duration;

/// Retry policy configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RetryPolicy {
    /// Maximum number of retry attempts
    pub max_retries: u32,
    /// Initial retry delay in milliseconds
    pub initial_delay_ms: u64,
    /// Maximum retry delay in milliseconds
    pub max_delay_ms: u64,
    /// Exponential backoff multiplier
    pub backoff_multiplier: f64,
    /// Add jitter to prevent thundering herd
    pub jitter: bool,
}

impl Default for RetryPolicy {
    fn default() -> Self {
        Self {
            max_retries: 3,
            initial_delay_ms: 1000, // 1 second
            max_delay_ms: 30000,    // 30 seconds
            backoff_multiplier: 2.0,
            jitter: true,
        }
    }
}

/// Retry strategy state
pub struct RetryStrategy {
    policy: RetryPolicy,
    attempt: u32,
    current_delay_ms: u64,
}

impl RetryStrategy {
    /// Create a new retry strategy
    pub fn new(policy: &RetryPolicy) -> Self {
        Self {
            policy: policy.clone(),
            attempt: 0,
            current_delay_ms: policy.initial_delay_ms,
        }
    }

    /// Check if we should retry
    pub fn should_retry(&self) -> bool {
        self.attempt < self.policy.max_retries
    }

    /// Get the next retry delay
    pub fn next_delay(&mut self) -> Option<Duration> {
        if !self.should_retry() {
            return None;
        }

        self.attempt += 1;

        // Calculate delay with exponential backoff
        let mut delay_ms = self.current_delay_ms;

        // Add jitter if enabled (±25%)
        if self.policy.jitter {
            use rand::Rng;
            let mut rng = rand::thread_rng();
            let jitter_factor = rng.gen_range(0.75..1.25);
            delay_ms = (delay_ms as f64 * jitter_factor) as u64;
        }

        // Update delay for next attempt
        self.current_delay_ms =
            (self.current_delay_ms as f64 * self.policy.backoff_multiplier) as u64;
        self.current_delay_ms = self.current_delay_ms.min(self.policy.max_delay_ms);

        Some(Duration::from_millis(delay_ms))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_retry_strategy() {
        let policy = RetryPolicy {
            max_retries: 3,
            initial_delay_ms: 100,
            max_delay_ms: 1000,
            backoff_multiplier: 2.0,
            jitter: false,
        };

        let mut strategy = RetryStrategy::new(&policy);

        // Should allow retries initially
        assert!(strategy.should_retry());

        // First retry - 100ms
        let delay1 = strategy.next_delay().unwrap();
        assert_eq!(delay1.as_millis(), 100);
        assert!(strategy.should_retry());

        // Second retry - 200ms
        let delay2 = strategy.next_delay().unwrap();
        assert_eq!(delay2.as_millis(), 200);
        assert!(strategy.should_retry());

        // Third retry - 400ms
        let delay3 = strategy.next_delay().unwrap();
        assert_eq!(delay3.as_millis(), 400);
        assert!(!strategy.should_retry()); // No more retries

        // No more delays
        assert!(strategy.next_delay().is_none());
    }

    #[test]
    fn test_max_delay_cap() {
        let policy = RetryPolicy {
            max_retries: 5,
            initial_delay_ms: 1000,
            max_delay_ms: 5000,
            backoff_multiplier: 10.0, // Aggressive backoff
            jitter: false,
        };

        let mut strategy = RetryStrategy::new(&policy);

        // First retry - 1000ms
        let delay1 = strategy.next_delay().unwrap();
        assert_eq!(delay1.as_millis(), 1000);

        // Second retry - should be capped at 5000ms
        let delay2 = strategy.next_delay().unwrap();
        assert_eq!(delay2.as_millis(), 5000);

        // Third retry - still capped at 5000ms
        let delay3 = strategy.next_delay().unwrap();
        assert_eq!(delay3.as_millis(), 5000);
    }
}
