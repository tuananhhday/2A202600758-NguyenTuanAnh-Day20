"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""

        from multi_agent_research_lab.services.llm_client import LLMClient

        sources = SearchClient().search(state.request.query, state.request.max_sources)
        state.sources = sources

        if not sources:
            state.research_notes = "No relevant sources found."
            return state

        sources_text = "\n\n".join(
            f"[{index}] {source.title}\nURL: {source.url or 'N/A'}\nSnippet: {source.snippet}"
            for index, source in enumerate(sources, start=1)
        )

        system_prompt = (
            "You are a professional Researcher Agent. Analyze the provided query and sources.\n"
            "Produce detailed, factual research notes summarizing findings relevant to the query.\n"
            "Make sure to cite your sources using bracketed indices (e.g. [1], [2]) based on the sources listed below.\n"
            "Do not add conversational fluff or preambles. Just return the structured research notes."
        )
        user_prompt = f"Query: {state.request.query}\n\nSources:\n{sources_text}"

        response = LLMClient().complete(system_prompt, user_prompt)
        state.research_notes = response.content

        state.agent_results.append(
            AgentResult(
                agent=AgentName.RESEARCHER,
                content=state.research_notes,
                metadata={
                    "source_count": len(sources),
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                },
            )
        )
        state.add_trace_event(
            "researcher.complete",
            {
                "source_count": len(sources),
                "titles": [source.title for source in sources],
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
            },
        )
        return state

