"""LangGraph workflow skeleton."""

from multi_agent_research_lab.agents import AnalystAgent, CriticAgent, ResearcherAgent, SupervisorAgent, WriterAgent
from multi_agent_research_lab.core.errors import AgentExecutionError
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(self) -> None:
        self.agents = {
            "supervisor": SupervisorAgent(),
            "researcher": ResearcherAgent(),
            "analyst": AnalystAgent(),
            "writer": WriterAgent(),
            "critic": CriticAgent(),
        }

    def build(self) -> object:
        """Return a lightweight graph description.

        This starter avoids a hard LangGraph dependency for the graded path, but
        preserves the same node/edge model so it can be swapped to LangGraph.
        """

        return {
            "nodes": list(self.agents),
            "edges": {
                "supervisor": ["researcher", "analyst", "writer", "critic", "done"],
                "researcher": ["supervisor"],
                "analyst": ["supervisor"],
                "writer": ["supervisor"],
                "critic": ["supervisor"],
            },
        }

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""

        self.build()
        while True:
            state = self._run_agent("supervisor", state)
            route = state.next_route
            if route == "done":
                state.add_trace_event("workflow.done", {"iterations": state.iteration})
                return state
            if route not in {"researcher", "analyst", "writer", "critic"}:
                raise AgentExecutionError(f"Unknown supervisor route: {route}")
            state = self._run_agent(route, state)

    def _run_agent(self, name: str, state: ResearchState) -> ResearchState:
        agent = self.agents[name]
        with trace_span(f"agent.{name}") as span:
            try:
                state = agent.run(state)
            except Exception as exc:
                state.errors.append(f"{name} failed: {exc}")
                span["error"] = str(exc)
                raise
            finally:
                state.add_trace_event(
                    f"agent.{name}.span",
                    {
                        "duration_seconds": span["duration_seconds"],
                        "error": span.get("error"),
                    },
                )
        return state
