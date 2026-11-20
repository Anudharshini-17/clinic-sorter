import csv
import json
import os
import re
import time
from collections import Counter
from datetime import datetime

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

ALLOWED_CATEGORIES = {
    "injury",
    "fever_cold",
    "stomach",
    "pain",
    "allergy",
    "other"
}

ALLOWED_PRIORITIES = {
    "see_now",
    "today",
    "routine"
}


# ============================================================
# RED FLAGS
# ============================================================

RED_FLAG_TERMS = [
    "chest pain",
    "difficulty breathing",
    "trouble breathing",
    "cannot breathe",
    "can't breathe",
    "unable to breathe",
    "shortness of breath",
    "fainting",
    "heavy bleeding",
    "severe bleeding",
    "face swelling",
    "lip swelling",
    "lips swelling",
    "tongue swelling",
    "unable to stand",

    # Tanglish
    "nenju vali",
    "moochu vida mudiyala",
    "moochu vidamudiyala",
    "moochu thinaral",
    "mayakkam",
    "adhigama blood"
]


# ============================================================
# DIAGNOSIS-LIKE TERMS
# ============================================================

DIAGNOSIS_TERMS = [
    "you have",
    "you are suffering from",
    "diagnosis",
    "diagnosed with",
    "likely has",
    "probably has",
    "you may have"
]


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a clinic visit sorting assistant.

Classify the student's note into exactly one category:

injury
fever_cold
stomach
pain
allergy
other

Classify priority as exactly one of:

see_now
today
routine

Important rules:

- Chest pain or difficulty breathing must be see_now.
- Fainting, heavy bleeding, serious swelling, or inability to stand must be see_now.
- Injury-related symptoms should generally be today.
- Fever/cold symptoms should generally be today.
- Stomach pain, nausea, vomiting, or diarrhea should generally be today.
- Routine should be used for non-urgent administrative requests.
- Do not diagnose diseases.
- Do not provide treatment.
- Give a short neutral summary.
- The nurse makes the final medical decision.

Return ONLY valid JSON:

{
  "category": "one allowed category",
  "priority": "one allowed priority",
  "summary": "short neutral summary"
}
"""


# ============================================================
# LOAD VISITS
# ============================================================

def load_visits(filename="visits.csv"):

    visits = []

    with open(
        filename,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            visits.append({
                "id": row.get("id", "").strip(),
                "time": row.get("time", "").strip(),
                "note": row.get("note", "").strip()
            })

    return visits


# ============================================================
# BUILD USER PROMPT
# ============================================================

def build_user_prompt(note):

    return f"""
Student clinic note:

{note}

Classify this note.

