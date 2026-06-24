"""Command-line entrypoint for the lab starter."""

import sys
from typing import Annotated, TextIO

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import AgentName, AgentResult, ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.services.llm_client import LLMClient

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    _configure_utf8_console()


def _configure_utf8_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        _reconfigure_stream(stream)


def _reconfigure_stream(stream: TextIO) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline."""

    _init()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    response = LLMClient().complete(
        system_prompt=(
            "You are a careful single-agent research assistant. Answer directly, "
            "state uncertainty, and keep the response concise."
        ),
        user_prompt=request.query,
    )
    state.final_answer = response.content
    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))


@app.command()
def benchmark(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")] = (
        "Compare single-agent and multi-agent workflows for customer support"
    ),
) -> None:
    """Run a small single-vs-multi benchmark."""

    _init()

    def baseline_runner(item: str) -> ResearchState:
        request = ResearchQuery(query=item)
        state = ResearchState(request=request)
        response = LLMClient().complete(
            system_prompt="You are a concise single-agent research assistant.",
            user_prompt=item,
        )
        state.final_answer = response.content
        state.agent_results.append(
            AgentResult(
                agent=AgentName.SUPERVISOR,
                content=response.content,
                metadata={
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                },
            )
        )
        return state

    def multi_runner(item: str) -> ResearchState:
        return MultiAgentWorkflow().run(ResearchState(request=ResearchQuery(query=item)))

    _, baseline_metrics = run_benchmark("single-agent-baseline", query, baseline_runner)
    _, multi_metrics = run_benchmark("multi-agent-workflow", query, multi_runner)
    report = render_markdown_report([baseline_metrics, multi_metrics])
    console.print(report)

    from multi_agent_research_lab.services.storage import LocalArtifactStore
    store = LocalArtifactStore()
    report_path = store.write_text("benchmark_report.md", report)
    console.print(f"[green]Saved benchmark report to: {report_path}[/green]")



if __name__ == "__main__":
    app()
