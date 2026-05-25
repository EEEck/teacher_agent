from __future__ import annotations

import os

from teacher_agent.agent import generate_lesson_plan, structure_lesson_notes
from teacher_agent.contracts import (
    AppBootstrap,
    GeneratePlanRequest,
    GeneratePlanResponse,
    SaveMemoryRequest,
    SaveMemoryResponse,
    StructureLessonRequest,
    StructureLessonResponse,
    class_options_from_backend,
)
from teacher_agent.schemas import LessonLogInput
from teacher_agent.tools import apply_update_bundle


def bootstrap_app() -> AppBootstrap:
    return AppBootstrap(
        class_options=class_options_from_backend(),
        api_key_ready="OPENAI_API_KEY" in os.environ,
    )


async def structure_lesson(request: StructureLessonRequest) -> StructureLessonResponse:
    lesson_input = LessonLogInput(
        class_key=request.class_key,
        notes=request.rough_notes,
    )
    return StructureLessonResponse(
        update_bundle=await structure_lesson_notes(lesson_input)
    )


async def generate_plan(request: GeneratePlanRequest) -> GeneratePlanResponse:
    return GeneratePlanResponse(
        lesson_plan=await generate_lesson_plan(request.class_key)
    )


def save_memory(request: SaveMemoryRequest) -> SaveMemoryResponse:
    apply_update_bundle(request.update_bundle)
    return SaveMemoryResponse(
        saved_filenames=tuple(
            proposal.filename for proposal in request.update_bundle.proposals
        )
    )
