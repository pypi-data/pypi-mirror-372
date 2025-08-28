#!/usr/bin/env python3
"""
Translation example using tidylinq with progress tracking.
"""

import argparse
from textwrap import dedent

from pydantic import BaseModel, Field

from tidylinq import completion_with_schema, from_iterable, retry


class Translation(BaseModel):
    term_source: str = Field(description="The source language term")
    term_target: str = Field(description="The term translated to the target language.")
    example_source: str = Field(description="Example of using the term in the source language.")
    example_target: str = Field(description="Example sentence target to the target language.")


def main():
    parser = argparse.ArgumentParser(description="Translate words using an LLM")
    parser.add_argument(
        "--model",
        default="gemini/gemini-2.5-flash",
        help="Model to use for translation",
    )
    parser.add_argument(
        "--parallelism",
        type=int,
        default=4,
        help="Number of parallel requests to the model.",
    )
    parser.add_argument(
        "words",
        nargs="+",
        help="Words to translate",
    )
    args = parser.parse_args()

    messages = [
        {
            "role": "system",
            "content": dedent("""
                You are an expert translator. Output a structured Japanese response in JSON format for the provided English words.
            """).strip(),
        },
    ]

    translations = (
        from_iterable(args.words)
        .select(
            lambda w: retry(completion_with_schema, backoff=1.0)(
                model=args.model,
                messages=messages + [{"role": "user", "content": w}],
                response_schema=Translation,
            ),
            parallelism=args.parallelism,
        )
        .with_progress(f"Translating {len(args.words)} words")
    )

    # Collect and display results
    results: list[Translation] = translations.to_list() # type: ignore
    print("\n" + "=" * 60 + "\n")
    for translation in results:
        print(f"English: {translation.term_source}")
        print(f"Japanese: {translation.term_target}")
        print(f"Example (EN): {translation.example_source}")
        print(f"Example (JP): {translation.example_target}")
        print("-" * 60)


if __name__ == "__main__":
    main()