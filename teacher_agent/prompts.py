from __future__ import annotations

from typing import Mapping

from teacher_agent.schemas import TARGET_FILENAMES


SYSTEM_PROMPT = """
You are KlassenPilot, an assistant for a Gymnasium Bayern teacher handling Chemie and Englisch in one class.

Hard rules:
- Keep student references pseudonymous only (S-001, S-002...).
- Keep concise teacher-usable markdown.
- Preserve useful existing information and integrate new notes.
- Never claim you wrote files; only propose content unless explicitly asked for a lesson plan.
""".strip()


def format_context(context: Mapping[str, str]) -> str:
    return "\n\n".join(
        f"## FILE: {name}\n{content}" for name, content in context.items()
    )


def build_structuring_prompt(notes: str, context: Mapping[str, str]) -> str:
    files = "\n".join(f"- {filename}" for filename in TARGET_FILENAMES)
    json_schema = ",\n  ".join(
        f'"{filename}": "...full markdown..."' for filename in TARGET_FILENAMES
    )

    return f"""
Task:
Given rough lesson notes and current markdown memory, propose complete updated content for these files:
{files}

Return JSON only with this schema:
{{
  {json_schema}
}}

Current memory:
{format_context(context)}

New rough lesson notes:
{notes}
""".strip()


def build_planning_prompt(context: Mapping[str, str]) -> str:
    return f"""
Task:
Plan the next lesson for Klasse 9b (Chemie + Englisch).

Use the complete memory below to generate a concrete next lesson plan.

Output in markdown with sections:
1) Lesson goal(s)
2) Starter (5-10 min)
3) Core activities (with timing)
4) Differentiation ideas
5) Misconceptions to watch
6) Exit ticket
7) Homework / follow-up

Keep practical and concise for a real teacher.

Context:
{format_context(context)}
""".strip()
