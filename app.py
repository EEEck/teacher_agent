from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import streamlit as st

try:
    from agents import Agent, Runner
except ImportError as exc:
    Agent = None
    Runner = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


ROOT = Path(__file__).parent
WIKI_ROOT = ROOT / "teacher_wiki"
CLASS_DIR = WIKI_ROOT / "classes" / "class_9b_2026_27"

TARGET_FILES = {
    "lesson_graph.md": CLASS_DIR / "lesson_graph.md",
    "course_state.md": CLASS_DIR / "course_state.md",
    "misconceptions.md": CLASS_DIR / "misconceptions.md",
    "student_notes.md": CLASS_DIR / "student_notes.md",
    "open_loops.md": CLASS_DIR / "open_loops.md",
}


@dataclass
class ClassConfig:
    key: str
    label: str
    class_dir: Path


CLASS_OPTIONS = {
    "class_9b_2026_27": ClassConfig(
        key="class_9b_2026_27",
        label="Klasse 9b (Chemie + Englisch)",
        class_dir=CLASS_DIR,
    )
}


def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_markdown(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n", encoding="utf-8")


def load_context(config: ClassConfig) -> Dict[str, str]:
    context_files = {
        "index.md": WIKI_ROOT / "index.md",
        "log.md": WIKI_ROOT / "log.md",
        "teacher_profile.md": WIKI_ROOT / "teacher_profile.md",
        "subjects/chemie.md": WIKI_ROOT / "subjects" / "chemie.md",
        "subjects/english.md": WIKI_ROOT / "subjects" / "english.md",
        "classes/course_state.md": config.class_dir / "course_state.md",
        "classes/lesson_graph.md": config.class_dir / "lesson_graph.md",
        "classes/student_notes.md": config.class_dir / "student_notes.md",
        "classes/misconceptions.md": config.class_dir / "misconceptions.md",
        "classes/open_loops.md": config.class_dir / "open_loops.md",
    }
    return {name: read_markdown(path) for name, path in context_files.items()}


def build_structuring_prompt(notes: str, context: Dict[str, str]) -> str:
    context_blob = "\n\n".join(
        f"## FILE: {name}\n{content}" for name, content in context.items()
    )
    return f"""
You are KlassenPilot, an assistant for a Gymnasium Bayern teacher handling Chemie and Englisch in one class.

Task:
Given rough lesson notes and current markdown memory, propose complete updated content for these files:
- lesson_graph.md
- course_state.md
- misconceptions.md
- student_notes.md
- open_loops.md

Hard rules:
- Do NOT mention writing files. You only propose content.
- Keep student references pseudonymous only (S-001, S-002...).
- Keep concise teacher-usable markdown.
- Preserve useful existing information and integrate new notes.

Return JSON only with this schema:
{{
  "lesson_graph.md": "...full markdown...",
  "course_state.md": "...full markdown...",
  "misconceptions.md": "...full markdown...",
  "student_notes.md": "...full markdown...",
  "open_loops.md": "...full markdown..."
}}

Current memory:
{context_blob}

New rough lesson notes:
{notes}
""".strip()


def build_planning_prompt(context: Dict[str, str]) -> str:
    context_blob = "\n\n".join(
        f"## FILE: {name}\n{content}" for name, content in context.items()
    )
    return f"""
You are KlassenPilot, planning the next lesson for Klasse 9b (Chemie + Englisch).

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
{context_blob}
""".strip()


async def run_agent(prompt: str, agent_name: str) -> str:
    if Agent is None or Runner is None:
        raise RuntimeError(
            "OpenAI Agents SDK is not available. Install dependencies from requirements.txt"
        ) from IMPORT_ERROR

    agent = Agent(name=agent_name, instructions="Be accurate and return exactly what is requested.")
    result = await Runner.run(agent, input=prompt)
    return result.final_output


def ensure_session_state() -> None:
    st.session_state.setdefault("proposed_updates", None)
    st.session_state.setdefault("lesson_plan", None)


def main() -> None:
    st.set_page_config(page_title="KlassenPilot", layout="wide")
    ensure_session_state()

    st.title("KlassenPilot — Local Prototype")
    st.caption("Teacher copilot for Gymnasium Bayern lessons (Chemie + Englisch).")

    with st.sidebar:
        st.header("Class")
        class_key = st.selectbox(
            "Select class",
            options=list(CLASS_OPTIONS.keys()),
            format_func=lambda k: CLASS_OPTIONS[k].label,
        )

    class_config = CLASS_OPTIONS[class_key]
    st.subheader(f"Lesson logging for {class_config.label}")

    rough_notes = st.text_area(
        "What happened in today's lesson?",
        height=180,
        placeholder="Paste rough notes here...",
    )

    if st.button("Structure lesson notes", type="primary"):
        if not rough_notes.strip():
            st.warning("Please enter rough lesson notes first.")
        else:
            with st.spinner("Structuring notes with agent..."):
                context = load_context(class_config)
                prompt = build_structuring_prompt(rough_notes, context)
                try:
                    output = __import__("asyncio").run(run_agent(prompt, "memory-structurer"))
                    st.session_state.proposed_updates = json.loads(output)
                except Exception as exc:
                    st.error(f"Failed to structure notes: {exc}")

    proposed_updates = st.session_state.proposed_updates
    if proposed_updates:
        st.markdown("### Proposed memory updates (review before saving)")
        for filename in TARGET_FILES:
            st.markdown(f"#### {filename}")
            st.code(proposed_updates.get(filename, ""), language="markdown")

        if st.button("Approve and save memory"):
            missing = [f for f in TARGET_FILES if f not in proposed_updates]
            if missing:
                st.error(f"Missing proposed updates for: {', '.join(missing)}")
            else:
                for filename, filepath in TARGET_FILES.items():
                    write_markdown(filepath, proposed_updates[filename])
                st.success("Memory saved.")

    st.markdown("---")
    st.subheader("Plan next lesson")
    if st.button("Generate next lesson plan"):
        with st.spinner("Generating lesson plan..."):
            context = load_context(class_config)
            prompt = build_planning_prompt(context)
            try:
                lesson_plan = __import__("asyncio").run(run_agent(prompt, "lesson-planner"))
                st.session_state.lesson_plan = lesson_plan
            except Exception as exc:
                st.error(f"Failed to generate plan: {exc}")

    if st.session_state.lesson_plan:
        st.markdown("### Next lesson plan")
        st.markdown(st.session_state.lesson_plan)

    if "OPENAI_API_KEY" not in os.environ:
        st.info("Set OPENAI_API_KEY in your environment before running agent actions.")


if __name__ == "__main__":
    main()
