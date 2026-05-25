from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from teacher_agent.schemas import LessonPlan, TARGET_FILENAMES, WikiUpdateBundle
from teacher_agent.wiki_store import CLASS_OPTIONS


TARGET_MEMORY_FILENAMES = TARGET_FILENAMES


@dataclass(frozen=True)
class ClassOption:
    key: str
    label: str


@dataclass(frozen=True)
class AppBootstrap:
    class_options: tuple[ClassOption, ...]
    api_key_ready: bool


@dataclass(frozen=True)
class MemoryDraft:
    filename: str
    markdown: str


@dataclass(frozen=True)
class StructureLessonRequest:
    class_key: str
    rough_notes: str


@dataclass(frozen=True)
class StructureLessonResponse:
    update_bundle: WikiUpdateBundle


@dataclass(frozen=True)
class GeneratePlanRequest:
    class_key: str


@dataclass(frozen=True)
class GeneratePlanResponse:
    lesson_plan: LessonPlan


@dataclass(frozen=True)
class SaveMemoryRequest:
    update_bundle: WikiUpdateBundle


@dataclass(frozen=True)
class SaveMemoryResponse:
    saved_filenames: tuple[str, ...]


def class_options_from_backend() -> tuple[ClassOption, ...]:
    return tuple(
        ClassOption(key=config.key, label=config.label)
        for config in CLASS_OPTIONS.values()
    )


def class_option_map(options: tuple[ClassOption, ...]) -> dict[str, ClassOption]:
    return {option.key: option for option in options}


def memory_drafts_from_session(
    class_key: str,
    value: Any,
) -> tuple[MemoryDraft, ...]:
    bundle = update_bundle_from_session(class_key, value)
    if bundle is None:
        return ()
    return tuple(
        MemoryDraft(filename=filename, markdown=bundle.markdown_for(filename))
        for filename in TARGET_MEMORY_FILENAMES
    )


def save_memory_request_from_session(
    class_key: str,
    value: Any,
) -> SaveMemoryRequest | None:
    bundle = update_bundle_from_session(class_key, value)
    if bundle is None:
        return None
    return SaveMemoryRequest(update_bundle=bundle)


def update_bundle_from_session(
    class_key: str,
    value: Any,
) -> WikiUpdateBundle | None:
    if value is None:
        return None
    if isinstance(value, WikiUpdateBundle):
        return value
    if isinstance(value, Mapping):
        try:
            return WikiUpdateBundle.from_mapping(class_key, value)
        except ValueError:
            return None
    return None


def lesson_plan_from_session(class_key: str, value: Any) -> LessonPlan | None:
    if value is None:
        return None
    if isinstance(value, LessonPlan):
        return value
    if isinstance(value, str):
        try:
            return LessonPlan(class_key=class_key, markdown=value).validate()
        except ValueError:
            return None
    return None
