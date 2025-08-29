# Resource Protection Features

This document describes the resource protection features implemented in MicroRapid to prevent resource exhaustion and improve reliability.

## Overview

MicroRapid implements several resource protection mechanisms:

1. **Request Timeout Enforcement** - Prevents hanging on slow APIs
2. **Retry Logic with Exponential Backoff** - Handles transient failures
3. **Body Size Limits** - Prevents memory exhaustion
4. **Response Size Validation** - Protects against large responses

## Features

### 1. Request Timeout Enforcement

All HTTP requests have configurable timeouts to prevent indefinite waiting:

```toml
[performance]
request_timeout = 30  # seconds
```

**Implementation:**
- Enforced at the HTTP client level
- Applies to all API operations
- Returns `TimeoutError` when exceeded
- Default: 30 seconds

### 2. Retry Logic with Exponential Backoff

Automatic retry for transient failures:

```toml
[performance]
max_retries = 3
```

**Retry Policy:**
- Max retries: 3 (configurable)
- Initial delay: 1 second
- Max delay: 30 seconds
- Backoff multiplier: 2.0
- Jitter: ±25% to prevent thundering herd

**Retryable Errors:**
- Network timeouts
- Connection errors
- HTTP 5xx errors
- HTTP 429 (rate limit)

**Non-retryable Errors:**
- HTTP 4xx (except 429)
- Authentication failures
- Validation errors

### 3. Request Body Size Limits

Prevents sending excessively large requests:

```toml
[performance]
max_body_size_mb = 10  # MB
```

**Implementation:**
- Checked before sending request
- Returns `PayloadTooLarge` error
- Default: 10MB

### 4. Response Size Limits

Protects against memory exhaustion from large responses:

**Configuration:**
- Max response size: 50MB (hardcoded)
- Streaming read with incremental size checking
- Early termination if limit exceeded

## Error Handling

### Timeout Errors

```json
{
  "error": {
    "code": 4002,
    "message": "Request timed out after 30 seconds"
  }
}
```

### Size Limit Errors

```json
{
  "error": {
    "code": 4413,
    "message": "Request body too large: 15728640 bytes (max: 10485760 bytes)"
  }
}
```

### Retry Exhausted

```json
{
  "error": {
    "code": 4001,
    "message": "Request failed after 3 retries: Connection refused"
  }
}
```

## Usage in Agent CLI

The Agent CLI automatically applies these protections when executing API operations:

```bash
# Agent respects timeout configuration
mrapids-agent start --config agent-config.toml

# In agent-config.toml:
[performance]
request_timeout = 60      # 1 minute timeout
max_retries = 5          # More retries for reliability
max_body_size_mb = 20    # Larger payloads allowed
```

## Best Practices

1. **Timeout Configuration**
   - Set based on expected API response times
   - Add buffer for network latency
   - Consider operation complexity

2. **Retry Strategy**
   - More retries for read operations
   - Fewer retries for write operations
   - Consider idempotency

3. **Size Limits**
   - Set based on API requirements
   - Monitor actual usage patterns
   - Leave headroom for growth

## Performance Impact

- **Minimal overhead**: ~1-2ms per request
- **Memory efficient**: Streaming for large responses
- **Network efficient**: Exponential backoff reduces load

## Future Enhancements

### Circuit Breaker Pattern (Planned)
- Fail fast when service is down
- Automatic recovery detection
- Per-endpoint tracking

### Response Streaming (Planned)
- True streaming for large responses
- Reduced memory footprint
- Progress callbacks

## Testing

Test the resource protection:

```bash
# Test timeout
curl -X POST http://localhost:3333 \
  -d '{"method": "run", "params": {"operation_id": "slowOperation"}}'

# Test large payload rejection
curl -X POST http://localhost:3333 \
  -H "Content-Length: 20000000" \
  -d @large-file.json

# Test retry behavior
# (Temporarily stop the target API to trigger retries)
```

## Configuration Reference

```toml
[performance]
# Request timeout in seconds
request_timeout = 30

# Maximum retry attempts
max_retries = 3

# Maximum request body size in MB
max_body_size_mb = 10

# Rate limiting (requests per minute)
rate_limit = 100
```

## Monitoring

Monitor resource protection metrics:

1. **Timeout Rate**: Track % of requests timing out
2. **Retry Rate**: Monitor retry frequency
3. **Size Violations**: Count payload rejections
4. **Response Times**: P50, P95, P99 latencies

## Troubleshooting

### "Request timed out"
- Increase `request_timeout`
- Check API server health
- Verify network connectivity

### "Payload too large"
- Increase `max_body_size_mb`
- Consider pagination
- Compress request data

### "Failed after retries"
- Check API availability
- Increase `max_retries`
- Review retry conditions