# ADR-0001: Single automatic retry on HTTP 429

## Status
Accepted

## Date
2026-04-11

## Context
The SDK performs one automatic retry when the API returns HTTP 429 (rate limit
exceeded). The retry sleeps for `min(Retry-After, 30)` seconds before re-issuing
the identical request. If the retry also returns 429, `ScriftRateLimitError` is
raised immediately - no further retries.

Transient network errors (`httpx.ConnectError`, `httpx.TimeoutException`) are NOT
retried automatically.

## Decision
Keep the single-retry behaviour as the permanent default. Reasons:

1. **Simplicity over configurability.** The SDK is synchronous and single-threaded.
   Adding configurable retry loops (`max_retries`, `retry_on_status`) before there
   is a documented consumer need is premature complexity.
2. **429 is the only transient API error worth auto-handling.** The Scrift API uses
   sliding window rate limits with accurate `Retry-After` headers. One retry with
   the server-supplied delay resolves the vast majority of burst-rate cases without
   consumer involvement.
3. **Network errors are caller responsibility.** Consumers building retry logic
   around network failures already have their own retry/circuit-breaker patterns.
   Double-retrying inside the SDK would conflict with those.

## Consequences
- Consumers who need zero-sleep behaviour (latency-sensitive pipelines) must catch
  `ScriftRateLimitError` and handle it themselves.
- If a future use case requires configurable retry, add `max_retries: int = 1` and
  `retry_on_status: frozenset[int] = frozenset({429})` kwargs to `ScriftClient.__init__`
  as a non-breaking additive change. Do not change the default behaviour.
- This ADR must be reviewed before implementing Phase 3 retry improvements.
