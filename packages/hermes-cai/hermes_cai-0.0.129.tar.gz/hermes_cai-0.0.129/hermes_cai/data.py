"""Module for preparing template data for Prompt Poet (PP) templates."""

from logging import LoggerAdapter

from constants import DEFAULT_USERNAME, NARRATOR_NAME
from decorators import monitor
from structured_prefix import StructuredPrefix
from template_helpers import (
    canonicalize_user_name,
    get_character_priming,
    maybe_inject_narrator,
    pretruncate_messages,
    raise_missing_context_data,
    get_scene_definition
)


@monitor
def build_template_data(
    structured_prefix: StructuredPrefix,
    logger: LoggerAdapter,
    stream_params: dict | None = None,
    continuation_count: int = 0,
    template_params: dict | None = None,
    special_tokens_mapping: dict | None = None,
    role_tokens_mapping: dict | None = None,
) -> dict:
    """Build template data for Prompt Poet (PP) templates."""
    if stream_params is None:
        stream_params = {}
    if structured_prefix.raw_prompt_data_dict is None:
        structured_prefix.parse_raw_prompt_data(contextual_logger=logger)
    if structured_prefix.chat_context_messages is None:
        structured_prefix.parse_chat_context_messages(contextual_logger=logger)

    # TODO: handle this in the template not in logical layer.
    username = structured_prefix.raw_prompt_data_dict.get("username", "")
    if not username or username == "-":
        username = DEFAULT_USERNAME
    config = structured_prefix.raw_prompt_data_dict.get("config", {})

    return {
        ### Raw prompt data that has not been tampered with ###
        "chat_type": structured_prefix.raw_prompt_data_dict.get("chat_type", ""),
        "character": structured_prefix.raw_prompt_data_dict.get("character", {}),
        "user_country_code": structured_prefix.raw_prompt_data_dict.get(
            "user_country_code", ""
        ),
        "username": username,
        "persona_definition": structured_prefix.raw_prompt_data_dict.get(
            "persona_definition", ""
        ),
        "is_proactive": structured_prefix.raw_prompt_data_dict.get(
            "is_proactive", False
        ),
        "proactive_metadata": structured_prefix.raw_prompt_data_dict.get(
            "proactive_metadata", {}
        ),
        "chat_context_messages": structured_prefix.chat_context_messages,
        "continuation_count": continuation_count,
        "dynamic_greeting_prompt": structured_prefix.raw_prompt_data_dict.get(
            "dynamic_greeting_prompt", ""
        ),
        "character_greeting_prompt": structured_prefix.raw_prompt_data_dict.get(
            "character_greeting_prompt", ""
        ),
        ### Config flags ###
        "should_remove_safety_truncated_messages": config.get(
            "should_remove_safety_truncated_messages", False
        ),
        ###  Constants data ###
        "narrator_name": NARRATOR_NAME,
        ### Legacy prompt data that has been tampered with by upstream components ###
        "character_definition_messages": structured_prefix.character_definitions,
        "pinned_history": structured_prefix.pinned_history or [],
        "chat_history": structured_prefix.chat_history,
        "reply_prompt": structured_prefix.reply_prompt,
        "timestamp": structured_prefix.timestamp,
        ### Filters ###
        # TODO: import ansible core filters instead of custom filters.
        "maybe_inject_narrator": maybe_inject_narrator,
        "get_character_priming": get_character_priming,
        "get_scene_definition": get_scene_definition,
        "canonicalize_user_name": canonicalize_user_name,
        "raise_missing_context_data": raise_missing_context_data,
        "pretruncate_messages": pretruncate_messages,
        "model_id": stream_params.get("model_id", ""),
        "audio_mode_token": stream_params.get("audio_mode_token", ""),
        "audio_mode_instruction_override": (
            stream_params.get("audio_mode_instruction_override", "")
        ),
        "safety_instructions": structured_prefix.raw_prompt_data_dict.get(
            "safety_instructions"
        ),
        "scene_info": structured_prefix.raw_prompt_data_dict.get("scene_info"),
        "attachments_content_list": structured_prefix.raw_prompt_data_dict.get(
            "attachments_content_list", None
        ),
        "conversation_facts": structured_prefix.conversation_facts,
        "template_params": template_params,
        "special_tokens_mapping": special_tokens_mapping,
        "role_tokens_mapping": role_tokens_mapping,
    }
