//! Rate limiting implementation for HTTP requests

use anyhow::{anyhow, Result};
use std::collections::HashMap;
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::Mutex;

/// Rate limiter configuration
#[derive(Debug, Clone)]
pub struct RateLimitConfig {
    /// Maximum requests per second
    pub requests_per_second: u32,
    /// Burst size (max requests that can be made at once)
    pub burst_size: u32,
    /// Whether to enable per-host rate limiting
    pub per_host_limiting: bool,
}

impl Default for RateLimitConfig {
    fn default() -> Self {
        Self {
            requests_per_second: 10,
            burst_size: 20,
            per_host_limiting: true,
        }
    }
}

/// Token bucket for rate limiting
#[derive(Debug)]
struct TokenBucket {
    tokens: f64,
    max_tokens: f64,
    refill_rate: f64,
    last_refill: Instant,
}

impl TokenBucket {
    fn new(max_tokens: u32, refill_rate: u32) -> Self {
        Self {
            tokens: max_tokens as f64,
            max_tokens: max_tokens as f64,
            refill_rate: refill_rate as f64,
            last_refill: Instant::now(),
        }
    }

    fn try_consume(&mut self, tokens: f64) -> bool {
        self.refill();

        if self.tokens >= tokens {
            self.tokens -= tokens;
            true
        } else {
            false
        }
    }

    fn refill(&mut self) {
        let now = Instant::now();
        let elapsed = now.duration_since(self.last_refill).as_secs_f64();

        self.tokens = (self.tokens + elapsed * self.refill_rate).min(self.max_tokens);
        self.last_refill = now;
    }

    fn time_until_tokens(&self, needed: f64) -> Duration {
        if self.tokens >= needed {
            return Duration::ZERO;
        }

        let tokens_needed = needed - self.tokens;
        let seconds_needed = tokens_needed / self.refill_rate;
        Duration::from_secs_f64(seconds_needed)
    }
}

/// Rate limiter for HTTP requests
pub struct RateLimiter {
    config: RateLimitConfig,
    global_bucket: Arc<Mutex<TokenBucket>>,
    host_buckets: Arc<Mutex<HashMap<String, TokenBucket>>>,
}

impl RateLimiter {
    pub fn new(config: RateLimitConfig) -> Self {
        let global_bucket = TokenBucket::new(config.burst_size, config.requests_per_second);

        Self {
            config,
            global_bucket: Arc::new(Mutex::new(global_bucket)),
            host_buckets: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Check if a request to the given host should be allowed
    pub async fn check_rate_limit(&self, host: Option<&str>) -> Result<()> {
        // If per-host limiting is enabled, use separate buckets per host
        if self.config.per_host_limiting {
            if let Some(host) = host {
                // Use per-host bucket with FULL rate limits (not halved)
                let mut host_buckets = self.host_buckets.lock().await;

                let bucket = host_buckets.entry(host.to_string()).or_insert_with(|| {
                    TokenBucket::new(
                        self.config.burst_size,          // Full burst for per-host
                        self.config.requests_per_second, // Full rate for per-host
                    )
                });

                if !bucket.try_consume(1.0) {
                    let wait_time = bucket.time_until_tokens(1.0);
                    return Err(anyhow!(
                        "Rate limit exceeded for host '{}'. Retry after {:?}",
                        host,
                        wait_time
                    ));
                }
            } else {
                // No host specified but per-host limiting is enabled
                // Fall back to global bucket for non-host-specific requests
                let mut global = self.global_bucket.lock().await;
                if !global.try_consume(1.0) {
                    let wait_time = global.time_until_tokens(1.0);
                    return Err(anyhow!(
                        "Global rate limit exceeded. Retry after {:?}",
                        wait_time
                    ));
                }
            }
        } else {
            // Per-host limiting is disabled, use global bucket only
            let mut global = self.global_bucket.lock().await;
            if !global.try_consume(1.0) {
                let wait_time = global.time_until_tokens(1.0);
                return Err(anyhow!(
                    "Global rate limit exceeded. Retry after {:?}",
                    wait_time
                ));
            }
        }

        Ok(())
    }

    /// Wait until rate limit allows request
    pub async fn wait_if_needed(&self, host: Option<&str>) -> Result<()> {
        loop {
            match self.check_rate_limit(host).await {
                Ok(()) => return Ok(()),
                Err(_e) => {
                    // Extract wait time from error message (simple approach)
                    // In production, we'd return a proper error type with duration
                    tokio::time::sleep(Duration::from_millis(100)).await;
                }
            }
        }
    }

    /// Clean up old host entries (call periodically)
    #[allow(dead_code)]
    pub async fn cleanup_old_hosts(&self) {
        let mut host_buckets = self.host_buckets.lock().await;

        // Remove entries that haven't been used recently
        // In production, track last access time
        if host_buckets.len() > 1000 {
            host_buckets.clear();
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_rate_limiting() {
        let config = RateLimitConfig {
            requests_per_second: 2,
            burst_size: 4,
            per_host_limiting: false,
        };

        let limiter = RateLimiter::new(config);

        // Should allow burst
        for _ in 0..4 {
            assert!(limiter.check_rate_limit(None).await.is_ok());
        }

        // Should be rate limited
        assert!(limiter.check_rate_limit(None).await.is_err());
    }

    #[tokio::test]
    async fn test_per_host_limiting() {
        let config = RateLimitConfig {
            requests_per_second: 10,
            burst_size: 20,
            per_host_limiting: true,
        };

        let limiter = RateLimiter::new(config);

        // Different hosts should have separate limits
        // Each host gets its own burst_size=20
        for _ in 0..20 {
            assert!(limiter.check_rate_limit(Some("host1.com")).await.is_ok());
            assert!(limiter.check_rate_limit(Some("host2.com")).await.is_ok());
        }

        // host1 should be limited now after 20 requests
        assert!(limiter.check_rate_limit(Some("host1.com")).await.is_err());

        // host2 should also be limited after 20 requests
        assert!(limiter.check_rate_limit(Some("host2.com")).await.is_err());

        // But host3 should still work
        assert!(limiter.check_rate_limit(Some("host3.com")).await.is_ok());
    }
}
