"""Lets the lesson scripts import the project's `resume` package."""
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2] / "project/ai-resume-analyzer"
sys.path.insert(0, str(PROJECT))
