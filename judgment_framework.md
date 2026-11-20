# Judgment Framework

| Part | What can go wrong? | Why does it matter? | Human / Python checkpoint |
|---|---|---|---|
| Input loading | Missing or empty fields | A malformed visit should not silently disappear | `load_visits()` validates required columns and skips unusable rows |
| LLM category | Wrong category | The nurse may see a less useful grouping | `is_valid()` checks allowed categories; nurse remains decision-maker |
| LLM priority | Priority too low | A genuinely urgent student could wait behind routine requests | Python red-flag rule can raise to `see_now` |
| LLM priority | Priority too high | It may make the queue less efficient, but the student is still seen | The nurse reviews the full queue |
| LLM summary | Disease/guess wording | The project must not diagnose | `remove_diagnosis()` replaces unsafe summaries |
| API failure | No model response | The program must not crash or silently mark unknown as routine | Retry once, then fallback to `today` |
| Tamil/Tanglish | Red flag missed by model | Informal wording may still describe urgent symptoms | Python checks required Tamil/Tanglish red flags |
| Sorting | Wrong queue order | Urgent students could appear later | `write_reports()` sorts by priority rank then arrival time |
| Summary report | Notes included | The in-charge summary should contain counts only | `summary.txt` contains no notes |
| Human checkpoint | Software treated as final medical decision | Medical decisions require human judgment | Nurse sees every student and makes every medical decision |

## Why too-low priority is worse

A priority that is too low can delay attention for a student whose note contains a red flag. A priority that is too high is less serious for this project because the student is still seen and the nurse makes the final medical decision. Therefore the Python safety rule is one-way: it can raise priority but never lower it.

## Human checkpoint

**The nurse sees every student and makes every medical decision.**
