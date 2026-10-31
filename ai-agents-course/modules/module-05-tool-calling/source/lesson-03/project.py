"""Lets the lesson scripts import the project's `productivity` package."""
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2] / "project/productivity-agent"
sys.path.insert(0, str(PROJECT))
