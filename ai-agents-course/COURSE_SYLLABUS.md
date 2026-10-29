# AI Agents with Python — Beginner to Production (2026)

Canonical syllabus. Modules are produced strictly in this order, one per request.
Every module ends with a fully implemented, tested practical project.

## Part I — Foundations

1. **Python for AI Engineering** — variables, data types, lists, dicts, sets, functions, classes,
   exceptions; modules, packages, files, JSON, environment variables, virtual environments, pip,
   project structure; type hints, HTTP requests, introductory async/await.
   *Project: Python AI Toolkit* — CLI that reads and validates JSON, processes data, generates reports.
2. **LLM Fundamentals and API Integration** — what LLMs do, tokens, context windows, prompts,
   generation; API requests, message history, structured output, output limits; API keys, rate
   limits, retries, costs, error handling. *Project: AI Study Assistant* (explanations + structured quizzes).
3. **Prompt Engineering and Structured Outputs** — instruction design, context, examples,
   constraints, task decomposition; reusable prompts, JSON outputs, Pydantic validation, parsing
   failures; prompt versioning and basic evaluations. *Project: AI Resume Analyzer* (skills-gap report).

## Part II — Build Agents from Scratch

4. **AI Agent Architecture** — chatbots vs workflows vs agents; models, instructions, tools, state,
   the agent loop; decide, act, observe, continue, stop. *Project: Smart Calculator Agent*.
5. **Tool Calling and Function Execution** — tool schemas, dispatch, arguments, results, multiple
   tools; external APIs, internal functions, validation, timeouts, permissions; human confirmation.
   *Project: Personal Productivity Agent* (calculator, notes search, read-only task lookup).
6. **Agent Memory and Conversation State** — history, short-term state, persistent memory,
   summarization; SQLite/PostgreSQL; user isolation, privacy, retention, deletion.
   *Project: Persistent AI Study Companion*.
7. **Reliable and Efficient Agents** — async, retries, backoff, timeouts, caching, rate limits;
   loop prevention, step limits, token budgets, logging, tracing. *Project: Resilient API Agent*.

## Part III — Knowledge and Tool Connectivity

8. **Model Context Protocol (MCP)** — hosts, clients, servers, tools, resources, prompts; Python
   server and client; transports, configuration, authorization, permissions.
   *Project: Restricted File Assistant MCP Server*.
9. **Embeddings and Vector Search** — embeddings, similarity, chunking, overlap, metadata,
   retrieval; indexing, top-k, filters, relevance. *Project: Semantic Search Engine*.
10. **Retrieval-Augmented Generation (RAG)** — ingestion, parsing, chunking, indexing, retrieval,
    generation; citations, query rewriting, grounded answers; missing information, retrieval
    evaluation. *Project: Chat With Your PDFs* (with source references).

## Part IV — Advanced Orchestration

11. **LangGraph Fundamentals** — state, nodes, edges, routing, cycles, checkpoints; persistence,
    interrupts, human approval, resumption. *Project: AI Content Workflow*.
12. **Multi-Agent Systems** — planner, researcher, executor, reviewer, handoffs, shared state;
    sequential and parallel; coordination failures, cost, latency, when not to use multi-agent.
    *Project: AI Research Team*.
13. **Web Research and Automation Agents** — permitted search APIs, browser automation,
    extraction, source comparison, citations; rate limits, terms, safe operation, confirmation.
    *Project: Research Assistant* (cited research brief).

## Part V — Quality and Security

14. **Testing and Evaluation of AI Agents** — unit tests, mocks, datasets, regression tests,
    expected outcomes; tool selection, retrieval and answer quality, evaluation reports.
    *Project: AI Agent Evaluation Suite*.
15. **AI Agent Security** — prompt injection, untrusted documents, secrets, least privilege;
    allowlists, validation, sandboxing, data leakage, authorization, audit logs.
    *Project: Secure Document Agent* (with adversarial test cases).

## Part VI — Production

16. **FastAPI for AI Applications** — REST, Pydantic, validation, authn/authz, exceptions;
    streaming, persistence, PostgreSQL, migrations, API docs. *Project: Authenticated AI Agent API*.
17. **Docker, Deployment, and Monitoring** — Dockerfiles, containers, config, secrets, health
    checks, logging; CI/CD, cloud deployment, monitoring, costs, scaling.
    *Project: Deploy the AI Agent API* (Docker + documented deployment workflow).
18. **Full-Stack AI Agent Application** — architecture, frontend, auth, state, retrieval, tools;
    rate limiting, usage tracking, observability, testing, deployment.
    *Project: Production AI Workspace* (research, document Q&A, task planning, human approval).

## Optional capstones (only on request, after Module 18)

1. AI Research Assistant
2. Enterprise Knowledge Assistant
3. AI Workflow Automation Platform
