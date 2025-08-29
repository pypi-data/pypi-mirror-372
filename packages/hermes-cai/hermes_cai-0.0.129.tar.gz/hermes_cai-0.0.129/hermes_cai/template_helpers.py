"""Helper functions for Hermes CAI template rendering."""

import re
from dataclasses import dataclass

from constants import DEFAULT_USERNAME, NARRATOR_NAME, PRETRUNCATION_TOKENS_PER_MESSAGE

# pylint: disable=unused-import
from contrib.lm_prefix_utils import get_character_priming,get_scene_definition  # noqa: F401
from exceptions import MissingContextDataError


@dataclass(slots=True, frozen=False)
class ChatContextMessage:
    """Chat Context Message."""

    author: str
    text: str
    # Unspecified: 0
    # HumanMessage: 1
    # CharacterMessage: 2
    # SystemMessage: 3
    type: int
    is_pinned: bool
    is_summary: bool
    attachments_content: str
    # Optional.
    is_safety_truncated: bool | None = None
    attachments_content_list: list[str] | None = None
    chat_id: str | None = None
    turn_id: str | None = None
    candidate_id: str | None = None


def maybe_inject_narrator(message: str, default_author: str = NARRATOR_NAME) -> str:
    """Inject narrator into the message if applicable."""
    if re.match(r"^[\w-]+:", message):
        return message
    return f"{default_author}: {message}"


def raise_missing_context_data(key: str):
    """Raise missing data from jinja context."""
    raise MissingContextDataError(f"Missing required key in jinja context: {key=}")


def canonicalize_user_name(name: str | None) -> str:
    """Makes name format consistent with author names we use in training data."""
    # The "-" is used in upstream components and should be overriden to default value.
    if name is None or not name or name == "-":
        return DEFAULT_USERNAME
    return "-".join(name.split())


def pretruncate_messages(
    messages: list[ChatContextMessage], token_limit: int
) -> list[ChatContextMessage]:
    """Pretruncates messages for Hermes generation."""
    message_truncation_step = token_limit // PRETRUNCATION_TOKENS_PER_MESSAGE
    while len(messages) > 2 * message_truncation_step:
        messages = messages[message_truncation_step:]
    return messages