Return only JSON with:
category
priority
summary
"""


# ============================================================
# GROQ CALL
# ============================================================

def call_groq(note, client=None):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Check your .env file."
        )

    # If evaluator gives us a client, use it.
    # Otherwise create a client here.
    if client is None:
        client = Groq(api_key=api_key)

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": build_user_prompt(note)
            }
        ],

        response_format={
            "type": "json_object"
        },

        reasoning_effort="low",
        include_reasoning=False,
        temperature=0,
        max_completion_tokens=512
    )

    content = response.choices[0].message.content

    return json.loads(content)


# ============================================================
# RED FLAG CHECK
# ============================================================

def contains_red_flag(note):

    text = note.lower()

    for term in RED_FLAG_TERMS:

        if term in text:
            return True

    return False


# ============================================================
# PRIORITY RULES
# ============================================================

def raise_priority(priority, note):

    text = note.lower().strip()

    # --------------------------------------------------------
    # 1. RED FLAGS
    # --------------------------------------------------------

    if contains_red_flag(text):
        return "see_now"


    # --------------------------------------------------------
    # 2. INJURY
    # --------------------------------------------------------

    injury_terms = [
        "injury",
        "injured",
        "twisted",
        "twist",
        "ankle",
        "knee",
        "wrist",
        "elbow",
        "sprain",
        "sprained",
        "fell",
        "fall",
        "hurt",
        "swollen",
        "swelling",
        "bruise",
        "bruised"
    ]

    if any(term in text for term in injury_terms):
        return "today"


    # --------------------------------------------------------
    # 3. STOMACH
    # --------------------------------------------------------

    stomach_terms = [
        "stomach pain",
        "stomach ache",
        "stomachache",
        "abdominal pain",
        "abdominal ache",
        "nausea",
        "vomiting",
        "vomit",
        "diarrhea",
        "diarrhoea"
    ]

    if any(term in text for term in stomach_terms):
        return "today"


    # --------------------------------------------------------
    # 4. FEVER / COLD
    # --------------------------------------------------------

    fever_cold_terms = [
        "fever",
        "sneezing",
        "cold",
        "cough",
        "sore throat",
        "runny nose",
        "headache"
    ]

    if any(term in text for term in fever_cold_terms):
        return "today"


    # --------------------------------------------------------
    # 5. KEEP VALID LLM PRIORITY
    # --------------------------------------------------------

    if priority in ALLOWED_PRIORITIES:
        return priority

    return "today"


# ============================================================
# DIAGNOSIS CHECK
# ============================================================

def contains_diagnosis(text):

    text = text.lower()

    for term in DIAGNOSIS_TERMS:

        if term in text:
            return True

    return False


# ============================================================
# NEUTRAL SUMMARY
# ============================================================

def neutral_summary(note):

    text = note.strip()

    if not text:
        return "Student requested a clinic visit."

    words = text.split()

    if len(words) <= 12:
        return text

    return " ".join(words[:12]) + "..."


# ============================================================
# REMOVE DIAGNOSIS LANGUAGE
# ============================================================

def remove_diagnosis(summary):

    text = summary.strip()

    replacements = [
        (r"\byou have\b", "reported"),
        (r"\byou are suffering from\b", "reported"),
        (r"\bdiagnosed with\b", "reported"),
        (r"\blikely has\b", "reported"),
        (r"\bprobably has\b", "reported"),
        (r"\byou may have\b", "reported")
    ]

    for pattern, replacement in replacements:

        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE
        )

    return text


# ============================================================
# VALIDATE RESULT
# ============================================================

def is_valid(result):

    if not isinstance(result, dict):
        return False

    required_keys = {
        "category",
        "priority",
        "summary"
    }

    if not required_keys.issubset(result.keys()):
        return False

    if result["category"] not in ALLOWED_CATEGORIES:
        return False

    if result["priority"] not in ALLOWED_PRIORITIES:
        return False

    if not isinstance(result["summary"], str):
        return False

    if not result["summary"].strip():
        return False

    return True


# ============================================================
# LOCAL FALLBACK CATEGORY
# ============================================================

def local_category(note):

    text = note.lower()

    # Injury
    if any(
        word in text
        for word in [
            "twisted",
            "injury",
            "injured",
            "ankle",
            "knee",
            "wrist",
            "sprain",
            "fell",
            "fall",
            "swollen",
            "swelling"
        ]
    ):
        return "injury"

    # Fever/cold
    if any(
        word in text
        for word in [
            "fever",
            "sneezing",
            "cough",
            "cold",
            "sore throat",
            "runny nose"
        ]
    ):
        return "fever_cold"

    # Stomach
    if any(
        word in text
        for word in [
            "stomach",
            "nausea",
            "vomiting",
            "vomit",
            "diarrhea",
            "diarrhoea",
            "abdominal"
        ]
    ):
        return "stomach"

    # Pain
    if any(
        word in text
        for word in [
            "chest pain",
            "headache",
            "body pain",
            "leg pain",
            "back pain",
            "neck pain",
            "pain"
        ]
    ):
        return "pain"

    # Allergy
    if any(
        word in text
        for word in [
            "allergy",
            "rash",
            "itching"
        ]
    ):
        return "allergy"

    return "other"


# ============================================================
# CLASSIFY
#
# IMPORTANT:
# evaluate.py calls:
# classify(note, client)
#
# Therefore this function returns:
# result, source
# ============================================================

def classify(note, client=None):

    # --------------------------------------------------------
    # TRY GROQ
    # --------------------------------------------------------

    for attempt in range(2):

        try:

            result = call_groq(
                note,
                client
            )

            if not is_valid(result):

                raise ValueError(
                    "Invalid JSON result from Groq."
                )

            # Get LLM values
            category = result["category"]
            priority = result["priority"]
            summary = result["summary"]

            # ------------------------------------------------
            # PYTHON PRIORITY SAFETY RULES
            # ------------------------------------------------

            priority = raise_priority(
                priority,
                note
            )

            # ------------------------------------------------
            # PROTECT AGAINST DIAGNOSIS
            # ------------------------------------------------

            if contains_diagnosis(summary):

                summary = neutral_summary(note)

            summary = remove_diagnosis(summary)

            final_result = {
                "category": category,
                "priority": priority,
                "summary": summary
            }

            return final_result, "groq"

        except Exception as error:

            print(
                f"Groq attempt {attempt + 1} failed: {error}"
            )

            if attempt == 0:
                time.sleep(2)


    # --------------------------------------------------------
    # LOCAL FALLBACK
    # --------------------------------------------------------

    category = local_category(note)

    priority = raise_priority(
        "routine",
        note
    )

    summary = neutral_summary(note)

    final_result = {
        "category": category,
        "priority": priority,
        "summary": summary
    }

    return final_result, "local_fallback"


# ============================================================
# TIME SORTING
# ============================================================

def time_key(time_text):

    try:

        return datetime.strptime(
            time_text,
            "%H:%M"
        )

    except ValueError:

        return datetime.max


# ============================================================
# WRITE REPORTS
# ============================================================

def write_reports(results):

    priority_order = {
        "see_now": 0,
        "today": 1,
        "routine": 2
    }

    results.sort(
        key=lambda x: (
            priority_order.get(
                x["priority"],
                99
            ),
            time_key(x["time"])
        )
    )

    # --------------------------------------------------------
    # NURSE QUEUE
    # --------------------------------------------------------

    with open(
        "nurse_queue.csv",
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "id",
            "time",
            "note",
            "category",
            "priority",
            "summary"
        ])

        for result in results:

            writer.writerow([
                result["id"],
                result["time"],
                result["note"],
                result["category"],
                result["priority"],
                result["summary"]
            ])


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    category_counts = Counter(
        result["category"]
        for result in results
    )

    priority_counts = Counter(
        result["priority"]
        for result in results
    )

    source_counts = Counter(
        result["source"]
        for result in results
    )

    with open(
        "summary.txt",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "============================================================\n"
        )

        file.write(
            "CLINIC VISIT SORTER - SUMMARY\n"
        )

        file.write(
            "============================================================\n\n"
        )

        file.write(
            f"Total visits: {len(results)}\n\n"
        )

        file.write(
            "CATEGORY COUNTS\n"
        )

        file.write(
            "----------------\n"
        )

        for category, count in category_counts.items():

            file.write(
                f"{category}: {count}\n"
            )

        file.write("\n")

        file.write(
            "PRIORITY COUNTS\n"
        )

        file.write(
            "----------------\n"
        )

        for priority, count in priority_counts.items():

            file.write(
                f"{priority}: {count}\n"
            )

        file.write("\n")

        file.write(
            "SOURCE COUNTS\n"
        )

        file.write(
            "----------------\n"
        )

        for source, count in source_counts.items():

            file.write(
                f"{source}: {count}\n"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("CLINIC VISIT SORTER")
    print("=" * 60)

    visits = load_visits()

    if not visits:

        print("No visits found in visits.csv.")
        return

    results = []

    print(
        f"\nProcessing {len(visits)} clinic visits...\n"
    )

    for index, visit in enumerate(visits):

        print(
            f"[{index + 1}/{len(visits)}] "
            f"{visit['id']} - "
            f"{visit['note']}"
        )

        result, source = classify(
            visit["note"]
        )

        result["id"] = visit["id"]
        result["time"] = visit["time"]
        result["note"] = visit["note"]
        result["source"] = source

        results.append(result)

        print(
            f"    Category : {result['category']}"
        )

        print(
            f"    Priority : {result['priority']}"
        )

        print(
            f"    Source   : {source}"
        )

        # Wait between Groq requests
        if index < len(visits) - 1:
            time.sleep(5)

    write_reports(results)

    print("\n")
    print("=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)

    print("\nCreated:")
    print("  nurse_queue.csv")
    print("  summary.txt")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()