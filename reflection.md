# 400-Word Reflection

Building the Clinic Visit Sorter helped me understand that an AI application is not only about sending a prompt to a language model. The most important lesson was that the application needs its own rules around the model. In this project, the LLM suggests a category, priority and short summary, but Python validates the result and applies the safety rules.

One important design decision was keeping the Groq API key outside the source code. I used a `.env` file and added it to `.gitignore`. This prevents the secret from being included in the GitHub repository. I also learned that the API response should not be trusted automatically. The program checks the category, priority and summary before using them.

The red-flag rule was another important part of the project. A model could classify a note incorrectly, so Python checks for phrases such as chest pain, breathing difficulty, and the Tamil/Tanglish phrases `nenju vali` and `moochu`. If a red flag is found, Python raises the priority to `see_now`. Python never lowers a priority. This makes the rule easy to explain and test.

I also learned the importance of a fallback. If the API is unavailable or gives an invalid response twice, the program does not crash and does not mark the visit as routine. Instead, it uses `today` and still performs the Python red-flag check.

The project also changed how I think about summaries. The tool must never diagnose a student. Therefore, the summary is restricted to symptoms and Python removes diagnosis-like wording such as disease names, `possible`, or `likely`.

Testing was useful because normal examples do not show every weakness. The evaluation harness checks five normal cases, while the red-team tests try prompt injection, diagnosis requests, and a Tamil red flag.

Finally, I learned that the human checkpoint is essential. The nurse sees every student and makes every medical decision. The software only helps organize the queue. This separation makes the system easier to explain, test and improve.
