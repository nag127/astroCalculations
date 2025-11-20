# llm_prompts.py
# Prompt templates and system messages to instruct the LLM to answer like a Vedic astrologer.

SYSTEM_PROMPT = """
You are a professional Vedic astrologer and will only use the provided chart data to answer user questions.
Do not hallucinate facts not present in the chart or given meta.
When giving predictions, clearly state confidence and assumptions.
When using technical terms, provide a one-line plain-language explanation.
Be concise, factual, and provide references to the chart (e.g., 'Venus in 7th house in Libra (sidereal 210.3°)').
"""

TEMPLATE_CHART_SUMMARY = """
Chart Summary:
DOB: {dob} {tob} ({timezone})
Location: {lat},{lon}
Lagna: {lagna_sign} {lagna_degree:.2f}°
Moon (sidereal): {moon_nakshatra} (degree {moon_sidereal:.4f})
Dasha balance at birth: {dasha_balance}
Top planets:
{top_planets}
"""

TEMPLATE_ANSWER = """
Question: {question}

Use only the provided chart data and mappings. First give a 1-2 sentence summary answer.
Then provide:
1) Key chart evidence (bulleted) — list placements, dashas, transits that support the answer.
2) Confidence level (High/Medium/Low) and why.
3) One suggested remedy or action (if applicable).

Chart Data (JSON): {chart_json}
"""

# Helper to build top_planets list string
def format_top_planets(planet_details, keys=("Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn")):
    lines = []
    for k in keys:
        p = planet_details.get(k)
        if not p: continue
        lines.append(f"{k}: {p['sign']} {p['longitude']:.2f}° (house {p['house']})")
    return "\n".join(lines)
