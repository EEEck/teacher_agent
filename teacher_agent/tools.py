from __future__ import annotations

from typing import Any, Mapping

from teacher_agent.schemas import TARGET_FILENAMES, WikiUpdateBundle

from . import wiki_store


def read_wiki_file(class_key: str, logical_name: str) -> str:
    return wiki_store.read_wiki_file(class_key, logical_name)


def load_class_context(class_key: str) -> dict[str, str]:
    return wiki_store.load_context(class_key)


def prepare_update_bundle(
    class_key: str,
    updates: Mapping[str, Any],
) -> WikiUpdateBundle:
    wiki_store.get_class_config(class_key)
    return WikiUpdateBundle.from_mapping(
        class_key,
        updates,
        TARGET_FILENAMES,
    )


def apply_update_bundle(bundle: WikiUpdateBundle) -> None:
    wiki_store.save_update_bundle(bundle)
