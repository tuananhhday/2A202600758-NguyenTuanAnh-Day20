"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""

        from multi_agent_research_lab.services.llm_client import LLMClient

        source_count = len(state.sources)
        citation_risk = "low" if source_count >= 3 else "medium"

        system_prompt = (
            "You are a professional Analyst Agent. Your task is to analyze the research notes provided.\n"
            "Identify key claims, compare viewpoints, evaluate trade-offs, and assess evidence/citation risk.\n"
            "Determine the citation risk (e.g. low/medium/high) and mention the count of sources available.\n"
            "Format your response cleanly. Do not add conversational preambles or chat. Just output the analysis notes."
        )
        user_prompt = (
            f"Query: {state.request.query}\n\n"
            f"Source count: {source_count}\n"
            f"Citation risk estimation: {citation_risk}\n\n"
            f"Research Notes:\n{state.research_notes or 'No research notes available.'}"
        )

        response = LLMClient().complete(system_prompt, user_prompt)
        state.analysis_notes = response.content

        state.agent_results.append(
            AgentResult(
                agent=AgentName.ANALYST,
                content=state.analysis_notes,
                metadata={
                    "citation_risk": citation_risk,
                    "source_count": source_count,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                },
            )
        )
        state.add_trace_event(
            "analyst.complete",
            {
                "citation_risk": citation_risk,
                "source_count": source_count,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
            },
        )
        return state

