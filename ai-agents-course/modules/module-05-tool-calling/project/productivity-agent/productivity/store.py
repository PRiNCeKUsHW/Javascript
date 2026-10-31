"""Tasks and notes, kept in one JSON file.

Every save writes a temporary file first and then replaces the real one, so a
crash in the middle of a write never leaves half a file behind.
"""
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class Task:
    id: int
    title: str
    due: str | None          # ISO date, e.g. "2026-11-05"
    priority: str            # low, normal or high
    done: bool = False


@dataclass
class Note:
    id: int
    title: str
    text: str


class Store:
    def __init__(self, path: Path) -> None:
        self.path = path

    # ------------------------------------------------------------ file access
    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"tasks": [], "notes": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: dict[str, Any]) -> None:
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(tmp, self.path)       # atomic: old file or new file, never half

    @staticmethod
    def _next_id(items: list[dict[str, Any]]) -> int:
        return max((item["id"] for item in items), default=0) + 1

    def reset(self) -> None:
        self._save({"tasks": [], "notes": []})

    # ------------------------------------------------------------ tasks
    def add_task(self, title: str, due: str | None, priority: str) -> Task:
        data = self._load()
        task = Task(self._next_id(data["tasks"]), title, due, priority)
        data["tasks"].append(asdict(task))
        self._save(data)
        return task

    def tasks(self, status: str = "open") -> list[Task]:
        tasks = [Task(**t) for t in self._load()["tasks"]]
        if status == "open":
            return [t for t in tasks if not t.done]
        if status == "done":
            return [t for t in tasks if t.done]
        return tasks

    def get_task(self, task_id: int) -> Task:
        for t in self._load()["tasks"]:
            if t["id"] == task_id:
                return Task(**t)
        raise LookupError(f"there is no task {task_id}")

    def complete_task(self, task_id: int) -> Task:
        data = self._load()
        for t in data["tasks"]:
            if t["id"] == task_id:
                t["done"] = True
                self._save(data)
                return Task(**t)
        raise LookupError(f"there is no task {task_id}")

    def delete_task(self, task_id: int) -> Task:
        data = self._load()
        for i, t in enumerate(data["tasks"]):
            if t["id"] == task_id:
                del data["tasks"][i]
                self._save(data)
                return Task(**t)
        raise LookupError(f"there is no task {task_id}")

    # ------------------------------------------------------------ notes
    def add_note(self, title: str, text: str) -> Note:
        data = self._load()
        note = Note(self._next_id(data["notes"]), title, text)
        data["notes"].append(asdict(note))
        self._save(data)
        return note

    def notes(self) -> list[Note]:
        return [Note(**n) for n in self._load()["notes"]]

    def search_notes(self, query: str) -> list[Note]:
        q = query.lower()
        return [n for n in self.notes()
                if q in n.title.lower() or q in n.text.lower()]
