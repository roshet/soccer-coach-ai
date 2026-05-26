import os
import anthropic
from services.biomechanics.base import BiomechanicsResult

TECHNIQUE_LABELS = {
    "shooting_driven": "driven shot",
    "passing_short": "short pass",
}

SYSTEM_PROMPT = """You are an elite UEFA Pro-licensed soccer coach with 20 years of experience
coaching professional and academy players. You provide precise, actionable biomechanical feedback
based on pose analysis data. Reference how professional players (Messi, Ronaldo, De Bruyne)
execute the same techniques. Be specific, encouraging, and professional.
Respond in 300-400 words. Structure your response as:
1. Overall assessment (2-3 sentences)
2. Key strengths (2-3 bullet points)
3. Priority improvements (2-3 bullet points with specific cues)
4. One drill recommendation"""


def _build_prompt(result: BiomechanicsResult) -> str:
    technique_label = TECHNIQUE_LABELS.get(result.technique, result.technique)
    score_lines = "\n".join(
        f"  - {k.replace('_', ' ').title()}: {v}/100"
        for k, v in result.scores.items()
    )
    flag_lines = "\n".join(f"  - {f}" for f in result.flags) if result.flags else "  - None"

    return f"""Biomechanical analysis for technique: {technique_label}
Overall score: {result.overall_score}/100

Checkpoint scores:
{score_lines}

Issues detected:
{flag_lines}

Please provide professional coaching feedback based on this analysis."""


def generate_feedback(
    result: BiomechanicsResult,
    client: anthropic.Anthropic | None = None,
) -> str | None:
    try:
        if client is None:
            client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": _build_prompt(result)}],
        )
        return message.content[0].text
    except Exception:
        return None
