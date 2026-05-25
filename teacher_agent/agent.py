from __future__ import annotations

from teacher_agent.prompts import (
    SYSTEM_PROMPT,
    build_planning_prompt,
    build_structuring_prompt,
)
from teacher_agent.schemas import LessonLogInput, LessonPlan, WikiUpdateBundle
from teacher_agent.tools import load_class_context
from teacher_agent.wiki_store import CLASS_OPTIONS

try:
    from agents import Agent, Runner
except ImportError as exc:
    Agent = None
    Runner = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


def build_agent(name: str) -> "Agent":
    if Agent is None:
        raise RuntimeError(
            "OpenAI Agents SDK is not available. Install dependencies from requirements.txt"
        ) from IMPORT_ERROR
    return Agent(name=name, instructions=SYSTEM_PROMPT)


async def run_agent(prompt: str, agent_name: str) -> str:
    if Runner is None:
        raise RuntimeError(
            "OpenAI Agents SDK is not available. Install dependencies from requirements.txt"
        ) from IMPORT_ERROR

    result = await Runner.run(build_agent(agent_name), input=prompt)
    return result.final_output


async def structure_lesson_notes(lesson_input: LessonLogInput) -> WikiUpdateBundle:
    lesson_input.validate(set(CLASS_OPTIONS))
    context = load_class_context(lesson_input.class_key)
    prompt = build_structuring_prompt(lesson_input.notes, context)
    output = await run_agent(prompt, "memory-structurer")
    return WikiUpdateBundle.from_agent_json(lesson_input.class_key, output)


async def generate_lesson_plan(class_key: str) -> LessonPlan:
    context = load_class_context(class_key)
    prompt = build_planning_prompt(context)
    output = await run_agent(prompt, "lesson-planner")
    return LessonPlan(class_key=class_key, markdown=output).validate()
