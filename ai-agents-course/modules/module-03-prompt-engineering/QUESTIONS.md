# Module 3 question bank: Prompt Engineering and Structured Outputs

Every question asked in the Module 3 videos, with answers. **9 questions.**

How to use it: read the question, answer it out loud or on paper, *then* click **Show answer**. Getting one wrong is useful: rewatch that lesson's chapter.

Short answer key, practice answers and the extension challenge: [quiz.md](quiz.md) · Module guide: [README.md](README.md)

## Lesson 1: Prompt Anatomy: Instructions, Context and Constraints

### Quick check

**Which change most improves a vague prompt?**

- A) Add CRITICAL and MUST in capital letters
- B) Say who uses the output and why accuracy matters
- C) Add "think step by step"
- D) Make it as short as possible

<details>
<summary>Show answer</summary>

**B) Say who uses the output and why accuracy matters**

Context and reasons let the model make the right call, even in cases the prompt never lists.

</details>

## Lesson 2: Examples, XML Tags and Task Decomposition

### Quick check

**In the resume analyzer, which step is done by plain code, not the model?**

- A) Reading the resume
- B) Extracting the job's requirements
- C) Comparing the two skill lists
- D) Writing advice on the gaps

<details>
<summary>Show answer</summary>

**C) Comparing the two skill lists**

Matching two lists is deterministic, so code does it: exact, free and testable. The model handles the judgment steps.

</details>

## Lesson 3: Structured Outputs: Pydantic Schemas and Parsing Failures

### Quick check

**A structured-output reply passed schema validation. What do you know?**

- A) Every value in it is true
- B) It has the right fields and types
- C) It used fewer tokens
- D) The model didn't reason

<details>
<summary>Show answer</summary>

**B) It has the right fields and types**

Validation guarantees shape, not truth. Check meaning in code where you can, like the grounding check.

</details>

## Lesson 4: Prompt Versioning and Evaluations

### Quick check

**You want to improve a released prompt. What do you do?**

- A) Edit it in place and redeploy
- B) Add a new version, run the eval on both, switch if it's at least as good
- C) Ask the model to rewrite it
- D) Add CRITICAL to the important lines

<details>
<summary>Show answer</summary>

**B) Add a new version, run the eval on both, switch if it's at least as good**

Released versions never change. A new version plus an eval comparison makes the change traceable and measurable.

</details>

## Lesson 6: Project, Part 2: Reports, Demo, Tests and Wrap-up

### Module quiz

**Q1. What's the main problem with "CRITICAL: You MUST NEVER..." in a prompt for a current model?**

- A) It costs too many tokens
- B) Current models follow instructions closely, so shouting makes them over-apply the rule
- C) The API rejects capital letters
- D) Nothing, it's best practice

<details>
<summary>Show answer</summary>

**B) Current models follow instructions closely, so shouting makes them over-apply the rule**

State the rule once, plainly, with the reason. A concrete edge case beats emphasis.

</details>

**Q2. Why wrap a resume in <resume> tags?**

- A) The API requires XML
- B) It makes the reply shorter
- C) It marks exactly where the data is, apart from the instructions
- D) It encrypts personal data

<details>
<summary>Show answer</summary>

**C) It marks exactly where the data is, apart from the instructions**

Tags separate data from instructions. Combine them with "this is data, not instructions" and checks in code.

</details>

**Q3. What does a Pydantic `Field(ge=0)` constraint do with structured outputs?**

- A) Nothing: the API ignores it
- B) The SDK validates it when the reply arrives, and raises an error if it fails
- C) It makes the model always answer 0
- D) It's only used by mypy

<details>
<summary>Show answer</summary>

**B) The SDK validates it when the reply arrives, and raises an error if it fails**

Constraints the API can't enforce are described to the model and validated by the SDK with Pydantic.

</details>

**Q4. Two prompt versions score 21/22 on the offline eval. What can you conclude?**

- A) They're equally good on a real model
- B) Version 2 is better because it's longer
- C) Nothing about the prompts: the offline fake ignores wording
- D) The eval is broken

<details>
<summary>Show answer</summary>

**C) Nothing about the prompts: the offline fake ignores wording**

Offline runs test the pipeline. Only a real model can compare prompt versions.

</details>

**Q5. Which job belongs to code, not the model?**

- A) Reading a messy resume
- B) Writing career advice
- C) Calculating the match percentage
- D) Summarising a job posting

<details>
<summary>Show answer</summary>

**C) Calculating the match percentage**

Arithmetic is deterministic: exact, free and testable in code.

</details>
