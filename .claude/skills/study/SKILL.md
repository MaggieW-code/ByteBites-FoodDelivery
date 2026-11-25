---
name: study
description: Study a workflow, pattern, tool, or concept with a bottom-up lesson - the problem it solves, first principles, the industry standard and its alternatives, how ByteBites uses it, pitfalls, and how to explain it to a teammate. Use when asked to explain, teach, "why do we", "how does X work", or before adopting a new pattern or library.
argument-hint: "<topic>"
---

# Study a topic from the bottom up

Topic: `$ARGUMENTS`

Goal: the learner can explain and defend this to a teammate without AI help. Start short,
then go deep. Use plain words; define every term the first time it appears.

Find ByteBites context README-first (`AGENTS.md` AGENT RULES): read the README of each
relevant folder, then open only the source files you need.

## Structure

1. **Quick version** (3 lines max): what it is and when you'd use it.
2. **The problem first:** what goes wrong without it. Use a concrete failure, ideally from
   this repo (search the code; cite `path:line`).
3. **First principles:** the smallest mental model that explains how it works. One diagram
   or short code example if it helps.
4. **The industry standard:** what professional teams use, and why it became the standard.
5. **Alternatives and trade-offs:** a table with the KISS option and at least one other,
   each with when it wins and what it costs. Recommend one for this repo and say why.
6. **In ByteBites:** where it already exists or would go, which `AGENTS.md` rule or README
   it connects to, and which layers of the vertical stack it touches.
7. **Pitfalls:** the 2-4 mistakes people actually make, and how to spot them.
8. **Explain it to a teammate:** one quoted sentence they could say in a meeting.
9. **Check understanding:** 2-3 questions the learner should be able to answer, with
   answers hidden under a "Answers" heading at the end.
10. **Learn more:** 1-3 sources, official documentation first. Only cite pages you have
    actually read in this session; otherwise name the documentation without a link.

## Rules

- Don't change any code while teaching. If the topic suggests a change, label it a fix or a
  proposal (`AGENTS.md` AGENT RULES) and offer it at the end.
- Prefer one worked example from this codebase over several generic ones.
- If the learner asks a follow-up, go one level deeper on that point only.
