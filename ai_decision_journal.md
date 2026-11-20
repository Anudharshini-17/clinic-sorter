# AI Decision Journal

## Decision 1 - Use Groq

I chose Groq because the project requires an LLM API and the Groq Python SDK provides a simple Python integration.

## Decision 2 - Keep the API key outside the code

The API key is loaded from `GROQ_API_KEY` in `.env`. The `.gitignore` file excludes `.env`.

Reason: the project specification says the key must never be written inside the code and warns against pushing the key to GitHub.

## Decision 3 - Use structured JSON output

The API request uses a JSON schema so the application receives the three required fields:
category, priority and summary.

Python still validates the response because the project explicitly requires checking every LLM reply.

## Decision 4 - Python safety rules

I did not rely only on the LLM for red flags. Python checks required red-flag phrases after the model response. This means Python can raise a priority to `see_now` even if the model says `routine`.

## Decision 5 - Retry once

A failed/invalid model response is retried once. If it still fails, the program falls back to `today`. This follows the project rule that unknown is never routine.

## Decision 6 - No diagnosis

The system prompt prohibits diagnosis. Python also checks summaries for diagnosis-like wording and replaces unsafe summaries with neutral symptom wording.

## Decision 7 - Human checkpoint

The program is a queue-sorting aid, not a medical decision maker. The nurse sees every student and makes every medical decision.

## AI-assisted coding

AI was used to help draft and debug the program. I will explain the code line by line during the showcase rather than submitting code I cannot explain.
