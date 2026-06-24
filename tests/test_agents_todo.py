import pytest

from multi_agent_research_lab.agents import SupervisorAgent
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState


def test_supervisor_initial_route() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    next_state = SupervisorAgent().run(state)
    assert next_state.next_route == "researcher"
    assert next_state.route_history == ["researcher"]

