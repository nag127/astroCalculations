"""
Utilities for turning the saved astrology JSON into a prompt payload for an LLM.

Usage:
    python prompt_builder.py --question "When will I get married?" \
        --extra-info "Current age 47, married once before, works in IT" \
        --chart-file astrology_output.json

This prints a ready-to-use system prompt and user prompt. You can optionally
write the prompt bundle to disk with --output prompt.json.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

from config import SIGNS
from llm_prompts import (
    SYSTEM_PROMPT,
    TEMPLATE_CHART_SUMMARY,
    TEMPLATE_ANSWER,
    format_top_planets,
)


def load_chart(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Chart file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_prompt_bundle(
    chart: Dict[str, Any], question: str, extra_context: Optional[str] = None
) -> Dict[str, str]:
    meta = chart.get("meta", {})
    lagna = chart.get("lagna", {})
    moon = chart.get("moon", {})
    dasha_balance = chart.get("dasha", {}).get("balance", {})

    lagna_sign_idx = lagna.get("sign_index", 0)
    lagna_sign = SIGNS[lagna_sign_idx]

    moon_nakshatra = ""
    moon_info = moon.get("nakshatra")
    if isinstance(moon_info, dict):
        moon_nakshatra = moon_info.get("nakshatra", "")

    top_planets = format_top_planets(chart.get("rasi_chart", {}).get("planets", {}))

    chart_summary = TEMPLATE_CHART_SUMMARY.format(
        dob=meta.get("dob"),
        tob=meta.get("tob"),
        timezone=meta.get("timezone"),
        lat=meta.get("latitude"),
        lon=meta.get("longitude"),
        lagna_sign=lagna_sign,
        lagna_degree=lagna.get("degree", 0.0),
        moon_nakshatra=moon_nakshatra,
        moon_sidereal=moon.get("sidereal"),
        dasha_balance=json.dumps(dasha_balance, indent=2),
        top_planets=top_planets or "N/A",
    )

    extra_section = ""
    if extra_context:
        extra_section = f"\nAdditional life context to consider:\n{extra_context.strip()}\n"

    user_prompt = (
        chart_summary
        + extra_section
        + TEMPLATE_ANSWER.format(
            question=question,
            chart_json=json.dumps(chart, indent=2, default=str),
        )
    )

    return {
        "system": SYSTEM_PROMPT.strip(),
        "user": user_prompt.strip(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Convert saved astrology JSON into an LLM-ready prompt."
    )
    parser.add_argument(
        "--chart-file",
        default="astrology_output.json",
        help="Path to the JSON file produced by main.py",
    )
    parser.add_argument(
        "--question",
        required=True,
        help="Natural-language question to ask the astrologer LLM.",
    )
    parser.add_argument(
        "--extra-info",
        default="",
        help="Optional life context (career, relationship history, goals).",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write the prompt bundle as JSON.",
    )

    args = parser.parse_args()
    chart = load_chart(Path(args.chart_file))
    bundle = build_prompt_bundle(chart, args.question, args.extra_info)

    if args.output:
        Path(args.output).write_text(json.dumps(bundle, indent=2), encoding="utf-8")
        print(f"Prompt bundle saved to {args.output}")

    print("\n=== System Prompt ===\n")
    print(bundle["system"])
    print("\n=== User Prompt ===\n")
    print(bundle["user"])


if __name__ == "__main__":
    main()

