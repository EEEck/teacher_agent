# KlassenPilot (Local Prototype)

KlassenPilot is a minimal teacher-level AI copilot prototype for a Gymnasium teacher. It currently supports one class (`Klasse 9b`) with Chemie + Englisch focus and two workflows:

1. Log a lesson from rough notes.
2. Generate the next lesson plan from accumulated class memory.

## Tech stack

- Python
- Streamlit UI
- OpenAI Agents SDK
- Local markdown files as memory
- No database/auth/grading

## Project structure

```text
app.py
teacher_agent/
|-- __init__.py
|-- agent.py
|-- backend.py
|-- contracts.py
|-- prompts.py
|-- schemas.py
|-- tools.py
`-- wiki_store.py
teacher_wiki/
|-- AGENTS.md
|-- index.md
|-- log.md
|-- teacher_profile.md
|-- subjects/
|   |-- chemie.md
|   `-- english.md
`-- classes/
    `-- class_9b_2026_27/
        |-- course_state.md
        |-- lesson_graph.md
        |-- student_notes.md
        |-- misconceptions.md
        `-- open_loops.md
```

## Architecture

- `app.py` contains only Streamlit UI logic: layout, session state, buttons, messages, and rendering.
- `teacher_agent/contracts.py` defines the fixed UI/backend boundary: request/response types, bootstrap data, and UI-facing memory drafts.
- `teacher_agent/backend.py` is the facade the UI calls for app bootstrap, lesson structuring, lesson planning, and approved memory saves.
- `teacher_agent/schemas.py` defines backend/domain schemas: `LessonLogInput`, `WikiUpdateProposal`, `WikiUpdateBundle`, and `LessonPlan`.
- `teacher_agent/wiki_store.py` owns all wiki file reads/writes and restricts writes to the approved class-memory files.
- `teacher_agent/tools.py` exposes safe app actions for loading context, preparing proposals, and applying approved updates.
- `teacher_agent/prompts.py` contains the system prompt and task prompt builders.
- `teacher_agent/agent.py` creates and runs the OpenAI Agents SDK agents and validates their outputs into schemas.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set your API key:

```bash
export OPENAI_API_KEY="your_key_here"
```

4. Run the app:

```bash
streamlit run app.py
```

## How it works

- Enter rough notes in **"What happened in today's lesson?"**.
- Click **"Structure lesson notes"**.
- The agent proposes complete markdown updates for:
  - `lesson_graph.md`
  - `course_state.md`
  - `misconceptions.md`
  - `student_notes.md`
  - `open_loops.md`
- Review proposed changes in the UI.
- Click **"Approve and save memory"** to persist updates.
- Click **"Generate next lesson plan"** to create a plan from current memory.

## Safety & memory rules

- The agent does not write directly to memory files.
- Memory writes only happen after explicit user approval.
- Student notes should only use pseudonymous IDs like `S-001`, `S-002`.
