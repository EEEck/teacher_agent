from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any

import streamlit as st

from teacher_agent.backend import (
    bootstrap_app,
    generate_plan,
    save_memory,
    structure_lesson,
)
from teacher_agent.contracts import (
    GeneratePlanRequest,
    MemoryDraft,
    StructureLessonRequest,
    TARGET_MEMORY_FILENAMES,
    class_option_map,
    lesson_plan_from_session,
    memory_drafts_from_session,
    save_memory_request_from_session,
    update_bundle_from_session,
)


def run_async(coro: Coroutine[Any, Any, Any]) -> Any:
    return asyncio.run(coro)


def ensure_session_state() -> None:
    st.session_state.setdefault("proposed_updates", None)
    st.session_state.setdefault("lesson_plan", None)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --kp-bg: #070a12;
            --kp-panel: rgba(13, 19, 33, 0.88);
            --kp-panel-2: rgba(18, 27, 45, 0.78);
            --kp-line: rgba(119, 199, 255, 0.18);
            --kp-text: #eef6ff;
            --kp-muted: #8fa5bd;
            --kp-cyan: #6ee7ff;
            --kp-blue: #7aa2ff;
        }

        .stApp {
            background:
                linear-gradient(135deg, rgba(8, 13, 24, 0.98) 0%, rgba(9, 17, 31, 0.98) 48%, rgba(7, 10, 18, 0.98) 100%),
                repeating-linear-gradient(90deg, rgba(110, 231, 255, 0.035) 0 1px, transparent 1px 72px);
            color: var(--kp-text);
        }

        [data-testid="stSidebar"] {
            background: rgba(5, 9, 17, 0.94);
            border-right: 1px solid var(--kp-line);
        }

        .block-container {
            padding-top: 2rem;
            max-width: 1280px;
        }

        h1, h2, h3 {
            letter-spacing: 0;
        }

        .kp-hero {
            border: 1px solid var(--kp-line);
            background: linear-gradient(135deg, rgba(11, 18, 31, 0.96), rgba(17, 26, 44, 0.82));
            padding: 1.2rem 1.35rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            box-shadow: 0 18px 55px rgba(0, 0, 0, 0.25);
        }

        .kp-title {
            color: var(--kp-text);
            font-size: 2rem;
            font-weight: 720;
            line-height: 1.1;
            margin: 0 0 0.35rem 0;
        }

        .kp-subtitle {
            color: var(--kp-muted);
            margin: 0;
            font-size: 0.98rem;
        }

        .kp-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.9rem;
        }

        .kp-chip {
            border: 1px solid rgba(110, 231, 255, 0.22);
            background: rgba(110, 231, 255, 0.08);
            color: #c8f6ff;
            border-radius: 999px;
            padding: 0.24rem 0.58rem;
            font-size: 0.78rem;
            font-weight: 650;
        }

        .kp-section-label {
            color: var(--kp-cyan);
            font-size: 0.75rem;
            font-weight: 760;
            letter-spacing: 0.08em;
            margin: 0.2rem 0 0.35rem 0;
            text-transform: uppercase;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--kp-line);
            background: var(--kp-panel);
        }

        .stTextArea textarea {
            background: rgba(7, 12, 22, 0.92);
            border: 1px solid var(--kp-line);
            color: var(--kp-text);
            border-radius: 8px;
        }

        .stButton > button {
            border-radius: 8px;
            border: 1px solid rgba(110, 231, 255, 0.24);
            font-weight: 680;
        }

        .stCodeBlock {
            border: 1px solid var(--kp-line);
            border-radius: 8px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(class_label: str) -> None:
    st.markdown(
        f"""
        <div class="kp-hero">
            <div class="kp-title">KlassenPilot</div>
            <p class="kp-subtitle">Agent workspace for {class_label}</p>
            <div class="kp-chip-row">
                <span class="kp-chip">local wiki memory</span>
                <span class="kp-chip">review before save</span>
                <span class="kp-chip">Chemie + Englisch</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_memory_drafts(drafts: tuple[MemoryDraft, ...]) -> None:
    st.markdown("### Proposed memory updates")
    st.caption("Review the generated markdown before approving it.")

    draft_by_filename = {draft.filename: draft for draft in drafts}
    for filename in TARGET_MEMORY_FILENAMES:
        draft = draft_by_filename[filename]
        with st.expander(filename, expanded=filename == TARGET_MEMORY_FILENAMES[0]):
            st.code(draft.markdown, language="markdown")


def main() -> None:
    st.set_page_config(page_title="KlassenPilot", layout="wide")
    ensure_session_state()
    apply_theme()
    app_bootstrap = bootstrap_app()
    class_options = class_option_map(app_bootstrap.class_options)

    with st.sidebar:
        st.markdown("### Class")
        class_key = st.selectbox(
            "Select class",
            options=list(class_options),
            format_func=lambda key: class_options[key].label,
        )
        proposed_updates = update_bundle_from_session(
            class_key,
            st.session_state.proposed_updates,
        )

        st.markdown("### Status")
        st.write("API key", "ready" if app_bootstrap.api_key_ready else "missing")
        st.write("Update draft", "ready" if proposed_updates else "empty")

    class_label = class_options[class_key].label
    render_header(class_label)

    left, right = st.columns([0.95, 1.25], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<div class="kp-section-label">Lesson Log</div>', unsafe_allow_html=True)
            rough_notes = st.text_area(
                "What happened in today's lesson?",
                height=230,
                placeholder="Paste rough notes here...",
            )

            if st.button("Structure lesson notes", type="primary", use_container_width=True):
                if not rough_notes.strip():
                    st.warning("Please enter rough lesson notes first.")
                else:
                    with st.spinner("Structuring notes with agent..."):
                        try:
                            response = run_async(
                                structure_lesson(
                                    StructureLessonRequest(
                                        class_key=class_key,
                                        rough_notes=rough_notes,
                                    )
                                )
                            )
                            st.session_state.proposed_updates = response.update_bundle
                        except Exception as exc:
                            st.error(f"Failed to structure notes: {exc}")

        with st.container(border=True):
            st.markdown('<div class="kp-section-label">Next Lesson</div>', unsafe_allow_html=True)
            if st.button("Generate next lesson plan", use_container_width=True):
                with st.spinner("Generating lesson plan..."):
                    try:
                        response = run_async(
                            generate_plan(GeneratePlanRequest(class_key=class_key))
                        )
                        st.session_state.lesson_plan = response.lesson_plan
                    except Exception as exc:
                        st.error(f"Failed to generate plan: {exc}")

            lesson_plan = lesson_plan_from_session(
                class_key,
                st.session_state.lesson_plan,
            )
            if lesson_plan:
                st.markdown(lesson_plan.markdown)

    with right:
        with st.container(border=True):
            st.markdown('<div class="kp-section-label">Agent Output</div>', unsafe_allow_html=True)

            memory_drafts = memory_drafts_from_session(
                class_key,
                st.session_state.proposed_updates,
            )
            if memory_drafts:
                render_memory_drafts(memory_drafts)

                if st.button("Approve and save memory", type="primary", use_container_width=True):
                    request = save_memory_request_from_session(
                        class_key,
                        st.session_state.proposed_updates,
                    )
                    if request is None:
                        st.error("No valid memory update draft is available.")
                        return
                    try:
                        save_memory(request)
                    except Exception as exc:
                        st.error(f"Failed to save memory: {exc}")
                    else:
                        st.success("Memory saved.")
            else:
                st.info("No proposed updates yet.")

    if not app_bootstrap.api_key_ready:
        st.info("Set OPENAI_API_KEY in your environment before running agent actions.")


if __name__ == "__main__":
    main()
