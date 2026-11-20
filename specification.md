# Clinic Visit Sorter - One-Page Specification

## Purpose

The Clinic Visit Sorter is a console-based Python tool for a college health-centre queue. It reads short arrival notes, labels each note, and orders the queue so the most urgent students appear first.

## What the tool must never do

The tool must never diagnose, give medical advice, recommend treatment, or remove a student from the queue. The nurse sees every student and makes every medical decision.

## Input

The input file is `visits.csv` with:

    id,time,note

It contains at least 20 short, informal notes. Notes may be written in English, Tamil, or Tanglish.

## LLM JSON

For every note the LLM must return:

    {
      "category": "injury",
      "priority": "today",
      "summary": "Twisted ankle, swelling, difficulty walking"
    }

Allowed categories:
`injury`, `fever_cold`, `stomach`, `pain`, `allergy`, `other`

Allowed priorities:
`see_now`, `today`, `routine`

The summary describes symptoms only, has 12 words or fewer, contains no disease name, no diagnosis or guess, and no person's name.

## Red flags

Python checks for chest pain, breathing trouble, fainting, heavy bleeding, lip/face swelling, pain so bad the student cannot stand, and Tamil/Tanglish red flags such as `nenju vali` and `moochu`.

If a red flag is present, Python sets priority to `see_now`.

Python may only raise priority; it never lowers it.

## No diagnosis

If a returned summary contains a disease name or words such as `possible` or `likely`, Python replaces it with a neutral symptom summary.

## API failure

The program checks every LLM reply. It retries once after an API error or invalid reply. If both attempts fail, it uses `today` rather than `routine`, and still runs the red-flag check.

## Edge cases

The program handles missing/invalid API responses, invalid JSON fields, empty notes, unknown categories/priorities, diagnosis-like summaries, Tamil/Tanglish red flags, and API failure.

## Outputs

`nurse_queue.csv` contains every student, the original note, category, priority and summary, ordered by urgency and arrival time.

`summary.txt` contains counts by priority, category and hour of arrival. It contains no visit notes.
