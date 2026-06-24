# Design Template - Multi-Agent Research System

## Problem

Building an automated research assistant that can take a complex user query, search for relevant evidence/sources, analyze the gathered facts, synthesize a structured report with correct citations, and verify the report for factual correctness.

## Why multi-agent?

A single-agent approach performs all steps (retrieval, analysis, writing, and review) in a single LLM context/call. This leads to several failure modes:
1. **Hallucination & Information Overload**: The LLM must process raw documents and generate the report simultaneously, frequently mixing up details or hallucinating unsupported claims.
2. **Lack of Depth**: Single-pass generation lacks cognitive iteration. There is no step where claims are critically analyzed or weighed.
3. **Hard to Debug/Trace**: If the output is poor, it is impossible to know whether the search, the analysis, or the synthesis failed.
4. **No Guardrails/Reviews**: The agent cannot check its own work dynamically before returning it to the user.

A multi-agent architecture resolves this by separating concerns: one agent gathers sources (Researcher), another analyzes risk and trade-offs (Analyst), a third writes the report (Writer), and a fourth fact-checks the work (Critic), all orchestrated by a Supervisor.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| **Supervisor** | Directs workflow transitions and stops when complete or at limit | Shared state (`ResearchState`) | Next agent name (`next_route`) | Infinite loops (mitigated by max iteration limits) |
| **Researcher** | Searches databases and drafts objective, cited research notes | `request.query`, `SearchClient` corpus | `sources`, `research_notes` | Retrieval failure (mitigated by fallback empty notes) |
| **Analyst** | Weighs claims, evaluates trade-offs, and assesses citation risk | `research_notes` | `analysis_notes` | Inaccurate risk rating (mitigated by Critic check) |
| **Writer** | Synthesizes a structured report with markdown and bracketed citations | `research_notes`, `analysis_notes`, `sources` | `final_answer` | Missing citations or formatting errors (mitigated by Critic feedback) |
| **Critic** | Evaluates final draft against research notes for truthfulness and citations | `research_notes`, `final_answer` | `approved` status, review text | False approval / pedantic loops (mitigated by revision limit) |

## Shared state

- `request`: Contains the query string, maximum sources, and target audience, ensuring all agents have the correct query context.
- `iteration`: Tracks the total routing hops to enforce global budget limits.
- `route_history`: Logs the sequence of agents called to trace performance and debug.
- `sources`: Stores raw source documents to maintain a persistent citation source.
- `research_notes`: Shared facts for the Analyst and Writer to build upon.
- `analysis_notes`: Critically analyzed claims and risks for the Writer to integrate.
- `final_answer`: Stores the current draft or the approved final markdown report.
- `agent_results`: Captures structured outputs (content, tokens, status) for cost estimation and auditing.
- `trace`: Stores performance timings of individual spans.
- `errors`: Collects warnings and errors for graceful degradation.

## Routing policy

```
           [User Query]
                │
                ▼
         ┌──────────────┐
  ┌─────►│  Supervisor  │◄────────────┐
  │      └──────┬───────┘             │
  │             │                     │
  │             ├─────────► researcher│
  │             ├─────────► analyst   │
  │             ├─────────► writer    │
  │             ├─────────► critic ───┘ (if rejected, reset final_answer -> writer)
  │             │
  │             ▼
  │          [done]
  └─────────────┘
```

## Guardrails

- **Max iterations**: Enforced in `SupervisorAgent` by comparing `state.iteration` to `settings.max_iterations` (default: 6), falling back to immediate exit.
- **Timeout**: Enforced on LLM client requests using the `timeout` parameter in `urlopen` set to `settings.timeout_seconds` (default: 60s).
- **Retry**: Handled implicitly by LLM network failure catch blocks, with exceptions added to `state.errors`.
- **Fallback**: If an agent fails or iterations run out, the system degrades gracefully by outputting a fallback draft using whatever notes were collected.
- **Validation**: Strict schema constraints using Pydantic models for all agent results and intermediate transfers.

## Benchmark plan

- **Query**: "Compare single-agent and multi-agent workflows for customer support"
- **Metrics**:
  - **Latency (seconds)**: Measuring wall-clock execution time.
  - **Estimated Cost (USD)**: Calculated based on actual prompt and completion tokens (GPT-3.5 pricing model).
  - **Quality (0-10)**: Estimated automatically by presence of notes, citations, and completion status.
  - **Citation Coverage**: Number of sources included in citations vs total sources retrieved.
- **Expected Outcome**: The multi-agent workflow should have higher quality score and citation coverage compared to the single-agent baseline, but at the expense of higher latency and token costs.

