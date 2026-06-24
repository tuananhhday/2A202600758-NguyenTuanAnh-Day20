"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown."""

    lines = [
        "# Benchmark Report",
        "",
        "This report compares a single-agent baseline with the multi-agent workflow.",
        "Quality is an automatic rubric estimate and should be confirmed by peer review.",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality | Notes |",
        "|---|---:|---:|---:|---|",
    ]
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        lines.append(f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} | {item.notes} |")
    lines.extend(
        [
            "",
            "## Failure Mode",
            "",
            "- If the LLM provider is rate-limited, the single-agent baseline can fail or slow down.",
            "- The multi-agent path keeps a deterministic local search fallback so trace, handoff, and benchmark evidence remain available.",
            "- The main fix is to retry provider calls with backoff and keep a mock/local corpus for classroom demos.",
            "",
            "## Trace Evidence",
            "",
            "The multi-agent state stores route history and trace events for supervisor, researcher, analyst, and writer steps.",
        ]
    )
    return "\n".join(lines) + "\n"
