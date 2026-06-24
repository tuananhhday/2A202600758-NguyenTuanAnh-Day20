# Benchmark Report

This report compares a single-agent baseline with the multi-agent workflow.
Quality is an automatic rubric estimate and should be confirmed by peer review.

| Run | Latency (s) | Cost (USD) | Quality | Notes |
|---|---:|---:|---:|---|
| single-agent-baseline | 12.31 | 0.0016 | 5.0 | sources=0; citation_coverage=0%; trace_events=0; failed=False |
| multi-agent-workflow | 47.10 | 0.0154 | 10.0 | sources=5; citation_coverage=100%; trace_events=19; failed=False |

## Failure Mode

- If the LLM provider is rate-limited, the single-agent baseline can fail or slow down.
- The multi-agent path keeps a deterministic local search fallback so trace, handoff, and benchmark evidence remain available.
- The main fix is to retry provider calls with backoff and keep a mock/local corpus for classroom demos.

## Trace Evidence

The multi-agent state stores route history and trace events for supervisor, researcher, analyst, and writer steps.
