# Cost and Latency Note

## API call count

For `N` visits, the normal path uses one Groq API call per visit.

The program retries once when a response fails validation or the API raises an error.

Therefore:
- normal maximum: approximately `N` calls
- worst case with one retry for every visit: `2N` calls

For the included 24-visit sample:
- normal: 24 calls
- worst case: 48 calls

## Latency

Latency depends on Groq model load, network speed, prompt size, and response length. The program processes notes one at a time, so the total run time is approximately the sum of the individual calls plus local Python processing.

Record the actual time from your own run if your faculty asks for measured latency.

## Cost

The exact cost depends on the model's current Groq pricing and the number of input/output tokens. This project uses `openai/gpt-oss-20b`.

A simple estimate is:

    daily_cost =
        (input_tokens / 1,000,000) * input_price
        +
        (output_tokens / 1,000,000) * output_price

Use the current Groq model/pricing page when completing the final measured figure, because prices and model availability can change.

The project deliberately keeps the prompt and response short to reduce token usage.

## What to report at the showcase

Write down:
1. Number of visits processed.
2. Number of API calls.
3. Number of retries.
4. Average time per call.
5. Total run time.
6. Current model pricing used for the calculation.
7. Estimated cost for one day's input.
