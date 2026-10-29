"""Create or update COURSE_MANIFEST.json (the machine-readable progress record).

usage:
  python tools/manifest.py init                      # create it if missing (all NOT_STARTED)
  python tools/manifest.py set 1 STATUS [key=value]  # update a module after real checks
  python tools/manifest.py show
Statuses: NOT_STARTED, IN_PROGRESS, VALIDATION_FAILED, READY, COMPLETED.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "COURSE_MANIFEST.json"
STATUSES = {"NOT_STARTED", "IN_PROGRESS", "VALIDATION_FAILED", "READY", "COMPLETED"}

MODULES = [
    (1, "Python for AI Engineering", "Python AI Toolkit", "I — Foundations"),
    (2, "LLM Fundamentals and API Integration", "AI Study Assistant", "I — Foundations"),
    (3, "Prompt Engineering and Structured Outputs", "AI Resume Analyzer", "I — Foundations"),
    (4, "AI Agent Architecture", "Smart Calculator Agent", "II — Build Agents from Scratch"),
    (5, "Tool Calling and Function Execution", "Personal Productivity Agent", "II — Build Agents from Scratch"),
    (6, "Agent Memory and Conversation State", "Persistent AI Study Companion", "II — Build Agents from Scratch"),
    (7, "Reliable and Efficient Agents", "Resilient API Agent", "II — Build Agents from Scratch"),
    (8, "Model Context Protocol (MCP)", "Restricted File Assistant MCP Server", "III — Knowledge and Tool Connectivity"),
    (9, "Embeddings and Vector Search", "Semantic Search Engine", "III — Knowledge and Tool Connectivity"),
    (10, "Retrieval-Augmented Generation (RAG)", "Chat With Your PDFs", "III — Knowledge and Tool Connectivity"),
    (11, "LangGraph Fundamentals", "AI Content Workflow", "IV — Advanced Orchestration"),
    (12, "Multi-Agent Systems", "AI Research Team", "IV — Advanced Orchestration"),
    (13, "Web Research and Automation Agents", "Research Assistant", "IV — Advanced Orchestration"),
    (14, "Testing and Evaluation of AI Agents", "AI Agent Evaluation Suite", "V — Quality and Security"),
    (15, "AI Agent Security", "Secure Document Agent", "V — Quality and Security"),
    (16, "FastAPI for AI Applications", "Authenticated AI Agent API", "VI — Production"),
    (17, "Docker, Deployment, and Monitoring", "Deployed AI Agent API", "VI — Production"),
    (18, "Full-Stack AI Agent Application", "Production AI Workspace", "VI — Production"),
]


def load():
    return json.loads(PATH.read_text())


def save(m):
    m["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    PATH.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")


def init():
    if PATH.exists():
        return
    save({
        "course": "AI Agents with Python — Beginner to Production (2026)",
        "language": "en",
        "video": {"width": 1920, "height": 1080, "fps": 60, "codec": "h264", "audio": "aac"},
        "design_system": "COURSE_DESIGN_SYSTEM.md",
        "next_module": 1,
        "modules": [{"number": n, "title": t, "part": part, "project": p, "status": "NOT_STARTED",
                     "lessons": [], "paths": {}, "validation": None, "render": None, "blockers": []}
                    for n, t, p, part in MODULES],
        "optional_capstones": ["AI Research Assistant", "Enterprise Knowledge Assistant",
                               "AI Workflow Automation Platform"],
    })


def set_status(n, status, extras):
    assert status in STATUSES, status
    m = load()
    mod = m["modules"][n - 1]
    mod["status"] = status
    for kv in extras:
        k, v = kv.split("=", 1)
        mod[k] = json.loads(v) if v[:1] in "[{\"" or v in ("true", "false", "null") or v.isdigit() else v
    done = [x["number"] for x in m["modules"] if x["status"] == "COMPLETED"]
    m["next_module"] = next((x["number"] for x in m["modules"] if x["status"] != "COMPLETED"), None)
    save(m)
    print(f"module {n}: {status}; completed: {done}; next: {m['next_module']}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "init":
        init()
    elif cmd == "set":
        set_status(int(sys.argv[2]), sys.argv[3], sys.argv[4:])
    elif cmd == "show":
        for x in load()["modules"]:
            print(f"{x['number']:>2} {x['status']:<18} {x['title']}")
