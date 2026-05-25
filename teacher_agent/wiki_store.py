from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from teacher_agent.schemas import TARGET_FILENAMES, WikiUpdateBundle


ROOT = Path(__file__).resolve().parent.parent
WIKI_ROOT = ROOT / "teacher_wiki"


@dataclass(frozen=True)
class ClassConfig:
    key: str
    label: str
    class_dir: Path


CLASS_OPTIONS = {
    "class_9b_2026_27": ClassConfig(
        key="class_9b_2026_27",
        label="Klasse 9b (Chemie + Englisch)",
        class_dir=WIKI_ROOT / "classes" / "class_9b_2026_27",
    )
}


def get_class_config(class_key: str) -> ClassConfig:
    try:
        return CLASS_OPTIONS[class_key]
    except KeyError as exc:
        known = ", ".join(CLASS_OPTIONS)
        raise ValueError(f"Unknown class '{class_key}'. Known classes: {known}") from exc


def target_file_paths(class_key: str) -> dict[str, Path]:
    config = get_class_config(class_key)
    return {filename: config.class_dir / filename for filename in TARGET_FILENAMES}


def context_file_paths(class_key: str) -> dict[str, Path]:
    config = get_class_config(class_key)
    return {
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


def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_markdown(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n", encoding="utf-8")


def load_context(class_key: str) -> dict[str, str]:
    return {
        name: read_markdown(path)
        for name, path in context_file_paths(class_key).items()
    }


def read_wiki_file(class_key: str, logical_name: str) -> str:
    paths = context_file_paths(class_key) | target_file_paths(class_key)
    try:
        path = paths[logical_name]
    except KeyError as exc:
        allowed = ", ".join(sorted(paths))
        raise ValueError(f"Wiki file '{logical_name}' is not allowed. Allowed: {allowed}") from exc
    return read_markdown(path)


def save_update_bundle(bundle: WikiUpdateBundle) -> None:
    paths = target_file_paths(bundle.class_key)
    for proposal in bundle.proposals:
        if proposal.filename not in paths:
            allowed = ", ".join(sorted(paths))
            raise ValueError(
                f"Wiki file '{proposal.filename}' is not writable. Allowed: {allowed}"
            )
        write_markdown(paths[proposal.filename], proposal.markdown)
