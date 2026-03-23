#!/usr/bin/env python3

import argparse
import time
from collections import Counter

import pandas as pd


def get_languages_from_post(post):
    """Return a list of language codes found in one post."""
    possible_keys = ["language", "lang", "langs", "languages"]
    languages = []

    # Walk the whole post so nested fields like doc.record.langs are also found.
    stack = [post]
    while stack:
        current = stack.pop()

        if isinstance(current, dict):
            for key, value in current.items():
                if key in possible_keys:
                    if isinstance(value, str):
                        if value.strip():
                            languages.append(value.strip().lower())
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and item.strip():
                                languages.append(item.strip().lower())

                if isinstance(value, (dict, list)):
                    stack.append(value)

        elif isinstance(current, list):
            for item in current:
                if isinstance(item, (dict, list)):
                    stack.append(item)

    return list(set(languages))


def count_languages_in_file(file_path):
    #Count languages in one NDJSON file using pandas.
    counts = Counter()
    malformed_lines = 0
    no_language_posts = 0

    df = pd.read_json(file_path, lines=True)
    total_posts = len(df)

    for _, row in df.iterrows():
        post = row.to_dict()
        languages = get_languages_from_post(post)

        if not languages:
            no_language_posts += 1
            continue

        for language in languages:
            counts[language] += 1

    return counts, total_posts, malformed_lines, no_language_posts


def print_results(title, counts, total_posts, malformed_lines, no_language_posts, top_n=10):
    #Print a small summary table.
    print("\n" + title)
    print("-" * len(title))
    print(f"{'Language':<12} {'Count':>10}")
    print(f"{'-' * 12} {'-' * 10}")

    for language, count in counts.most_common(top_n):
        print(f"{language:<12} {count:>10}")

    print(
        f"Stats: total_posts={total_posts}, malformed_lines={malformed_lines}, "
        f"posts_with_no_language={no_language_posts}"
    )


def main():
    parser = argparse.ArgumentParser(description="Beginner pandas draft language counter")
    parser.add_argument(
        "--mastodon",
        default="datasets/mastodon-small.ndjson",
        help="Path to Mastodon NDJSON file",
    )
    parser.add_argument(
        "--bluesky",
        default="datasets/bluesky-small.ndjson",
        help="Path to BlueSky NDJSON file",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Show top N languages",
    )

    args = parser.parse_args()

    start_time = time.perf_counter()

    mastodon_counts, mastodon_total, mastodon_bad, mastodon_no_lang = count_languages_in_file(args.mastodon)
    bluesky_counts, bluesky_total, bluesky_bad, bluesky_no_lang = count_languages_in_file(args.bluesky)

    print_results(
        "Mastodon Language Counts",
        mastodon_counts,
        mastodon_total,
        mastodon_bad,
        mastodon_no_lang,
        args.top,
    )

    print_results(
        "BlueSky Language Counts",
        bluesky_counts,
        bluesky_total,
        bluesky_bad,
        bluesky_no_lang,
        args.top,
    )

    end_time = time.perf_counter()
    print(f"\nTotal processing time (seconds): {end_time - start_time:.6f}")


if __name__ == "__main__":
    main()
