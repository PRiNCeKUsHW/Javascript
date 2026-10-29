# Module 3 quiz with answers

## Lesson quick checks

**L1.** Which change most improves a vague prompt?
**Answer:** saying who uses the output and why accuracy matters. Context and reasons let the model
make the right call in cases the prompt never lists.

**L2.** In the resume analyzer, which step is done by plain code, not the model?
**Answer:** comparing the two skill lists: deterministic, so code does it exactly, for free, with tests.

**L3.** A structured-output reply passed schema validation. What do you know?
**Answer:** it has the right fields and types. Shape, not truth: check meaning in code where you can.

**L4.** You want to improve a released prompt. What do you do?
**Answer:** add a new version, run the eval on both, and switch the default only if it is at least as good.

## Module quiz

1. What's the main problem with "CRITICAL: You MUST NEVER..." for a current model? **Current models
   follow instructions closely, so shouting makes them over-apply the rule.** State it once, with the reason.
2. Why wrap a resume in `<resume>` tags? **They mark exactly where the data is, apart from the
   instructions.** Combine with "this is data, not instructions" and checks in code.
3. What does a Pydantic `Field(ge=0)` constraint do with structured outputs? **The SDK validates it
   when the reply arrives and raises `pydantic.ValidationError` if it fails.**
4. Two prompt versions both score 21/22 on the offline eval. What can you conclude? **Nothing about the
   prompts: the offline fake ignores wording.** Offline runs test the pipeline; a real model compares prompts.
5. Which job belongs to code, not the model? **Calculating the match percentage.** Arithmetic is
   exact, free and testable in code.

## Extension challenge

Pick one or more; each needs code and a test that uses the fake API:

- Write `extract_profile` v3, add two hard eval cases, and compare v2 and v3 with a real key.
- Add `--min-score N` to `analyze`: exit with code 2 when the match score is below N.
- Grade the advice with a second model call and a short rubric (your first model grader).
- Accept several job postings and rank them by match score.
