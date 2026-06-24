"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""

        from multi_agent_research_lab.core.schemas import AgentName, AgentResult
        from multi_agent_research_lab.services.llm_client import LLMClient

        system_prompt = (
            "You are a professional Critic Agent. Your task is to evaluate the writer's final report.\n"
            "Compare the report against the research notes to ensure all facts are supported and citations are correct.\n"
            "Check for hallucinations or inaccurate assertions.\n"
            "If the report is accurate, well-cited, and fully addresses the query, write 'APPROVED'.\n"
            "If there are deficiencies, list them clearly so the writer can address them."
        )
        user_prompt = (
            f"Query: {state.request.query}\n\n"
            f"Research Notes:\n{state.research_notes or 'No research notes.'}\n\n"
            f"Final Report:\n{state.final_answer or 'No final report.'}"
        )

        response = LLMClient().complete(system_prompt, user_prompt)
        critique = response.content
        approved = "APPROVED" in critique.upper()

        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC,
                content=critique,
                metadata={
                    "approved": approved,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                },
            )
        )
        state.add_trace_event(
            "critic.complete",
            {
                "approved": approved,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
            },
        )
        return state

