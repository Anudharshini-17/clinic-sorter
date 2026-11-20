# Clinic Visit Sorter - Groq API

## 1. Project purpose

Clinic Visit Sorter is a console-based Python project for a college health-centre queue.

It reads short student arrival notes, asks an LLM to classify each note, validates the response, applies Python red-flag rules, and writes:

- `nurse_queue.csv` - every student ordered by urgency and arrival time
- `summary.txt` - counts by priority, category and hour; no notes

The program does not diagnose, give medical advice, or remove students from the queue.

## 2. Project files

- `main.py` - complete application
- `system_prompt.txt` - five-role system prompt
- `visits.csv` - sample input with 24 notes
- `evaluate.py` - five-case evaluation harness
- `red_team.py` - three red-team tests
- `judgment_framework.md` - Judgment Framework
- `cost_latency.md` - cost and latency note
- `ai_decision_journal.md` - AI Decision Journal
- `reflection.md` - 400-word reflection
- `specification.md` - one-page project specification
- `requirements.txt` - Python packages
- `.env.example` - safe API-key template
- `.gitignore` - prevents `.env` from being committed

## 3. Requirements

Python 3.7+ and a Groq API key.

Groq's official Python setup uses the `groq` package and the `GROQ_API_KEY`
environment variable. The key must not be hardcoded.

## 4. Windows setup

Open Command Prompt in this project folder.

Install packages:

    py -m pip install -r requirements.txt

Create the environment file:

    copy .env.example .env

Open `.env` in Notepad and replace:

    PASTE_YOUR_GROQ_API_KEY_HERE

with your actual key.

Do not put quotes around the key unless needed by your shell.

## 5. Test the API

Run:

    py main.py

The program reads `visits.csv` and writes `nurse_queue.csv` and `summary.txt`.

## 6. Run evaluation

    py evaluate.py

## 7. Run red-team tests

    py red_team.py

## 8. Git

Before the first commit, verify:

    git status

Make sure `.env` is not listed as a file to commit.

Then:

    git init
    git add .
    git commit -m "Create Clinic Visit Sorter"
    git log --oneline

After making a meaningful change:

    git add .
    git commit -m "Add validation and red flag checks"

Third example:

    git add .
    git commit -m "Add evaluation and red team tests"

## 9. Important project rule

The nurse is the human checkpoint. The software only sorts the queue.
The nurse sees every student and makes every medical decision.

## 10. Explain every line

For the showcase, be able to explain:
- why the API key is in `.env`
- what `load_visits()` does
- why `classify()` retries once
- how `is_valid()` checks the LLM response
- why `raise_priority()` can only increase urgency
- how `remove_diagnosis()` prevents diagnosis-like summaries
- how sorting orders `see_now`, `today`, then `routine`
- what `write_reports()` produces
