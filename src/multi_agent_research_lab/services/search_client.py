"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client with a deterministic local corpus.

    The lab can be completed without paying for a search API. Swap this class for
    Tavily/Bing/SerpAPI later if live web search is required.
    """

    _CORPUS = [
        SourceDocument(
            title="Anthropic: Building effective agents",
            url="https://www.anthropic.com/engineering/building-effective-agents",
            snippet=(
                "Effective agentic systems should start simple, add orchestration only "
                "when it improves outcomes, and keep workflows observable."
            ),
            metadata={"topics": ["agents", "guardrails", "orchestration"]},
        ),
        SourceDocument(
            title="OpenAI Agents SDK orchestration and handoffs",
            url="https://developers.openai.com/api/docs/guides/agents/orchestration",
            snippet=(
                "Agent handoffs work best when each role has a clear instruction set, "
                "structured input, and explicit transfer conditions."
            ),
            metadata={"topics": ["agents", "handoff", "supervisor"]},
        ),
        SourceDocument(
            title="LangGraph concepts",
            url="https://langchain-ai.github.io/langgraph/concepts/",
            snippet=(
                "Graph-based agent workflows model state, nodes, edges, conditional "
                "routing, retries, and durable execution."
            ),
            metadata={"topics": ["langgraph", "state", "routing"]},
        ),
        SourceDocument(
            title="LangSmith tracing",
            url="https://docs.smith.langchain.com/",
            snippet=(
                "Tracing captures intermediate steps, latency, inputs, outputs, and "
                "errors so teams can debug and evaluate LLM applications."
            ),
            metadata={"topics": ["trace", "evaluation", "latency"]},
        ),
        SourceDocument(
            title="Multi-agent benchmark rubric",
            url=None,
            snippet=(
                "Compare single-agent and multi-agent runs by latency, quality, cost, "
                "citation coverage, and failure rate rather than appearance alone."
            ),
            metadata={"topics": ["benchmark", "quality", "failure"]},
        ),
    ]

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search local documents using simple keyword overlap."""

        query_terms = {term.lower().strip(".,:;!?()") for term in query.split()}
        scored: list[tuple[int, SourceDocument]] = []
        for document in self._CORPUS:
            haystack = " ".join(
                [
                    document.title,
                    document.snippet,
                    " ".join(str(topic) for topic in document.metadata.get("topics", [])),
                ]
            ).lower()
            score = sum(1 for term in query_terms if term and term in haystack)
            scored.append((score, document))

        scored.sort(key=lambda item: item[0], reverse=True)
        selected = [document for score, document in scored if score > 0]
        if not selected:
            selected = [document for _, document in scored]
        return selected[:max_results]
