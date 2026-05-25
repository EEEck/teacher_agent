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
teacher_wiki/
├── AGENTS.md
├── index.md
├── log.md
├── teacher_profile.md
├── subjects/
│   └── chemie.md
└── classes/
    └── class_9b_2026_27/
        ├── course_state.md
        ├── lesson_graph.md
        ├── student_notes.md
        ├── misconceptions.md
        └── open_loops.md
```

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
