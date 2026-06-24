"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.next_route` with the next route."""

        settings = get_settings()
        if state.iteration >= settings.max_iterations:
            route = "done"
            state.errors.append("Max iterations reached; using fallback route")
        elif not state.research_notes:
            route = "researcher"
        elif not state.analysis_notes:
            route = "analyst"
        elif not state.final_answer:
            route = "writer"
        else:
            # We have a final answer. Check if it has been evaluated by the critic.
            critic_results = [r for r in state.agent_results if r.agent == "critic"]
            if not critic_results:
                route = "critic"
            else:
                last_critic = critic_results[-1]
                approved = last_critic.metadata.get("approved", False)
                if approved:
                    route = "done"
                else:
                    # Critic rejected the draft. Route back to writer if iterations permit.
                    writer_count = sum(1 for r in state.route_history if r == "writer")
                    if writer_count < 3:
                        state.final_answer = None  # Reset final answer to force writer node to rerun
                        route = "writer"
                        state.errors.append(f"Critic rejected draft: {last_critic.content[:150]}... Routing back to writer.")
                    else:
                        route = "done"
                        state.errors.append("Critic rejected draft, but routing to done due to iteration limits.")

        state.next_route = route
        state.record_route(route)
        state.add_trace_event(
            "supervisor.route",
            {
                "route": route,
                "iteration": state.iteration,
                "has_research": bool(state.research_notes),
                "has_analysis": bool(state.analysis_notes),
                "has_final": bool(state.final_answer),
            },
        )
        return state

