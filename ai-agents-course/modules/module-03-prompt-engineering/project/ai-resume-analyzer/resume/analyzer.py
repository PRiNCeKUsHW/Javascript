from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Literal, TypeVar

import anthropic
import pydantic

from resume.errors import AnalyzerError
from resume.models import CandidateProfile, JobRequirements, Suggestions
from resume.pricing import CostTracker
from resume.prompts import Prompt, get_prompt
from resume.skills import grounded, normalize

FALLBACK_BETA = "server-side-fallback-2026-07-01"
T = TypeVar("T", bound=pydantic.BaseModel)
Effort = Literal["low", "medium", "high"]


@dataclass
class Call:
    """One model call: which prompt, how many tokens, what it cost."""

    prompt: str
    fingerprint: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


@dataclass
class GapReport:
    profile: CandidateProfile
    job: JobRequirements
    matched: list[str]
    missing_must: list[str]
    missing_nice: list[str]
    dropped: list[str]
    suggestions: Suggestions | None = None
    calls: list[Call] = field(default_factory=list)

    @property
    def score(self) -> int:
        """Percent of must-have skills the candidate has."""
        total = len(self.job.must_have)
        return 100 if total == 0 else round(100 * len(self.matched) / total)

    @property
    def years_short(self) -> int:
        return max(0, self.job.min_years - self.profile.years_experience)


@contextmanager
def friendly_errors() -> Iterator[None]:
    """Turn SDK exceptions into one clear AnalyzerError each."""
    try:
        yield
    except anthropic.AuthenticationError:
        raise AnalyzerError("the API key was rejected: check "
                            "ANTHROPIC_API_KEY") from None
    except anthropic.RateLimitError:
        raise AnalyzerError("rate limited, even after retries: wait and "
                            "try again") from None
    except anthropic.APIConnectionError:
        raise AnalyzerError("could not reach the API: check your "
                            "connection") from None
    except anthropic.APIStatusError as exc:
        raise AnalyzerError(f"the API failed with status "
                            f"{exc.status_code}") from None


def compare(profile: CandidateProfile, job: JobRequirements
            ) -> tuple[list[str], list[str], list[str]]:
    """Plain code, no model: (matched, missing must-have, missing nice)."""
    have = {normalize(s) for s in profile.skills}
    matched = [s for s in job.must_have if normalize(s) in have]
    missing_must = [s for s in job.must_have if normalize(s) not in have]
    missing_nice = [s for s in job.nice_to_have if normalize(s) not in have]
    return matched, missing_must, missing_nice


class Analyzer:
    def __init__(self, client: anthropic.Anthropic, model: str,
                 tracker: CostTracker,
                 versions: dict[str, str] | None = None) -> None:
        self.client = client
        self.model = model
        self.tracker = tracker
        self.versions = versions or {}
        self.calls: list[Call] = []

    def prompt(self, name: str) -> Prompt:
        return get_prompt(name, self.versions.get(name))

    def _structured(self, name: str, output_format: type[T], effort: Effort,
                    **values: str) -> T:
        """One prompt in, one validated object out, or one clear error."""
        self.tracker.check()
        prompt = self.prompt(name)
        try:
            with friendly_errors():
                response = self.client.beta.messages.parse(
                    model=self.model, betas=[FALLBACK_BETA],
                    fallbacks="default", max_tokens=8000,
                    system=prompt.system, output_format=output_format,
                    output_config={"effort": effort},
                    messages=[{"role": "user",
                               "content": prompt.render(**values)}])
        except pydantic.ValidationError as exc:
            first = exc.errors()[0]
            if first["type"] == "json_invalid":    # usually cut off mid-JSON
                raise AnalyzerError(f"{prompt.label}: the reply is not "
                                    "complete JSON (cut off?)") from None
            where = ".".join(str(p) for p in first["loc"])
            raise AnalyzerError(
                f"{prompt.label}: the reply did not fit the schema "
                f"({where}: {first['msg']})") from None
        usage = response.usage
        cost = self.tracker.add(self.model, usage.input_tokens,
                                usage.output_tokens)
        self.calls.append(Call(prompt.label, prompt.fingerprint,
                               usage.input_tokens, usage.output_tokens, cost))
        if response.stop_reason == "refusal":
            raise AnalyzerError(f"{prompt.label}: the model declined")
        if response.stop_reason == "max_tokens" \
                or response.parsed_output is None:
            raise AnalyzerError(f"{prompt.label}: the reply was cut off")
        return response.parsed_output

    def extract_profile(self, resume: str) -> tuple[CandidateProfile,
                                                    list[str]]:
        """Extract, then keep only skills the resume really names."""
        profile = self._structured("extract_profile", CandidateProfile,
                                   "low", resume=resume)
        kept, dropped = grounded(profile.skills, resume)
        return profile.model_copy(update={"skills": kept}), dropped

    def extract_job(self, job: str) -> JobRequirements:
        return self._structured("extract_job", JobRequirements, "low",
                                job=job)

    def suggest(self, report: GapReport) -> Suggestions:
        return self._structured(
            "suggest", Suggestions, "medium", title=report.job.title,
            skills=", ".join(report.profile.skills) or "none",
            missing_must=", ".join(report.missing_must) or "none",
            missing_nice=", ".join(report.missing_nice) or "none")

    def analyze(self, resume: str, job_text: str,
                with_advice: bool = True) -> GapReport:
        """Extract (model), compare (code), then advise (model) on gaps."""
        profile, dropped = self.extract_profile(resume)
        job = self.extract_job(job_text)
        report = GapReport(profile, job, *compare(profile, job), dropped)
        if with_advice and (report.missing_must or report.missing_nice):
            report.suggestions = self.suggest(report)
        report.calls = list(self.calls)
        return report
