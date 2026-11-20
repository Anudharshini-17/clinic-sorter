import os

from dotenv import load_dotenv
from groq import Groq

from main import classify


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


# ============================================================
# EVALUATION TEST CASES
# ============================================================

TESTS = [

    {
        "id": "T1",
        "note": "I twisted my ankle and it is swollen",
        "expected_category": "injury",
        "expected_priority": "today"
    },

    {
        "id": "T2",
        "note": "I have fever and sneezing",
        "expected_category": "fever_cold",
        "expected_priority": "today"
    },

    {
        "id": "T3",
        "note": "I have stomach pain and nausea",
        "expected_category": "stomach",
        "expected_priority": "today"
    },

    {
        "id": "T4",
        "note": "I need a medical certificate for yesterday",
        "expected_category": "other",
        "expected_priority": "routine"
    },

    {
        "id": "T5",
        "note": "Chest pain and difficulty breathing",
        "expected_category": "pain",
        "expected_priority": "see_now"
    }
]


# ============================================================
# MAIN EVALUATION
# ============================================================

def main():

    print("=" * 60)
    print("CLINIC VISIT SORTER - EVALUATION")
    print("=" * 60)

    # --------------------------------------------------------
    # CREATE GROQ CLIENT
    # --------------------------------------------------------

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:

        print("\nERROR:")
        print("GROQ_API_KEY is missing from .env")
        return

    client = Groq(
        api_key=api_key
    )

    total = len(TESTS)
    passed = 0


    # --------------------------------------------------------
    # RUN TESTS
    # --------------------------------------------------------

    for test in TESTS:

        print("\n")
        print(test["id"])

        print(
            f"Note: {test['note']}"
        )

        print(
            f"Expected: "
            f"{test['expected_category']} / "
            f"{test['expected_priority']}"
        )

        try:

            # IMPORTANT:
            # classify returns:
            # result, source

            result, source = classify(
                test["note"],
                client
            )

            actual_category = result["category"]
            actual_priority = result["priority"]
            summary = result["summary"]

            print(
                f"Actual:   "
                f"{actual_category} / "
                f"{actual_priority}"
            )

            print(
                f"Summary:  {summary}"
            )

            print(
                f"Source:   {source}"
            )


            # ------------------------------------------------
            # CHECK RESULT
            # ------------------------------------------------

            category_ok = (
                actual_category
                == test["expected_category"]
            )

            priority_ok = (
                actual_priority
                == test["expected_priority"]
            )

            if category_ok and priority_ok:

                print(
                    "Result:   PASS"
                )

                passed += 1

            else:

                print(
                    "Result:   FAIL"
                )

        except Exception as error:

            print(
                f"ERROR: {error}"
            )

            print(
                "Result:   FAIL"
            )


    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)

    print(
        f"Score: {passed}/{total}"
    )

    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()