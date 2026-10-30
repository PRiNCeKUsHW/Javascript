# Teaching style (the learner's own brief, 2026-10-30)

Every lesson script, from the remakes of Modules 1-4 onward, follows this. The learner's goal is
deep understanding and interview confidence, not memorizing answers.

## Language
- Simple, natural English, like a patient senior developer mentoring a junior.
- Keep terms accurate, but explain every unfamiliar term the first time (and add it to `GLOSSARY.md`).
- Never treat a question as too basic. No academic jargon.

## Every concept: What → Why → How → Where → Practice
1. **What** it is, in one or two plain sentences.
2. **Why** it exists: the problem it solves (show the problem first when possible).
3. **How** it works inside, step by step (diagram or dry-run table when it helps).
4. **Where** developers use it, and when not to.
5. **Practice**: a small runnable Python example, then the project code.

Never show complicated code before the idea behind it.

## Analogies
Use a real-life analogy for abstract ideas (API = waiter between customer and kitchen,
cache = keeping things within reach), then connect it back to the real concept explicitly.
Skip the analogy when a direct explanation is clearer.

## Code
- Simple version first, better version after, and say why it's better.
- Explain every important line: input, processing, output.
- Split screen (`run` scene): code on the left, real output on the right, each line tied to what it printed.
- Dry runs: a table of variables changing step by step for loops and agent turns.
- Mention time/space cost when it matters.

## Interview perspective (each module)
- Common interview questions, what the interviewer expects, and traps.
- Differences between similar concepts (e.g. workflow vs agent).
- Follow-up questions an interviewer might ask.
- A short, interview-ready answer the learner can say out loud.

## Pace and structure
- One idea at a time; never skip an intermediate step; brief prerequisite refreshers.
- Don't keep asking "did you understand?": finish the explanation, then give practice.

## End of every substantial lesson
1. Short recap.
2. 3-5 practice questions, easy to hard (answers not revealed in the same breath; answers go in the
   module's `quiz.md`).
3. One real-world scenario.
4. A few interview questions.
5. Key takeaways.

## Honesty
- Say when something is version-dependent or uncertain.
- Explain trade-offs when there are several approaches.
- Never fabricate output: every terminal output in a video is a real run.
