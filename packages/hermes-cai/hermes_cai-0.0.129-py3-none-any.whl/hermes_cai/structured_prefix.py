"""Structured Prefix."""

import json
import logging
from dataclasses import dataclass, field

from decorators import monitor
from pydantic import BaseModel

DEFAULT_TOKEN_LIMIT: int = 7936
DEFAULT_HERMES_GENERATION_TEMPLATE: str = "production_raw.yml.j2"


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
    attachments_type: str | None = None
    chat_id: str | None = None
    turn_id: str | None = None
    candidate_id: str | None = None
    lores: dict[str, str] | None = None


@dataclass(slots=True, frozen=False)
class ConversationFact:
    category: str | None = None
    value: str | None = None


class StructuredPrefix(BaseModel):
    """Structure Prefix."""

    # REQUIRED.
    character_definitions: list[str]
    chat_history: list[str]
    reply_prompt: str
    timestamp: str

    # OPTIONAL.
    pinned_history: list[str] | None = None
    chat_hist_global_index: int = 0
    space_added: bool = False
    token_limit: int = DEFAULT_TOKEN_LIMIT
    use_hermes_generation: bool = False
    # Boolean flags referenced in the production template.
    config: dict[str, bool] = field(default_factory=dict)
    # The actual raw template string passed from upstream components.
    hermes_generation_template: str | None = None
    raw_prompt_data_str: str | None = "{}"
    # Never passed in from upstream components; created by tokenizer.
    raw_prompt_data_dict: dict | None = None
    # The name of the template in the registry to use for Hermes generation.
    hermes_generation_template_name: str = DEFAULT_HERMES_GENERATION_TEMPLATE
    # Raw chat context messages; duplicate of chat_history and pinned_history
    # without upstream formatting.
    chat_context_messages_str: str | None = "[]"
    chat_context_messages: list[ChatContextMessage] | None = None
    conversation_facts: dict[str, list[ConversationFact]] | None = None

    # TODO: pull out contextual_logger into contextvars so we don't have to pass it around.
    @monitor
    def parse_raw_prompt_data(self, contextual_logger: logging.LoggerAdapter):
        """Parse raw prompt data."""
        try:
            self.raw_prompt_data_dict = json.loads(self.raw_prompt_data_str)
        except Exception as ex:
            contextual_logger.error(
                f"### Hermes: Failed to parse raw prompt data: {self.raw_prompt_data_str=} {ex=}"
            )
            self.raw_prompt_data_dict = {}

    # TODO: pull out contextual_logger into contextvars so we don't have to pass it around.
    @monitor
    def parse_chat_context_messages(self, contextual_logger: logging.LoggerAdapter):
        """Parse chat context messages."""
        self.chat_context_messages = []
        if not self.chat_context_messages_str:
            return

        try:
            tmp = json.loads(self.chat_context_messages_str)
            for obj in tmp:
                if "is_summary" not in obj:
                    obj["is_summary"] = False
                if "attachments_content" not in obj:
                    obj["attachments_content"] = ""
                self.chat_context_messages.append(ChatContextMessage(**obj))
        except Exception as ex:
            contextual_logger.error(
                f"### Hermes: Failed to parse chat context messages: {self.chat_context_messages_str=} {ex=}"
            )
