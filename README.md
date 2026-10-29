# AI Agents with Python 2026: Beginner to Production

Source code for the YouTube course **AI Agents with Python 2026: Beginner to Production**:
18 modules that take you from Python basics to a deployed, tested, secure AI agent application.
Every module has narrated lesson videos, English captions, a fully working project with tests,
a quiz and an extension challenge.

> Arrived from a YouTube description? Each video links straight to its module folder below.

## Modules

| # | Module | Project | Status |
|---|--------|---------|--------|
| 1 | [Python for AI Engineering](ai-agents-course/modules/module-01-python-ai-engineering) | [Python AI Toolkit](ai-agents-course/modules/module-01-python-ai-engineering/project/python-ai-toolkit) | Published |
| 2 | [LLM Fundamentals and API Integration](ai-agents-course/modules/module-02-llm-fundamentals) | [AI Study Assistant](ai-agents-course/modules/module-02-llm-fundamentals/project/ai-study-assistant) | Published |
| 3 | Prompt Engineering and Structured Outputs | AI Resume Analyzer | Coming soon |
| 4 | AI Agent Architecture | Smart Calculator Agent | Coming soon |
| 5 | Tool Calling and Function Execution | Personal Productivity Agent | Coming soon |
| 6 | Agent Memory and Conversation State | Persistent AI Study Companion | Coming soon |
| 7 | Reliable and Efficient Agents | Resilient API Agent | Coming soon |
| 8 | Model Context Protocol (MCP) | Restricted File Assistant MCP Server | Coming soon |
| 9 | Embeddings and Vector Search | Semantic Search Engine | Coming soon |
| 10 | Retrieval-Augmented Generation (RAG) | Chat With Your PDFs | Coming soon |
| 11 | LangGraph Fundamentals | AI Content Workflow | Coming soon |
| 12 | Multi-Agent Systems | AI Research Team | Coming soon |
| 13 | Web Research and Automation Agents | Research Assistant | Coming soon |
| 14 | Testing and Evaluation of AI Agents | AI Agent Evaluation Suite | Coming soon |
| 15 | AI Agent Security | Secure Document Agent | Coming soon |
| 16 | FastAPI for AI Applications | Authenticated AI Agent API | Coming soon |
| 17 | Docker, Deployment, and Monitoring | Deployed AI Agent API | Coming soon |
| 18 | Full-Stack AI Agent Application | Production AI Workspace | Coming soon |

Full syllabus: [ai-agents-course/COURSE_SYLLABUS.md](ai-agents-course/COURSE_SYLLABUS.md)

## Run a project

You need Python 3.11 or newer. For example, the Module 2 project:

```bash
cd ai-agents-course/modules/module-02-llm-fundamentals/project/ai-study-assistant
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest                 # 23 tests, no API key needed
python -m study --offline explain "Python decorators"
```

Every project README has its own setup steps. From Module 2 on, the projects call the
Anthropic API. Each one also has an offline mode with a built-in fake API, so you can follow
along and run the tests without a key. To use a real model, copy `.env.example` to `.env`
and add your own `ANTHROPIC_API_KEY`. Never commit that file.

## Repository layout

```text
ai-agents-course/        the course: modules, projects, lesson scripts, captions, video tooling
  modules/module-NN-*/   one folder per module (README, project/, source/, quiz.md, captions/)
  studio/                Remotion project that renders the lesson videos
  tools/                 build, render and validation scripts
fastapi-course/          an earlier FastAPI course
bytetitan-ep14-counter/  "Python in 60 Seconds" short (HyperFrames)
hyperframes/, remotion/  video tooling experiments
01_basics/               early JavaScript practice
```

Rendered videos and narration audio are not stored in the repository. Watch the lessons on
YouTube, or rebuild them with the tools in `ai-agents-course/` (see its README).
