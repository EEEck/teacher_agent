from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping


TARGET_FILENAMES = (
    "lesson_graph.md",
    "course_state.md",
    "misconceptions.md",
    "student_notes.md",
    "open_loops.md",
)


@dataclass(frozen=True)
class LessonLogInput:
    class_key: str
    notes: str

    def validate(self, known_class_keys: set[str]) -> "LessonLogInput":
        if not self.class_key.strip():
            raise ValueError("Class key is required.")
        if self.class_key not in known_class_keys:
            known = ", ".join(sorted(known_class_keys))
            raise ValueError(f"Unknown class '{self.class_key}'. Known classes: {known}")
        if not self.notes.strip():
            raise ValueError("Lesson notes are required.")
        return self


@dataclass(frozen=True)
class WikiUpdateProposal:
    filename: str
    markdown: str

    def validate(self, allowed_filenames: tuple[str, ...]) -> "WikiUpdateProposal":
        if self.filename not in allowed_filenames:
            allowed = ", ".join(allowed_filenames)
            raise ValueError(
                f"Wiki file '{self.filename}' is not allowed. Allowed: {allowed}"
            )
        if not self.markdown.strip():
            raise ValueError(f"Proposed update for '{self.filename}' is empty.")
        return self


@dataclass(frozen=True)
class WikiUpdateBundle:
    class_key: str
    proposals: tuple[WikiUpdateProposal, ...]

    @classmethod
    def from_mapping(
        cls,
        class_key: str,
        updates: Mapping[str, Any],
        allowed_filenames: tuple[str, ...] = TARGET_FILENAMES,
    ) -> "WikiUpdateBundle":
        if not class_key.strip():
            raise ValueError("Class key is required.")

        missing = [name for name in allowed_filenames if name not in updates]
        unexpected = sorted(set(updates) - set(allowed_filenames))
        if missing:
            raise ValueError(f"Missing proposed updates for: {', '.join(missing)}")
        if unexpected:
            raise ValueError(f"Unexpected proposed updates for: {', '.join(unexpected)}")

        proposals = tuple(
            cls._proposal_from_value(name, updates[name], allowed_filenames)
            for name in allowed_filenames
        )
        return cls(class_key=class_key, proposals=proposals)

    @classmethod
    def from_agent_json(
        cls,
        class_key: str,
        output: str,
        allowed_filenames: tuple[str, ...] = TARGET_FILENAMES,
    ) -> "WikiUpdateBundle":
        try:
            parsed = json.loads(output)
        except json.JSONDecodeError as exc:
            raise ValueError("Agent returned invalid JSON for wiki updates.") from exc

        if not isinstance(parsed, dict):
            raise ValueError("Agent returned a JSON value that is not an object.")

        return cls.from_mapping(class_key, parsed, allowed_filenames)

    @staticmethod
    def _proposal_from_value(
        filename: str,
        markdown: Any,
        allowed_filenames: tuple[str, ...],
    ) -> WikiUpdateProposal:
        if not isinstance(markdown, str):
            raise ValueError(
                f"Proposed update for '{filename}' must be a markdown string."
            )
        return WikiUpdateProposal(filename=filename, markdown=markdown).validate(
            allowed_filenames
        )

    def as_mapping(self) -> dict[str, str]:
        return {proposal.filename: proposal.markdown for proposal in self.proposals}

    def markdown_for(self, filename: str) -> str:
        for proposal in self.proposals:
            if proposal.filename == filename:
                return proposal.markdown
        raise ValueError(f"No proposed update for '{filename}'.")


@dataclass(frozen=True)
class LessonPlan:
    class_key: str
    markdown: str

    def validate(self) -> "LessonPlan":
        if not self.class_key.strip():
            raise ValueError("Class key is required.")
        if not self.markdown.strip():
            raise ValueError("Lesson plan is empty.")
        return self
