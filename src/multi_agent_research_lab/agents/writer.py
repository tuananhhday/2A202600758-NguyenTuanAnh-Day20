"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""

        from multi_agent_research_lab.services.llm_client import LLMClient

        citations = []
        sources_text_lines = []
        for index, source in enumerate(state.sources, start=1):
            location = source.url or "local lab rubric"
            citations.append(f"[{index}] {source.title} - {location}")
            sources_text_lines.append(f"[{index}] {source.title}\nURL: {location}\nSnippet: {source.snippet}")

        sources_text = "\n\n".join(sources_text_lines)

        system_prompt = (
            "You are a professional Writer Agent. Your task is to write a cohesive, comprehensive final report answering the user's query.\n"
            "You MUST use the provided research notes, analysis notes, and source list.\n"
            "Format the report cleanly with markdown headers, a summary section, detailed key findings, trade-offs/analysis, and a 'Sources' section listing the citations used.\n"
            "Every key fact/claim should cite the relevant source using its index (e.g. [1], [2]).\n"
            "Do not add conversational filler. Just output the final structured report."
        )
        user_prompt = (
            f"Query: {state.request.query}\n\n"
            f"Research Notes:\n{state.research_notes or 'No research notes available.'}\n\n"
            f"Analysis Notes:\n{state.analysis_notes or 'No analysis notes available.'}\n\n"
            f"Sources list:\n{sources_text}"
        )

        response = LLMClient().complete(system_prompt, user_prompt)
        state.final_answer = response.content

        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content=state.final_answer,
                metadata={
                    "citation_count": len(citations),
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                },
            )
        )
        state.add_trace_event(
            "writer.complete",
            {
                "citation_count": len(citations),
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
            },
        )
        return state

