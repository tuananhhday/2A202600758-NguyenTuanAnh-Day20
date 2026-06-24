"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and estimate simple rubric-facing metrics."""

    started = perf_counter()
    try:
        state = runner(query)
        failed = bool(state.errors) or not state.final_answer
    except Exception as exc:
        state = ResearchState.model_validate({"request": {"query": query}, "errors": [str(exc)]})
        failed = True
    latency = perf_counter() - started
    source_count = len(state.sources)
    citation_coverage = min(source_count / max(state.request.max_sources, 1), 1.0)
    quality_score = _estimate_quality(state, citation_coverage, failed)
    
    # Calculate estimated cost based on token usage
    total_input = 0
    total_output = 0
    for res in state.agent_results:
        total_input += res.metadata.get("input_tokens") or 0
        total_output += res.metadata.get("output_tokens") or 0
    
    # standard GPT-3.5-Turbo style pricing: $0.0015/1k input, $0.002/1k output
    estimated_cost = (total_input * 0.0015 + total_output * 0.002) / 1000.0

    notes = (
        f"sources={source_count}; citation_coverage={citation_coverage:.0%}; "
        f"trace_events={len(state.trace)}; failed={failed}"
    )
    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=estimated_cost,
        quality_score=quality_score,
        notes=notes,
    )
    return state, metrics



def _estimate_quality(state: ResearchState, citation_coverage: float, failed: bool) -> float:
    if failed:
        return 2.0
    score = 4.0
    if state.research_notes:
        score += 1.5
    if state.analysis_notes:
        score += 1.5
    if state.final_answer:
        score += 1.0
    score += min(citation_coverage, 1.0) * 2.0
    return min(score, 10.0)
