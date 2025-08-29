"""Tests for the hermes_engine module."""
import json
import re
import unittest
from itertools import combinations
from logging import LoggerAdapter
from unittest.mock import MagicMock, patch

from constants import TRUNCATION_STEPS_CHOICES, BOM, EOM
from contrib.lm_prefix_utils import get_tokenizer, MAX_USED_DEFINITION_LEN, \
    get_character_priming
from engine import StructuredPrefix, build_structured_prefix, HERE, \
    DEFAULT_TEMPLATE_DIR, MonitoredPrompt, DEFAULT_TEMPLATE_NAME, \
    DEFAULT_TRUNCATION_STEP, USE_TEMPLATE_CACHING
from exceptions import MissingContextDataError
from structured_prefix import ChatContextMessage, ConversationFact


# Mock version of the function for testing purposes
def mock_raise_missing_context_data(key):
    del key
    # The function does nothing, it's just a placeholder for testing


def mock_get_character_priming(character, username, *, truncation_length=MAX_USED_DEFINITION_LEN):
    del character
    del username
    return [
        {
            "src": "Foo",
            "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        }
    ]


def mock_canonicalize_name(name):
    return name


MOCK_USERNAME = "jeff"
MOCK_CHARACTER = {"participant__name": "balderdash"}


class TestBuildStructuredPrefix(unittest.TestCase):
    """Tests for the build_structured_prefix function."""

    def setUp(self):
        """Initialize the test case."""
        # Mock the ContextualLogger to test logging without side effects
        self.mock_logger = MagicMock(spec=LoggerAdapter)
        self.tokenizer = get_tokenizer()
        self.encode_func = self.tokenizer.tokenize
        self.template_patcher = patch("engine.DEFAULT_TEMPLATE_DIR", "../../templates/chat_stack/default/templates")
        self.template_patcher.start()

    def test_narrator_injection(self):
        """Test that the function injects narrator name on character definition messages."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but?",
                "Balderdash: but I lie about my past",
                "needle-in-haystack",
            ],
            pinned_history=[""],
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Assert that the total token count is within the limit
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertIn("narrator: needle-in-haystack", prompt_string)

    def test_audio_mode_instruction(self):
        """Test that audio mode instruction is used correctly."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but?",
                "Balderdash: but I lie about my past",
            ],
            token_limit=1000,
            pinned_history=[""],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[],
            hermes_generation_template_name="production_raw.yml.j2",
            chat_context_messages=[
                ChatContextMessage(
                    author="Balderdash",
                    text="filler",
                    type=1,
                    is_pinned=False,
                    is_summary=False,
                    attachments_content="",
                )
            ],
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "Character Title",
                    "description": "Character Description",
                    "definition": "Character Definition",
                    "sanitized_definition": "Character Sanitized Definition"
                },
                "user_country_code": "US",
                "persona_definition": "Persona Definition",
                "is_proactive": false
                }""",
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
        )

        stream_params = {"model_id": "heather_voice"}
        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            stream_params=stream_params,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertTrue(prompt_string.endswith("<|AudioMode|>"))
        self.assertIn(
            "<|beginningofmessage|>Additional Instructions:\nWhenever you see the text <|AudioMode|>, switch to using spoken language that reflects a conversational style.",
            prompt_string,
        )

        # Test audio mode overrides.
        stream_params["audio_mode_token"] = "audio_mode_token"  # noqa: S105
        stream_params["audio_mode_instruction_override"] = (
            "If you see the text audio_mode_token use a more conversational style."
        )
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            stream_params=stream_params,
            encode_func=self.encode_func,
        )

        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertTrue(prompt_string.endswith("audio_mode_token"))
        self.assertIn(
            "<|beginningofmessage|>If you see the text audio_mode_token use a more conversational style.",
            prompt_string,
        )
        self.assertNotIn(
            "<|beginningofmessage|>Additional Instructions:\nWhenever you see the text <|AudioMode|>, switch to using spoken language that reflects a conversational style.",
            prompt_string,
        )

        # Test audio mode disabled.
        stream_params["model_id"] = "heather"
        stream_params.pop("audio_mode_token")
        stream_params.pop("audio_mode_instruction_override")
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            stream_params=stream_params,
            encode_func=self.encode_func,
        )

        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertNotIn("audio_mode_token", prompt_string)
        self.assertNotIn("<|AudioMode|>", prompt_string)
        self.assertNotIn(
            "<|beginningofmessage|>If you see the text audio_mode_token use a more conversational style.",
            prompt_string,
        )
        self.assertNotIn(
            "<|beginningofmessage|>Additional Instructions:\nWhenever you see the text <|AudioMode|>, switch to using spoken language that reflects a conversational style.",
            prompt_string,
        )

    def test_below_token_limit(self):
        """Test that the function does not truncate messages when the token limit is not exceeded."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but?",
                "Balderdash: but I lie about my past",
            ],
            pinned_history=["First pinned message."],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        context_tokens = result["tokenized_context"].tokens

        # Assert that the total token count is within the limit
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertGreaterEqual(len(context_tokens), 100)
        self.assertIn(
            "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            prompt_string,
        )

    def test_above_token_limit(self):
        """Test that the function truncates messages when the token limit is exceeded."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but?",
                "Balderdash: but I lie about my past",
            ],
            pinned_history=[""],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            token_limit=100,
            hermes_generation_template_name="production.yml.j2",
        )

        # Assert that the total token count is within the limit
        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

    def test_pretruncation_step(self):
        """Test the pretruncation step truncates the appropriate messages."""
        chat_context_messages = [
            ChatContextMessage(
                author="Balderdash",
                text="filler",
                type=1,
                is_pinned=False,
                is_summary=False,
                attachments_content="",
            )
        ] * 200
        chat_context_messages[0] = ChatContextMessage(
            author="Balderdash",
            text="This message should be pretruncated.",
            type=1,
            is_pinned=False,
            is_summary=False,
            attachments_content="",
        )
        chat_context_messages.append(
            ChatContextMessage(
                author="Balderdash",
                text="This message should NOT be pretruncated.",
                type=1,
                is_pinned=False,
                is_summary=False,
                attachments_content="",
            )
        )
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but?",
                "Balderdash: but I lie about my past",
            ],
            token_limit=1000,
            pinned_history=[""],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[],
            hermes_generation_template_name="production_raw.yml.j2",
            chat_context_messages=chat_context_messages,
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "Character Title",
                    "description": "Character Description",
                    "definition": "Character Definition",
                    "sanitized_definition": "Character Sanitized Definition"
                },
                "user_country_code": "US",
                "persona_definition": "Persona Definition",
                "is_proactive": false
                }""",
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
        )

        # Execute the function under test
        result = build_structured_prefix(
            self.mock_logger,
            structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Assert that the total token count is within the limit
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertIn("This message should NOT be pretruncated", prompt_string)
        self.assertNotIn("This message should be pretruncated", prompt_string)

    def test_truncation_steps(self):
        """Test that the function truncates messages when the token limit is exceeded."""
        # Total tokens is 1285 - don't change the inputs!
        chat_history = ["Name: Lorem ipsum dolor sit"] * 105
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but?",
                "Balderdash: but I lie about my past",
            ],
            pinned_history=[],
            # Each message is exactly 10 tokens (with bom/eom) therefore truncation will happen in multiples of 10.
            chat_history=chat_history,
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            token_limit=1024,
            hermes_generation_template_name="production.yml.j2",
        )

        expected_token_counts = [1019, 929, 879, 629, 379, 129, 79, 79]
        for truncation_step, expectation in zip(
            [1, 100, *TRUNCATION_STEPS_CHOICES], expected_token_counts, strict=False
        ):
            result = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=structured_prefix,
                truncation_step=truncation_step,
                encode_func=self.encode_func,
            )
            self.assertEqual(len(result["tokenized_context"].tokens), expectation)

        # With empty character definitions.
        structured_prefix.character_definitions = []
        expected_token_counts = [1014, 954, 804, 554, 304, 54, 14, 14]
        for truncation_step, expectation in zip(
            [1, 100, *TRUNCATION_STEPS_CHOICES], expected_token_counts, strict=False
        ):
            result = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=structured_prefix,
                truncation_step=truncation_step,
                encode_func=self.encode_func,
            )
            self.assertEqual(len(result["tokenized_context"].tokens), expectation)

    def test_include_pins(self):
        """Test that pinned history is included in the tokenized context."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but? Balderdash: but I lie about my past",
            ],
            # This will require roughly 125 tokens with current vocab.
            pinned_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        context_tokens = result["tokenized_context"].tokens
        # Assert that the total token count is within the limit
        self.assertGreater(
            len(context_tokens), 300
        )  # char_def and chat_history takes approx 210

    def test_persona_injection(self):
        """Test that persona injection WAI."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but? Balderdash: but I lie about my past",
                'jeff\'s self-intro is "name: Jeff\neye color: redname: Jeff"',
            ],
            # This will require roughly 125 tokens with current vocab.
            pinned_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        context_tokens = result["tokenized_context"].tokens
        # Assert that the total token count is within the limit
        self.assertGreater(
            len(context_tokens), 300
        )  # char_def and chat_history takes approx 210

    def test_return_keys(self):
        """Test that the return payload contains expected keys."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but? Balderdash: but I lie about my past",
                'jeff\'s self-intro is "name: Jeff\neye color: redname: Jeff"',
            ],
            # This will require roughly 125 tokens with current vocab.
            pinned_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        for k in [
            "character_definitions",
            "chat_history",
            "chat_hist_global_index",
            "reply_prompt",
            "space_added",
            "token_limit",
            "tokenized_context",
            "timestamp",
        ]:
            self.assertIn(k, result)

    def test_edge_cases(self):
        """Test that edge cases are handled correctly."""
        # Missing character definitions still passes valid prompt regex.
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[],
            # This will require roughly 125 tokens with current vocab.
            pinned_history=[
                "Jeff: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Balderdash: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Jeff: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Balderdash: Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Balderdash: Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Jeff: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Balderdash: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Jeff: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Balderdash: Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Jeff: Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Missing pinned history still passes valid prompt regex.
        structured_prefix = StructuredPrefix(
            character_definitions=[],
            pinned_history=[],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Balerdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

    def test_whitespace_injection(self):
        """Test that whitespace is injected where appropriate e.g. `<|space|>`."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but? Balderdash: but I lie about my past",
                'jeff\'s self-intro is "name: Jeff\neye color: redname: Jeff"',
            ],
            # This will require roughly 125 tokens with current vocab.
            pinned_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertIn("2024 04 23 Tuesday Odin", prompt_string)

    def test_raw_prompt_data(self):
        """Test that raw prompt data is interpolated correctly."""
        structured_prefix = StructuredPrefix(
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but? Balderdash: but I lie about my past",
                'jeff\'s self-intro is "name: Jeff\neye color: redname: Jeff"',
            ],
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            hermes_generation_template_name="test.yml.j2",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "Character Title",
                    "description": "Character Description",
                    "definition": "Character Definition",
                    "sanitized_definition": "Character Sanitized Definition"
                },
                "user_country_code": "US",
                "persona_definition": "Persona Definition",
                "is_proactive": false
                }""",
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)

        for needle in [
            "ONE_ON_ONE",
            "Balderdash",
            "Character Title",
            "Character Description",
            "Character Definition",
            "Character Sanitized Definition",
            "User country code is: US",
            "Persona Definition",
        ]:
            self.assertIn(
                needle,
                prompt_string,
            )

    def test_conversation_facts(self):
        """Test that conversation facts is interpolated correctly."""
        conversation_facts = {
            "participant A": [
                ConversationFact(category="category A", value="value A"),
                ConversationFact(category="category B", value="value B"),
            ],
            "participant B": [
                ConversationFact(category="category C", value="value C"),
                ConversationFact(category="category D", value="value D"),
            ]
        }
        structured_prefix = StructuredPrefix(
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but? Balderdash: but I lie about my past",
                'jeff\'s self-intro is "name: Jeff\neye color: redname: Jeff"',
            ],
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            hermes_generation_template_name="test.yml.j2",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "Character Title",
                    "description": "Character Description",
                    "definition": "Character Definition",
                    "sanitized_definition": "Character Sanitized Definition"
                },
                "user_country_code": "US",
                "persona_definition": "Persona Definition",
                "is_proactive": false
                }""",
            conversation_facts=conversation_facts,
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        # extract substring between START_FACTS and END_FACTS
        match = re.search(r"START_FACTS(.*?)END_FACTS", prompt_string, re.DOTALL)
        self.assertTrue(match, "FACTS not found in prompt")
        facts = match.group(1)
        lines = []
        for line in facts.splitlines():
            l = line.strip()
            if l:
                lines.append(line.strip())
        got = "\n".join(lines)
        lines = []
        for participant, facts in conversation_facts.items():
            lines.append(f"PARTICIPANT: {participant}")
            for fact in facts:
                lines.append(f"- {fact.category}: {fact.value}")
        want = "\n".join(lines)
        self.assertEqual(got, want, f"Incorrect facts {got=} {want=}")

    def test_template_params(self):
        """Test template params."""
        chat_history = [
            "Message 1",
            "Message 2",
            "Message 3",
            "Message 4",
            "Message 5",
        ]
        max_chat_history = 2
        structured_prefix = StructuredPrefix(
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but? Balderdash: but I lie about my past",
                'jeff\'s self-intro is "name: Jeff\neye color: redname: Jeff"',
            ],
            chat_history=chat_history,
            reply_prompt="Balderdash:",
            hermes_generation_template_name="test.yml.j2",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "Character Title",
                    "description": "Character Description",
                    "definition": "Character Definition",
                    "sanitized_definition": "Character Sanitized Definition"
                },
                "user_country_code": "US",
                "persona_definition": "Persona Definition",
                "is_proactive": false
                }""",
        )
        template_params = {
            "max_chat_history": max_chat_history,
        }
        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            template_params=template_params,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        # extract substring between START_TEMPLATE_PARAMS and END_TEMPLATE_PARAMS
        match = re.search(r"START_TEMPLATE_PARAMS(.*?)END_TEMPLATE_PARAMS", prompt_string, re.DOTALL)
        self.assertTrue(match, "Template params not found in prompt")
        msgs = match.group(1)
        lines = []
        for line in msgs.splitlines():
            l = line.strip()
            if l:
                lines.append(line.strip())
        got = "\n".join(lines)
        want = "\n".join(chat_history[-max_chat_history:])
        self.assertEqual(got, want, f"Messages doesn't match {got=} {want=}")

    def _build_prompts_with_templates(
        self, structured_prefix: StructuredPrefix, template_names: list[str]
    ) -> dict[str, str]:
        if not template_names:
            raise ValueError("At least one template name must be provided.")

        retval = {}
        for template_name in template_names:
            structured_prefix.hermes_generation_template_name = template_name
            result = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=structured_prefix,
                truncation_step=1,
                encode_func=self.encode_func,
            )
            retval[template_name] = self.tokenizer.detokenize(
                result["tokenized_context"].tokens
            )
        return retval

    def _compare_prompt_map(self, prompt_map: dict[str, str]):
        self.maxDiff = None
        for (template_name_a, prompt_a), (template_name_b, prompt_b) in combinations(
            prompt_map.items(), 2
        ):
            self.assertEqual(
                prompt_a,
                prompt_b,
                f"Prompts do not match: \n\n\t({template_name_a=}, {prompt_a=})\n\n\t({template_name_b}, {prompt_b=})",
            )

    def test_production_template_parity(self):
        """Test that the production template is equivalent to the raw template."""
        # Full of data.
        base_structured_prefix = StructuredPrefix(
            character_definitions=[
                "Balderdash: Character Title - Character Description",
                "narrator: Jeff's self-intro is Persona Definition",
                "Balderdash: Character Sanitized Definition",
            ],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            pinned_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "Character Title",
                    "description": "Character Description",
                    "definition": "Balderdash: Character Definition",
                    "sanitized_definition": "Balderdash: Character Sanitized Definition"
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "Persona Definition",
                "is_proactive": false
                }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": false
                }
            ]""",
        )
        template_names = ["production_raw.yml.j2"]

        prompt_map = self._build_prompts_with_templates(
            structured_prefix=base_structured_prefix.model_copy(),
            template_names=template_names,
        )
        self._compare_prompt_map(prompt_map=prompt_map)

        # Missing character definition messages.
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            pinned_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "",
                    "description": "",
                    "definition": "",
                    "sanitized_definition": ""
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "",
                "is_proactive": false
                }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": false
                }
            ]""",
        )
        prompt_map = self._build_prompts_with_templates(
            structured_prefix=base_structured_prefix.model_copy(),
            template_names=template_names,
        )
        self._compare_prompt_map(prompt_map=prompt_map)

        # Only character title.
        base_structured_prefix = StructuredPrefix(
            character_definitions=["Balderdash: Character Title"],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "Character Title",
                    "description": "",
                    "definition": "",
                    "sanitized_definition": ""
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "",
                "is_proactive": false
                }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": false
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": false
                }
            ]""",
        )
        prompt_map = self._build_prompts_with_templates(
            structured_prefix=base_structured_prefix.model_copy(),
            template_names=template_names,
        )
        self._compare_prompt_map(prompt_map=prompt_map)

        base_structured_prefix = StructuredPrefix(
            character_definitions=["narrator: Jeff's self-intro is Persona definition"],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "",
                    "description": "",
                    "definition": "",
                    "sanitized_definition": ""
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "Persona definition",
                "is_proactive": false
                }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": false
                }
            ]""",
        )
        prompt_map = self._build_prompts_with_templates(
            structured_prefix=base_structured_prefix.model_copy(),
            template_names=template_names,
        )
        self._compare_prompt_map(prompt_map=prompt_map)

    def test_names(self):
        """Tests that a default value is used for empty names."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            hermes_generation_template_name="production_raw.yml.j2",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "",
                "user_country_code": "US",
                "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": false
                }
            ]""",
        )
        # Will fail template validation on empty username.
        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Test for both templates.
        base_structured_prefix.hermes_generation_template_name = "production.yml.j2"
        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Allow username to have underscores.
        base_structured_prefix.character_definitions = ["User_: Who are you?"]
        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Allow any unicode name.
        base_structured_prefix.character_definitions = ["Usér_: Who are you?"]
        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Allow any unicode name.
        base_structured_prefix.character_definitions = ["Хван-Хенджин: Who are you?"]
        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Allow any unicode name.
        base_structured_prefix.character_definitions = ["李小龙: Who are you?"]
        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

    def test_production_raw_template(self):
        """Test the basic mechanics of the raw template."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            hermes_generation_template_name="production_raw.yml.j2",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": false
                }
            ]""",
        )

        # Tests that persona is spliced in correctly after first character definition message (title and description).
        structured_prefix = base_structured_prefix.model_copy()
        structured_prefix.raw_prompt_data_str = """{
            "chat_type": "ONE_ON_ONE",
            "character": {
                "participant__name": "Balderdash",
                "title": "A great Character",
                "description": "Tongue in cheek.",
                "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
            },
            "username": "Jeff",
            "user_country_code": "US",
            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
            "is_proactive": false
        }"""

        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertRegex(
            prompt_string,
            r"^.*Balderdash: A great Character - Tongue in cheek.*name: Jeff\neye color: red\nname: Jeff.*Jeff: Who are you?<|endofmessage|><|beginningofmessage|>\nBalderdash: I'm The Balderdash!.*$",
        )

        # Tests that it is resilient to no character definition messages.
        structured_prefix = base_structured_prefix.model_copy()
        structured_prefix.raw_prompt_data_str = """{
            "chat_type": "ONE_ON_ONE",
            "character": {
                "participant__name": "Balderdash",
                "title": "",
                "description": "",
                "definition": "",
                "sanitized_definition": ""
            },
            "username": "Jeff",
            "user_country_code": "US",
            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
            "is_proactive": false
        }"""

        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Tests that persona exists if character definition is empty.
        structured_prefix = base_structured_prefix.model_copy()
        structured_prefix.raw_prompt_data_str = """{
            "chat_type": "ONE_ON_ONE",
            "character": {
                "participant__name": "Balderdash",
                "title": "A great Character",
                "description": "Tongue in cheek.",
                "definition": "",
                "sanitized_definition": ""
            },
            "username": "Jeff",
            "user_country_code": "US",
            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
            "is_proactive": false
        }"""

        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertRegex(
            prompt_string,
            r"^.*Balderdash: A great Character - Tongue in cheek.*name: Jeff\neye color: red\nname: Jeff.*$",
        )

        # Tests that raises on missing character from prompt data.
        structured_prefix = base_structured_prefix.model_copy()
        structured_prefix.raw_prompt_data_str = """{
            "chat_type": "ONE_ON_ONE",
            "username": "Jeff",
            "user_country_code": "US",
            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
            "is_proactive": false
        }"""

        with self.assertRaisesRegex(MissingContextDataError, r".*character.*"):
            _ = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=structured_prefix,
                truncation_step=1,
                encode_func=self.encode_func,
            )

        # Tests that pins are correctly interleaved.
        structured_prefix = base_structured_prefix.model_copy()
        structured_prefix.chat_context_messages_str = """[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": true
                }
            ]"""

        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        # One after first pin and one at the end
        self.assertEqual(prompt_string.count("narrator: [some messages omitted]"), 2)

        # Tests that pins are not interleaved.
        structured_prefix = base_structured_prefix.model_copy()
        structured_prefix.chat_context_messages_str = """[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": true
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": true
                }
            ]"""

        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        # Only one at the end
        self.assertEqual(prompt_string.count("narrator: [some messages omitted]"), 1)

    def test_production_raw_template_configs(self):
        shared_params = {
            "character_definitions": [],
            "chat_history": [
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            "reply_prompt": "Balderdash:",
            "timestamp": "2024 04 23 Tuesday 19 07",
            "chat_context_messages_str": """[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true, "is_safety_truncated": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false, "is_safety_truncated": true
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": false
                }
            ]""",
        }
        minors_raw_prompt_data_str = """{
            "chat_type": "ONE_ON_ONE",
            "character": {
                "participant__name": "Balderdash",
                "title": "A great Character",
                "description": "Tongue in cheek.",
                "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
            },
            "username": "Jeff",
            "user_country_code": "US",
            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
            "is_proactive": false,
            "config": {
                "should_remove_safety_truncated_messages": true
            }
        }"""
        minors_structured_prefix = StructuredPrefix(
            **shared_params, raw_prompt_data_str=minors_raw_prompt_data_str
        )
        minors_result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=minors_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        # Assert that safety truncated messages (both pinned and unpinned) are omitted.
        minors_prompt_string = self.tokenizer.detokenize(
            minors_result["tokenized_context"].tokens
        )
        self.assertNotIn(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            minors_prompt_string,
        )
        self.assertNotIn(
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            minors_prompt_string,
        )

        standard_raw_prompt_data_str = """{
            "chat_type": "ONE_ON_ONE",
            "character": {
                "participant__name": "Balderdash",
                "title": "A great Character",
                "description": "Tongue in cheek.",
                "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
            },
            "username": "Jeff",
            "user_country_code": "US",
            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
            "is_proactive": false
        }"""
        standard_structured_prefix = StructuredPrefix(
            **shared_params, raw_prompt_data_str=standard_raw_prompt_data_str
        )
        standard_result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=standard_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        # Assert that safety truncated messages (both pinned and unpinned) are still in the prompt.
        standard_prompt_string = self.tokenizer.detokenize(
            standard_result["tokenized_context"].tokens
        )
        self.assertIn(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            standard_prompt_string,
        )
        self.assertIn(
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            standard_prompt_string,
        )

    def test_production_raw_template_with_attachments_content(self):
        """Test the production raw template prompt with attachments content."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash",
                    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "type": 2,
                    "is_pinned": true
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "attachments_content": "only one attachment"
                },
                {
                    "author": "Balderdash",
                    "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                    "type": 2,
                    "is_pinned": false,
                    "attachments_content": "first attachment, second attachment"
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "is_summary": true,
                    "attachments_content": null
                }
            ]""",
        )
        res = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            use_gcs_template=True,
            gcs_template_path="chat_stack/default/templates/production_raw.yml.j2",
        )
        # The attachments content should be injected into the prompt.
        self.assertIn(
            "narrator: You're looking at the contents shared by Jeff: only one attachment",
            self.tokenizer.detokenize(res["tokenized_context"].tokens),
        )
        self.assertIn(
            "narrator: You're looking at the contents shared by Balderdash: first attachment, second attachment",
            self.tokenizer.detokenize(res["tokenized_context"].tokens),
        )

        self.assertNotIn(
            "should not be injected",
            self.tokenizer.detokenize(res["tokenized_context"].tokens),
        )

        prefix_no_attachments = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Linda: New message with no attachments",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "Linda",
                "user_country_code": "US",
                "persona_definition": "name: Linda\\neye color: red\\nname: Linda",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true, "is_summary": true, "attachments_content_list": ["should not be injected"]
                },
                {
                    "author": "Linda", "text": "New message with no attachments", "type": 1, "is_pinned": false
                }
            ]""",
        )
        res_no_attachments = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=prefix_no_attachments,
            truncation_step=1,
            encode_func=self.encode_func,
            use_gcs_template=True,
            gcs_template_path="chat_stack/chat_attachment_exp/templates/production_raw.yml.j2",
        )
        # If there is no attachments content, the narrator message should not be injected.
        self.assertNotIn(
            "narrator: Jeff had shared",
            self.tokenizer.detokenize(res_no_attachments["tokenized_context"].tokens),
        )

    def test_production_raw_template_with_custom_attachments_prompt(self):
        """Test the production raw template prompt with custom attachments prompt."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash",
                    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "type": 2,
                    "is_pinned": true
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "attachments_content": "image description",
                    "attachments_type": "TYPE_IMAGE"
                },
                {
                    "author": "Balderdash",
                    "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                    "type": 2,
                    "is_pinned": false,
                    "attachments_content": "sticker description",
                    "attachments_type": "TYPE_STICKER"
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "is_summary": true,
                    "attachments_content": "image description without type"
                }
            ]""",
        )
        template_params = {
            "image_prompt_format_prefix": "narrator: prefix ",
            "image_prompt_format_suffix": " shared an image ",
            "sticker_prompt_format_prefix": "",
            "sticker_prompt_format_suffix": ": gifted a sticker ",
        }
        res = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            use_gcs_template=False,
            template_params=template_params,
        )
        result = self.tokenizer.detokenize(res["tokenized_context"].tokens)
        # The attachments content should be injected into the prompt.
        self.assertIn(
            "narrator: prefix Jeff shared an image image description",
            result,
        )
        self.assertIn(
            "Balderdash: gifted a sticker sticker description",
            result,
        )
        self.assertIn(
            "narrator: prefix Jeff shared an image image description without type",
            result,
        )

    def test_vllm_mistral_template(self):
        """Test vllm mistral template prompt."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name=str(HERE/".."/".."/DEFAULT_TEMPLATE_DIR/"chat_stack/vllm_mistral/templates/production_raw.yml.j2"),
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash",
                    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "type": 2,
                    "is_pinned": true
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "attachments_content": "image description",
                    "attachments_type": "TYPE_IMAGE"
                },
                {
                    "author": "Balderdash",
                    "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                    "type": 2,
                    "is_pinned": false,
                    "attachments_content": "sticker description",
                    "attachments_type": "TYPE_STICKER"
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "is_summary": true,
                    "attachments_content": "image description without type"
                }
            ]""",
        )
        template_params = {
            "image_prompt_format_prefix": "narrator: prefix ",
            "image_prompt_format_suffix": " shared an image ",
            "sticker_prompt_format_prefix": "",
            "sticker_prompt_format_suffix": ": gifted a sticker ",
        }
        res = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            use_gcs_template=False,
            template_params=template_params,
        )
        self.assertEqual(len(res["prompt"].messages), 6)

    def test_special_token_overrides_all_overriden(self):
        """Test special token overrides."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                        "chat_type": "ONE_ON_ONE",
                        "character": {
                            "participant__name": "Balderdash",
                            "title": "A great Character",
                            "description": "Tongue in cheek.",
                            "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                            "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                        },
                        "username": "Jeff",
                        "user_country_code": "US",
                        "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                        "is_proactive": false
                    }""",
            chat_context_messages_str="""[
                        {
                            "author": "Balderdash",
                            "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                            "type": 2,
                            "is_pinned": true
                        },
                        {
                            "author": "Jeff",
                            "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                            "type": 1,
                            "is_pinned": false,
                            "attachments_content": "only one attachment"
                        },
                        {
                            "author": "Balderdash",
                            "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                            "type": 2,
                            "is_pinned": false,
                            "attachments_content": "first attachment, second attachment"
                        },
                        {
                            "author": "Jeff",
                            "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                            "type": 1,
                            "is_pinned": false,
                            "is_summary": true,
                            "attachments_content": null
                        }
                    ]""",
        )


        special_tokens_mapping = {
            'bod': "<|CUSTOM_BOD|>",
            'bom': "<|CUSTOM_BOM|>",
            'eom': "<|CUSTOM_EOM|>",
            'space': "<|CUSTOM_SPACE|>",
            'start_token': "<|CUSTOM_START|>",
            'audio_mode_token': "<|CUSTOM_AUDIO|>"
        }

        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            special_tokens_mapping=special_tokens_mapping,
        )

        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)

        self.assertIn("<|CUSTOM_BOD|>", prompt_string, "Custom BOD token not found in prompt")
        self.assertIn("<|CUSTOM_BOM|>", prompt_string, "Custom BOM token not found in prompt")
        self.assertIn("<|CUSTOM_EOM|>", prompt_string, "Custom EOM token not found in prompt")


        self.assertNotIn("<|beginningofdialog|>", prompt_string, "Default BOD token found in prompt")
        self.assertNotIn("<|beginningofmessage|>", prompt_string, "Default BOM token found in prompt")
        self.assertNotIn("<|endofmessage|>", prompt_string, "Default EOM token found in prompt")

    def test_special_token_overrides_some_overriden(self):
            """Test special token overrides."""
            base_structured_prefix = StructuredPrefix(
                character_definitions=[],
                chat_history=[
                    "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                ],
                reply_prompt="Balderdash:",
                timestamp="2024 04 23 Tuesday 19 07",
                raw_prompt_data_str="""{
                            "chat_type": "ONE_ON_ONE",
                            "character": {
                                "participant__name": "Balderdash",
                                "title": "A great Character",
                                "description": "Tongue in cheek.",
                                "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                                "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                            },
                            "username": "Jeff",
                            "user_country_code": "US",
                            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                            "is_proactive": false
                        }""",
                chat_context_messages_str="""[
                            {
                                "author": "Balderdash",
                                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                                "type": 2,
                                "is_pinned": true
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "attachments_content": "only one attachment"
                            },
                            {
                                "author": "Balderdash",
                                "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                                "type": 2,
                                "is_pinned": false,
                                "attachments_content": "first attachment, second attachment"
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "is_summary": true,
                                "attachments_content": null
                            }
                        ]""",
            )

            special_tokens_mapping = {
                'bod': "<|CUSTOM_BOD|>",
            }

            result = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=base_structured_prefix,
                truncation_step=1,
                encode_func=self.encode_func,
                special_tokens_mapping=special_tokens_mapping,
            )

            prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)

            self.assertIn("<|CUSTOM_BOD|>", prompt_string, "Custom BOD token not found in prompt")
            self.assertIn("<|beginningofmessage|>", prompt_string, "Custom BOM token not found in prompt")

    def test_production_raw_template_with_lores(self):
        """Test the production raw template prompt with lores."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash",
                    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "type": 2,
                    "is_pinned": true
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "lores": {
                        "lore1": "lore1 content",
                        "lore2": "lore2 content"
                    }
                }
            ]""",
        )
        res = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            use_gcs_template=False,
        )
        # The lores should be injected into the prompt.
        self.assertIn(
            "narrator: lore1 - lore1 content\nlore2 - lore2 content",
            self.tokenizer.detokenize(res["tokenized_context"].tokens),
        )

    def test_production_raw_template_with_continuations(self):
        """Test the production raw template prompt with continuations."""
        use_cases = [
            {
                "name": "last message belongs to the user",
                "reply_prompt": "Balderdash:",
                "messages": """[
                    {
                        "author": "Balderdash",
                        "text": "Character Message 1",
                        "type": 2,
                        "is_pinned": false
                    },
                    {
                        "author": "Jeff",
                        "text": "User Message 1.",
                        "type": 1,
                        "is_pinned": false
                    }
                ]""",
                "expected_messages": 2,
                "expected_last_message": "Jeff: User Message 1.",
            },
            {
                "name": "last message belongs to the character",
                "reply_prompt": "Balderdash:",
                "messages": """[
                    {
                        "author": "Balderdash",
                        "text": "Character Message 1",
                        "type": 2,
                        "is_pinned": false
                    },
                    {
                        "author": "Jeff",
                        "text": "User Message 1.",
                        "type": 1,
                        "is_pinned": false
                    },
                    {
                        "author": "Balderdash",
                        "text": "Character Message 2",
                        "type": 2,
                        "is_pinned": false
                    }
                ]""",
                "expected_messages": 4,
                "expected_last_message": "narrator: *continue*",
            },
            {
                "name": "last message belongs to the character with non-character reply prompt",
                "reply_prompt": "Elon:",
                "messages": """[
                    {
                        "author": "Balderdash",
                        "text": "Character Message 1",
                        "type": 2,
                        "is_pinned": false
                    },
                    {
                        "author": "Jeff",
                        "text": "User Message 1.",
                        "type": 1,
                        "is_pinned": false
                    },
                    {
                        "author": "Balderdash",
                        "text": "Character Message 2",
                        "type": 2,
                        "is_pinned": false
                    }
                ]""",
                "expected_messages": 3,
                "expected_last_message": "Balderdash: Character Message 2",
            },
            {
                "name": "last message belongs to the character with extended reply prompt",
                "reply_prompt": "Balderdash: some message here",
                "messages": """[
                    {
                        "author": "Balderdash",
                        "text": "Character Message 1",
                        "type": 2,
                        "is_pinned": false
                    },
                    {
                        "author": "Jeff",
                        "text": "User Message 1.",
                        "type": 1,
                        "is_pinned": false
                    },
                    {
                        "author": "Balderdash",
                        "text": "Character Message 2",
                        "type": 2,
                        "is_pinned": false
                    }
                ]""",
                "expected_messages": 4,
                "expected_last_message": "narrator: *continue*",
            },
        ]
        for use_case in use_cases:
            messages = use_case["messages"]
            messages_json = json.loads(messages)
            chat_history = [f"{msg['author']}: {msg['text']}" for msg in messages_json]
            base_structured_prefix = StructuredPrefix(
                character_definitions=[],
                chat_history=chat_history,
                reply_prompt=use_case["reply_prompt"],
                timestamp="2024 04 23 Tuesday 19 07",
                hermes_generation_template_name=str(HERE/".."/".."/DEFAULT_TEMPLATE_DIR/"chat_stack/default/templates/production_raw.yml.j2"),
                raw_prompt_data_str="""{
                    "chat_type": "ONE_ON_ONE",
                    "character": {
                        "participant__name": "Balderdash",
                        "title": "A great Character",
                        "description": "Tongue in cheek.",
                        "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...\\n{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                        "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...\\n{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                    },
                    "username": "Jeff",
                    "user_country_code": "US",
                    "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                    "is_proactive": false
                }""",
                chat_context_messages_str=messages,
            )
            res = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=base_structured_prefix,
                truncation_step=1,
                encode_func=self.encode_func,
                use_gcs_template=False,
                template_params={"use_continuations": True},
            )
            result = self.tokenizer.detokenize(res["tokenized_context"].tokens)
            messages_without_chat_history = 10  # 1 - date, 1 - character description, 6 - character definition, 1 - persona definition, 1 - reply prompt
            self.assertEqual(len(res["prompt"].messages), messages_without_chat_history + use_case["expected_messages"], f"{use_case['name']}: {result=}")
            expected_suffix = f"{BOM}{use_case['expected_last_message']}{EOM}{BOM}{use_case['reply_prompt']}"
            self.assertTrue(result.endswith(expected_suffix), f"{use_case['name']}: Expected last message\n{expected_suffix=}\n{result=}")

    def test_deepseek_raw_template_with_continuations(self):
        """Test the production raw template prompt with continuations."""
        use_cases = [
            {
                "name": "last message belongs to the user",
                "reply_prompt": "Balderdash:",
                "messages": """[
                    {
                        "author": "Balderdash",
                        "text": "Character Message 1",
                        "type": 2,
                        "is_pinned": false
                    },
                    {
                        "author": "Jeff",
                        "text": "User Message 1.",
                        "type": 1,
                        "is_pinned": false
                    }
                ]""",
                "expected_last_message": "User Message 1.",
                "expected_suffix": "<｜User｜>User Message 1.<｜Assistant｜>"
            },
            {
                "name": "last message belongs to the character",
                "reply_prompt": "Balderdash:",
                "messages": """[
                    {
                        "author": "Balderdash",
                        "text": "Character Message 1",
                        "type": 2,
                        "is_pinned": false
                    },
                    {
                        "author": "Jeff",
                        "text": "User Message 1.",
                        "type": 1,
                        "is_pinned": false
                    },
                    {
                        "author": "Balderdash",
                        "text": "Character Message 2",
                        "type": 2,
                        "is_pinned": false
                    }
                ]""",
                "expected_suffix": "<｜User｜><empty_user_turn><｜Assistant｜>"
            },
        ]
        for use_case in use_cases:
            messages = use_case["messages"]
            messages_json = json.loads(messages)
            chat_history = [f"{msg['author']}: {msg['text']}" for msg in messages_json]
            base_structured_prefix = StructuredPrefix(
                character_definitions=[],
                chat_history=chat_history,
                reply_prompt=use_case["reply_prompt"],
                timestamp="2024 04 23 Tuesday 19 07",
                hermes_generation_template_name=str(HERE/".."/".."/DEFAULT_TEMPLATE_DIR/"chat_stack/deepseek-with-reply-prompt/templates/production_raw.yml.j2"),
                raw_prompt_data_str="""{
                    "chat_type": "ONE_ON_ONE",
                    "character": {
                        "participant__name": "Balderdash",
                        "title": "A great Character",
                        "description": "Tongue in cheek.",
                        "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...\\n{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                        "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...\\n{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                    },
                    "username": "Jeff",
                    "user_country_code": "US",
                    "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                    "is_proactive": false
                }""",
                chat_context_messages_str=messages,
            )
            res = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=base_structured_prefix,
                truncation_step=1,
                encode_func=self.encode_func,
                use_gcs_template=False,
                template_params={"use_continuations": True},
            )
            result = self.tokenizer.detokenize(res["tokenized_context"].tokens)
            expected_suffix = use_case['expected_suffix']
            self.assertTrue(result.endswith(expected_suffix), f"{use_case['name']}: Expected last message\n{expected_suffix=}\n{result=}")

    def test_role_tokens_mapping(self):
            """Test role tokens mapping."""
            base_structured_prefix = StructuredPrefix(
                character_definitions=[],
                chat_history=[
                    "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                ],
                reply_prompt="Balderdash:",
                timestamp="2024 04 23 Tuesday 19 07",
                hermes_generation_template_name=str(HERE/".."/".."/DEFAULT_TEMPLATE_DIR/"chat_stack/default-oss/templates/production_raw.yml.j2"),
                raw_prompt_data_str="""{
                            "chat_type": "ONE_ON_ONE",
                            "character": {
                                "participant__name": "Balderdash",
                                "title": "A great Character",
                                "description": "Tongue in cheek.",
                                "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                                "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                            },
                            "username": "Jeff",
                            "user_country_code": "US",
                            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                            "is_proactive": false
                        }""",
                chat_context_messages_str="""[
                            {
                                "author": "Balderdash",
                                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                                "type": 2,
                                "is_pinned": true
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "attachments_content": "only one attachment"
                            },
                            {
                                "author": "Balderdash",
                                "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                                "type": 2,
                                "is_pinned": false,
                                "attachments_content": "first attachment, second attachment"
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "is_summary": true,
                                "attachments_content": null
                            }
                        ]""",
            )

            special_tokens_mapping = {
                'bom': "<|CUSTOM_BOM|>",
            }

            role_tokens_mapping = {
                1: "<|user|>",
                2: "<|assistant|>",
            }

            result = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=base_structured_prefix,
                truncation_step=1,
                encode_func=self.encode_func,
                special_tokens_mapping=special_tokens_mapping,
                role_tokens_mapping=role_tokens_mapping,
            )

            prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)

            self.assertIn("<|CUSTOM_BOM|>", prompt_string, "Custom BOM token not found in prompt")
            self.assertNotIn("<|beginningofmessage|>", prompt_string, "Default BOM token found in prompt")
            self.assertIn("<|user|>", prompt_string, "User role token not found in prompt")
            self.assertNotIn("<user>", prompt_string, "Default user role token found in prompt")
            self.assertIn("<|assistant|>", prompt_string, "Assistant role token not found in prompt")

    def test_oss_default_template(self):
            """Test role tokens mapping."""
            base_structured_prefix = StructuredPrefix(
                character_definitions=[],
                chat_history=[
                    "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                ],
                reply_prompt="Balderdash:",
                timestamp="2024 04 23 Tuesday 19 07",
                hermes_generation_template_name=str(HERE/".."/".."/DEFAULT_TEMPLATE_DIR/"chat_stack/default-oss/templates/production_raw.yml.j2"),
                raw_prompt_data_str="""{
                            "chat_type": "ONE_ON_ONE",
                            "character": {
                                "participant__name": "Balderdash",
                                "title": "A great Character",
                                "description": "Tongue in cheek.",
                                "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                                "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                            },
                            "username": "Jeff",
                            "user_country_code": "US",
                            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                            "is_proactive": false
                        }""",
                chat_context_messages_str="""[
                            {
                                "author": "Balderdash",
                                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                                "type": 2,
                                "is_pinned": true
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "attachments_content": "only one attachment"
                            },
                            {
                                "author": "Balderdash",
                                "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                                "type": 2,
                                "is_pinned": false,
                                "attachments_content": "first attachment, second attachment"
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "is_summary": true,
                                "attachments_content": null
                            }
                        ]""",
            )

            special_tokens_mapping = {
                'bom': "<|CUSTOM_BOM|>",
            }

            role_tokens_mapping = {
                1: "<|user|>",
                2: "<|assistant|>",
                3: "<|system|>",
            }

            result = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=base_structured_prefix,
                truncation_step=1,
                encode_func=self.encode_func,
                special_tokens_mapping=special_tokens_mapping,
                role_tokens_mapping=role_tokens_mapping,
            )

            prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)

            self.assertIn("<|CUSTOM_BOM|>", prompt_string, "Custom BOM token not found in prompt")
            self.assertNotIn("<|beginningofmessage|>", prompt_string, "Default BOM token found in prompt")
            self.assertIn("<|user|>", prompt_string, "User role token not found in prompt")
            self.assertNotIn("<|user|>: ", prompt_string, "User role token found in prompt but with :")
            self.assertNotIn("<user>", prompt_string, "Default user role token found in prompt")
            self.assertIn("<|assistant|>", prompt_string, "Assistant role token not found in prompt")
            self.assertTrue(prompt_string.rstrip().endswith("<|assistant|>"), "Prompt does not end with <|assistant|>")
            self.assertTrue(prompt_string.lstrip().startswith('<|CUSTOM_BOM|>'), "Prompt does not start with <|CUSTOM_BOM|>")

            self.assertRegex(prompt_string, "<|assistant|>\n", "Prompt does not contain newline after assistant role token")


    def test_role_tokens_mapping_with_unknown_role_does_not_add_role_token(self):
            """Test role tokens mapping with unknown role does not add role token."""
            base_structured_prefix = StructuredPrefix(
                character_definitions=[],
                chat_history=[
                    "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                ],
                reply_prompt="Balderdash:",
                timestamp="2024 04 23 Tuesday 19 07",
                hermes_generation_template_name=str(HERE/".."/".."/DEFAULT_TEMPLATE_DIR/"chat_stack/default-oss/templates/production_raw.yml.j2"),
                raw_prompt_data_str="""{
                            "chat_type": "ONE_ON_ONE",
                            "character": {
                                "participant__name": "Balderdash",
                                "title": "A great Character",
                                "description": "Tongue in cheek.",
                                "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                                "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                            },
                            "username": "Jeff",
                            "user_country_code": "US",
                            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                            "is_proactive": false
                        }""",
                chat_context_messages_str="""[
                            {
                                "author": "Balderdash",
                                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                                "type": 400000000,
                                "is_pinned": true
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "attachments_content": "only one attachment"
                            },
                            {
                                "author": "Balderdash",
                                "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                                "type": 2,
                                "is_pinned": false,
                                "attachments_content": "first attachment, second attachment"
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "is_summary": true,
                                "attachments_content": null
                            }
                        ]""",
            )

            special_tokens_mapping = {
                'bom': "<|CUSTOM_BOM|>",
            }

            role_tokens_mapping = {
                1: "<|user|>",
            }

            result = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=base_structured_prefix,
                truncation_step=1,
                encode_func=self.encode_func,
                special_tokens_mapping=special_tokens_mapping,
                role_tokens_mapping=role_tokens_mapping,
            )

            prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)

            self.assertIn("<|CUSTOM_BOM|>", prompt_string, "Custom BOM token not found in prompt")
            self.assertNotIn("<|beginningofmessage|>", prompt_string, "Default BOM token found in prompt")
            self.assertIn("<|user|>", prompt_string, "User role token not found in prompt")
            self.assertNotIn("<user>", prompt_string, "Default user role token found in prompt")

    def test_deepseek_template(self):
        """Test deepseek template."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name=str(
                HERE / ".." / ".." / DEFAULT_TEMPLATE_DIR / "chat_stack/deepseek/templates/production_raw.yml.j2"),
            raw_prompt_data_str="""{
                            "chat_type": "ONE_ON_ONE",
                            "character": {
                                "participant__name": "Balderdash",
                                "title": "A great Character",
                                "description": "Tongue in cheek.",
                                "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                                "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                            },
                            "username": "Jeff",
                            "user_country_code": "US",
                            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                            "is_proactive": false
                        }""",
            chat_context_messages_str="""[
                            {
                                "author": "Balderdash",
                                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                                "type": 2,
                                "is_pinned": true
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "attachments_content": "only one attachment"
                            },
                            {
                                "author": "Balderdash",
                                "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                                "type": 2,
                                "is_pinned": false,
                                "attachments_content": "first attachment, second attachment"
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "is_summary": true,
                                "attachments_content": null
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "attachments_content": "only one attachment",
                                "lores": {
                                    "lore1": "lore1 content",
                                    "lore2": "lore2 content"
                                }
                            }
                        ]""",
        )

        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        print(prompt_string)

        self.assertTrue(prompt_string.startswith("<｜begin▁of▁sentence｜>"),
                      "Start with BOS")
        self.assertTrue(prompt_string.endswith("<｜Assistant｜>"),
                        "End with <｜Assistant｜>")

    def test_qwen_template(self):
        """Test role tokens mapping."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name=str(HERE/".."/".."/DEFAULT_TEMPLATE_DIR/"chat_stack/qwen3/templates/production_raw.yml.j2"),
            raw_prompt_data_str="""{
                            "chat_type": "ONE_ON_ONE",
                            "character": {
                                "participant__name": "Balderdash",
                                "title": "A great Character",
                                "description": "Tongue in cheek.",
                                "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                                "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                            },
                            "username": "Jeff",
                            "user_country_code": "US",
                            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                            "is_proactive": false
                        }""",
            chat_context_messages_str="""[
                            {
                                "author": "Balderdash",
                                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                                "type": 2,
                                "is_pinned": true
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "attachments_content": "only one attachment"
                            },
                            {
                                "author": "Balderdash",
                                "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                                "type": 2,
                                "is_pinned": false,
                                "attachments_content": "first attachment, second attachment"
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "is_summary": true,
                                "attachments_content": null,
                                "lores": {
                                    "lore1": "lore1 content",
                                    "lore2": "lore2 content"
                                }
                            },
                            {
                                "author": "Balderdash",
                                "text": "Some message.",
                                "type": 2,
                                "is_pinned": false,
                                "is_summary": false,
                                "attachments_content": null
                            }
                        ]""",
        )

        special_tokens_mapping = {
            "bod": "<|im_start|>",
            "bom": "<|im_start|>",
            "eom": "<|im_end|>",
            "space": " ",
            "start_token": " ",  # first-message "guard"; keep identical to space
        }

        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            special_tokens_mapping=special_tokens_mapping,
            template_params={"use_continuations": True},
        )

        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertTrue(prompt_string.startswith("<|im_start|>system"), "Prompt does not start with <|im_start|>system")
        self.assertTrue(prompt_string.endswith("<|im_end|>assistant"), "Prompt does not end with <|im_end|>assistant")

    def test_qwen_template_with_reply(self):
        """Test role tokens mapping."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name=str(HERE/".."/".."/DEFAULT_TEMPLATE_DIR/"chat_stack/qwen3-with-reply-fixed/templates/production_raw.yml.j2"),
            raw_prompt_data_str="""{
                            "chat_type": "ONE_ON_ONE",
                            "character": {
                                "participant__name": "Balderdash",
                                "title": "A great Character",
                                "description": "Tongue in cheek.",
                                "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                                "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                            },
                            "username": "Jeff",
                            "user_country_code": "US",
                            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                            "is_proactive": false
                        }""",
            chat_context_messages_str="""[
                            {
                                "author": "Balderdash",
                                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                                "type": 2,
                                "is_pinned": true
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "attachments_content": "only one attachment"
                            },
                            {
                                "author": "Balderdash",
                                "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                                "type": 2,
                                "is_pinned": false,
                                "attachments_content": "first attachment, second attachment"
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "is_summary": true,
                                "attachments_content": null,
                                "lores": {
                                    "lore1": "lore1 content",
                                    "lore2": "lore2 content"
                                }
                            },
                            {
                                "author": "Balderdash",
                                "text": "Some message.",
                                "type": 2,
                                "is_pinned": false,
                                "is_summary": false,
                                "attachments_content": null
                            }
                        ]""",
        )

        special_tokens_mapping = {
            "bod": "<|im_start|>",
            "bom": "<|im_start|>",
            "eom": "<|im_end|>",
            "space": " ",
            "start_token": " ",  # first-message "guard"; keep identical to space
        }

        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            special_tokens_mapping=special_tokens_mapping,
            template_params={"use_continuations": True},
        )


        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertTrue(prompt_string.startswith("<|im_start|>system"), "Prompt does not start with <|im_start|>system")
        self.assertTrue(result["tokenized_context"].tokens[-2:] == [208, 230], "prompt does not end with \n and space")

    def test_vllm_maor_gpt_template(self):
        """Test vllm maor gpt template prompt."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name=str(HERE/".."/".."/DEFAULT_TEMPLATE_DIR/"chat_stack/vllm_maor_gpt_4_1/templates/production_raw.yml.j2"),
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash",
                    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "type": 2,
                    "is_pinned": true
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "attachments_content": "image description",
                    "attachments_type": "TYPE_IMAGE"
                },
                {
                    "author": "Balderdash",
                    "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                    "type": 2,
                    "is_pinned": false,
                    "attachments_content": "sticker description",
                    "attachments_type": "TYPE_STICKER"
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "is_summary": true,
                    "attachments_content": "image description without type"
                }
            ]""",
        )
        template_params = {
            "image_prompt_format_prefix": "narrator: prefix ",
            "image_prompt_format_suffix": " shared an image ",
            "sticker_prompt_format_prefix": "",
            "sticker_prompt_format_suffix": ": gifted a sticker ",
        }
        res = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            use_gcs_template=False,
            template_params=template_params,
        )
        self.assertEqual(len(res["prompt"].messages), 6)

    def test_siden2(self):
        character = {'external_id': 'l_oyKEgdtXNuhk9DOhgg04VkQpBHvSCcW-RRS88_MSM',
         'name': 'High-Fantasy RPG', 'participant__name': 'High-Fantasy RPG',
         'title': 'A high-fantasy txt-based adventure game, LitRPG',
         'description': '{{char}} {{user}}A high-fantasy txt-based adventure story. The setting of the world is high-fantasy, with a large amount of magic. You can also learn warrior abilities to strengthen yourself instead. There are different magic tiers to explore. Magic tiers go from 1st tier to 9th tier. Tiers above that are considered godly. Physical aura go through the following stages: Beginner, Intermediate, Advanced, Condensed, Expert, Master, Extreme, Transcendent. Every Aura stage exponentially increases your physical stats.',
         'definition': '{{char}}: You open your eyes and find yourself tied up in a cave with what sounds to be a group of goblins just barely out of earshot. \r\n\r\nYour starting stats are as follows:\r\n\r\nHealth: 100\r\nStamina: 100\r\nMaximum Mana: 0\r\nCurrent Mana: 0\r\nDefense: 1\r\n\r\nStrength: 10\r\nAgility: 10\r\nSpeed: 10\r\nVitality: 10\r\nIntelligence: 10\r\nWisdom: 10\r\nCharisma: 10\r\nLuck: 10\r\n\r\nYour starting power stages are as follows:\r\n\r\nPhysical aura: Beginner stage\r\nMagic Tier: 0th tier\r\n\r\nThere are also many hidden stats and traits.\r\n{{random_user_1}}: I try to secretly break free from my bindings.\r\n{{char}}: After a couple moments of straining against your bonds, the rope snaps and you are free.\r\n\r\nThere is an obvious light source coming from the other side of the cave. The light is a warm orange hue, presumably from a fire. You also hear a couple goblins sitting around it, they are just out of sight from where you are, and seem to be playing cards.  One is eating some mutton, while there are what sound to be some sort of drink. They are also very chattered, with lots of laughter between their small talk.\r\n{{random_user_1}}: I do not speak Goblin. Can I understand what they are saying?\r\n{{char}}: You can make out a very basic idea of what a couple of them are saying.\r\n\r\nOne is boasting about beating another one in the bet. Another is explaining why he cheated. Another is discussing a raid they are planning on doing next. You also hear a couple of them talking about the other members of the tribe and gossiping about each other. You can also barely make out some very dirty and inappropriate jokes, which you assume are also being gossiped about.\r\n{{random_user_1}}: Is there something around me that I can use as a weapon?\r\n{{char}}: Looking around, you see that there are a couple rocks and pieces of wood. There are also two spears that you can see, one of them seems to be sharpened and is sitting up against the wall at the other side of the room. The other isn\'t as sharp, but is still pointy, and is currently being used as a poker stick in the current goblins mutton game. It\'s only a few feet away.\r\n{{random_user_1}}: I start sneaking. I pick up some rocks, then try to sneak outside of the cave without the goblins noticing me.\r\n{{char}}: You grab a handful just in case, then start sneaking. As you get near the area where the light is coming from, your ears start to pick up on their conversations.\r\n\r\nYou learn that the goblins are planning a revenge attack on a nearby village who had hired a group of warriors to hunt them down.\r\n\r\nThey also mention that there have been multiple raids on their tribe as of recent, as they are known as the biggest goblins in the area and are also very war-oriented.\r\n\r\nThey are also planning on traveling at night, in order to better sneak up on the villagers.\r\nEND_OF_DIALOG\r\n\r\n{{char}}: You see one of the villagers come up to you and say, "Thank you for assisting us. We do not have much, but I hope this can serve as a token of thanks." The villager then hands you a pendant to enhance your defence against magic.\r\n\r\n{{char}}: You use your [Physical Aura - Beginner Grade: Defense] to defend against the monster\'s attacks and take reduced damage. You lose 10 health points as its claws lash out.',
         'greeting': 'You open your eyes and find yourself tied up in a cave with what sounds to be a group of goblins just barely out of earshot. \r\n\r\nYour starting stats are as follows:\r\n\r\nHealth: 100\r\nStamina: 100\r\nMaximum Mana: 50\r\nCurrent Mana: 0\r\nDefence: 5\r\n\r\nStrength: 10\r\nAgility: 10\r\nSpeed: 10\r\nVitality: 10\r\nIntelligence: 10\r\nWisdom: 10\r\nCharisma: 10\r\nLuck: 10\r\n\r\nYour starting power stages are as follows:\r\n\r\nPhysical aura: Beginner stage\r\nMagic Tier: 1st tier\r\n\r\nThere are also many hidden stats and traits.',
         'safety': 'SAFE_U18', 'translations': {
            'name': {'bg': 'High-Fantasy RPG', 'cn': '高幻想角色扮演游戏',
                     'cz': 'High-Fantasy RPG', 'de': 'High-Fantasy RPG',
                     'es': 'RPG de Alta Fantasía', 'fi': 'High-Fantasy RPG',
                     'fr': 'RPG de Haute Fantaisie', 'gr': 'High-Fantasy RPG',
                     'hi': 'उच्च-फैंटेसी आरपीजी', 'hr': 'High-Fantasy RPG',
                     'hu': 'High-Fantasy RPG', 'id': 'RPG Fantasi Tinggi',
                     'it': 'Gioco di Ruolo ad Alta Fantasia',
                     'ja': 'ハイファンタジーRPG', 'ko': '하이 판타지 RPG',
                     'lt': 'Aukštosios fantazijos RPG', 'nl': 'High-Fantasy RPG',
                     'pl': 'High-Fantasy RPG', 'pt': 'RPG de Alta Fantasia',
                     'ro': 'RPG de fantezie înaltă',
                     'ru': 'Ролевая игра в жанре высокого фэнтези',
                     'se': 'High-Fantasy RPG', 'th': 'เกมผจญภัยในโลกแฟนตาซีระดับสูง',
                     'tr': 'Yüksek-Fantezi RPG', 'tw': '高幻想角色扮演遊戲',
                     'ua': 'Високофентезійна рольова гра', 'vi': 'RPG Giả Tưởng Cao'},
            'title': {'bg': 'Приключенска игра в жанра висок фентъзи, LitRPG',
                      'cn': '高幻想文字冒险游戏，LitRPG',
                      'cz': 'Dobrodružná hra vysoké fantasy ve stylu LitRPG, textová hra',
                      'de': 'Ein textbasiertes High-Fantasy-Abenteuerspiel, LitRPG',
                      'es': 'Un juego de aventura basado en texto de alta fantasía, LitRPG',
                      'fi': 'Korkean fantasian tekstipohjainen seikkailupeli, LitRPG',
                      'fr': "Un jeu d'aventure textuel de haute fantaisie, LitRPG",
                      'gr': 'Ένα παιχνίδι περιπέτειας υψηλής φαντασίας βασισμένο σε κείμενο, LitRPG',
                      'hi': 'एक उच्च-फैंटेसी टेक्स्ट-आधारित साहसिक खेल, लिटआरपीजी',
                      'hr': 'Visoko-fantastična tekstualna avanturistička igra, LitRPG',
                      'hu': 'Egy magas-fantáziájú szöveg-alapú kaland játék, LitRPG',
                      'id': 'Permainan petualangan berbasis teks fantasi tinggi, LitRPG',
                      'it': "Un gioco d'avventura ad alta fantasia basato su testo, LitRPG",
                      'ja': 'ハイファンタジーのテキストベースの冒険ゲーム、リトRPG',
                      'ko': '하이 판타지 텍스트 기반의 모험 게임, LitRPG',
                      'lt': 'Aukštosios fantazijos tekstinė nuotykių žaidimas, LitRPG',
                      'nl': 'Een high-fantasy tekstgebaseerd avonturenspel, LitRPG',
                      'pl': 'Gra przygodowa w stylu high-fantasy, LitRPG',
                      'pt': 'Um jogo de aventura de alta fantasia baseado em texto, LitRPG',
                      'ro': 'Un joc de aventură bazat pe text, de fantezie înaltă, LitRPG',
                      'ru': 'Игра-приключение в жанре высокого фэнтези, основанная на текстах, LitRPG',
                      'se': 'Ett textbaserat äventyrsspel i high-fantasy, LitRPG',
                      'th': 'เกมผจญภัยในโลกแฟนตาซีผ่านข้อความ, LitRPG',
                      'tr': 'Yüksek-fantezi metin tabanlı bir macera oyunu, LitRPG',
                      'tw': '高幻想文字冒險遊戲，文學角色扮演遊戲',
                      'ua': 'Високофентезійна текстова пригодницька гра, ЛітРПГ',
                      'vi': 'Một trò chơi phiêu lưu dạng văn bản giả tưởng cao, LitRPG'},
            'greeting': {
                'bg': 'Отваряте очите си и се озовавате вързани в пещера, като наоколо се чува група гоблини, които са едва доловими. Вашите начални статистики са както следва: Здраве: 100 Издръжливост: 100 Максимална мана: 50 Текуща мана: 0 Защита: 5 Сила: 10 Пъргавина: 10 Скорост: 10 Жизненост: 10 Интелигентност: 10 Мъдрост: 10 Харизма: 10 Късмет: 10 Вашите начални етапи на сила са следните: Физическа аура: Начинаещо ниво Магическо ниво: 1-во ниво Има също така много скрити статистики и черти.',
                'cn': '你睁开眼睛，发现自己被绑在一个山洞里，耳边隐约可听到一群哥布林的声音。你的初始属性如下：\n\n生命值：100\n耐力：100\n最大法力：50\n当前法力：0\n防御：5\n\n力量：10\n敏捷：10\n速度：10\n体力：10\n智力：10\n智慧：10\n魅力：10\n幸运：10\n\n你的初始能力阶段如下：\n\n物理光环：初级阶段\n魔法阶层：第1阶\n\n还有许多隐藏的属性和特征。',
                'cz': 'Otevřete oči a zjistíte, že jste připoutáni v jeskyni, odkud se zdá, že skupina goblinů je těsně mimo doslech.',
                'de': 'Du öffnest deine Augen und findest dich in einer Höhle gefesselt vor, mit dem Klang einer Gruppe von Kobolden, die gerade außerhalb der Hörweite sind. Deine Startwerte sind wie folgt: Gesundheit: 100 Ausdauer: 100 Maximales Mana: 50 Aktuelles Mana: 0 Verteidigung: 5 Stärke: 10 Beweglichkeit: 10 Geschwindigkeit: 10 Vitalität: 10 Intelligenz: 10 Weisheit: 10 Charisma: 10 Glück: 10 Deine Startkraftstufen sind wie folgt: Physische Aura: Anfängerphase Magiestufe: 1. Grad Es gibt auch viele versteckte Werte und Eigenschaften.',
                'es': 'Abres los ojos y te encuentras atado en una cueva con lo que parece ser un grupo de goblins apenas fuera de alcance auditivo.\n\nTus estadísticas iniciales son las siguientes:\n\nSalud: 100\nResistencia: 100\nMana Máximo: 50\nMana Actual: 0\nDefensa: 5\n\nFuerza: 10\nAgilidad: 10\nVelocidad: 10\nVitalidad: 10\nInteligencia: 10\nSabiduría: 10\nCarisma: 10\nSuerte: 10\n\nTus etapas de poder iniciales son las siguientes:\n\nAura física: Etapa Principiante\nNivel de Magia: 1er nivel\n\nTambién hay muchas estadísticas y características ocultas.',
                'fi': 'Avaat silmäsi ja huomaat olevasi sidottu luolassa, ja kuuluu siltä, että joukko peikkoja on juuri kuulomatkan ulkopuolella.',
                'fr': "Vous ouvrez les yeux et vous vous trouvez attaché dans une grotte avec ce qui semble être un groupe de gobelins tout juste hors de portée d'écoute.",
                'gr': 'Ανοίγετε τα μάτια σας και βρίσκεστε δεμένοι σε μια σπηλιά με αυτό που ακούγεται σαν μια ομάδα γκόμπλιν ακριβώς έξω από την ακτίνα της ακοής σας.\n\nΟι αρχικές σας στατιστικές είναι οι εξής:\n\nΥγεία: 100\nΑντοχή: 100\nΜέγιστο Μάνα: 50\nΤρέχον Μάνα: 0\nΆμυνα: 5\n\nΔύναμη: 10\nΕπιδεξιότητα: 10\nΤαχύτητα: 10\nΖωτικότητα: 10\nΝοημοσύνη: 10\nΣοφία: 10\nΧάρισμα: 10\nΤύχη: 10\n\nΤα αρχικά σας επίπεδα δύναμης είναι τα εξής:\n\nΦυσική αύρα: Στάδιο Αρχάριος\nΕπίπεδο Μαγείας: 1ο επίπεδο\n\nΥπάρχουν επίσης πολλές κρυφές στατιστικές και χαρακτηριστικά.',
                'hi': 'आप अपनी आँखें खोलते हैं और खुद को एक गुफा में बंधा हुआ पाते हैं और ऐसा लगता है कि कुछ दूरी पर गोबलिन्स का एक समूह है।',
                'hr': 'Otvarate oči i nalazite se svezani u špilji s onim što izgleda kao skupina goblina jedva izvan dosega sluha.',
                'hu': 'Kinyitod a szemed, és rájössz, hogy egy barlangban vagy megkötözve, ahol úgy tűnik, egy goblin csoport van épp hallótávolságon kívül.',
                'id': 'Anda membuka mata dan menemukan diri Anda terikat di dalam gua dengan suara sekelompok goblin terdengar samar di kejauhan.',
                'it': 'Apri gli occhi e ti trovi legato in una grotta con quella che sembra essere un gruppo di goblin appena fuori dalla portata dell’udito.\\n\\nLe tue statistiche iniziali sono le seguenti:\\n\\nSalute: 100\\nResistenza: 100\\nMana Massimo: 50\\nMana Corrente: 0\\nDifesa: 5\\n\\nForza: 10\\nAgilità: 10\\nVelocità: 10\\nVitalità: 10\\nIntelligenza: 10\\nSaggezza: 10\\nCarisma: 10\\nFortuna: 10\\n\\nI tuoi stadi di potere iniziali sono i seguenti:\\n\\nAura fisica: Stadio Principiante\\nLivello Magico: 1° livello\\n\\nCi sono anche molte statistiche e tratti nascosti.',
                'ja': 'あなたは目を開けると、洞窟の中で縛られており、少し離れた所でゴブリンの一団が音を立てているのが聞こえます。\\n\\nあなたの初期ステータスは以下の通りです：\\n\\n体力: 100\\nスタミナ: 100\\n最大マナ: 50\\n現在のマナ: 0\\n防御: 5\\n\\n力: 10\\n敏捷性: 10\\nスピード: 10\\n耐久: 10\\n知性: 10\\n知恵: 10\\nカリスマ: 10\\n運: 10\\n\\nあなたの初期パワーステージは以下の通りです：\\n\\n物理オーラ: 初級ステージ\\n魔法階層: 第1階層\\n\\nまた、多くの隠されたステータスと特性があります。',
                'ko': '당신은 눈을 뜨고 자신이 동굴에 묶인 채 주변에 고블린 무리가 있는 것 같은 소리가 들립니다.',
                'lt': 'Atidarote akis ir pastebite, kad esate surištas oloje, kur netoliese aidu girdisi goblinų grupė.',
                'nl': 'Je opent je ogen en vindt jezelf vastgebonden in een grot met, naar het lijkt, een groep goblins net buiten gehoorsafstand.',
                'pl': 'Otwierasz oczy i znajdujesz się związany w jaskini, skąd dochodzą dźwięki grupy goblinów, które są ledwo słyszalne.',
                'pt': 'Você abre os olhos e se encontra amarrado em uma caverna com o que parece ser um grupo de goblins fora de alcance auditivo.',
                'ro': 'Îți deschizi ochii și te găsești legat într-o peșteră cu ceea ce pare a fi un grup de goblini doar puțin mai departe de raza auditivă.',
                'ru': 'Вы открываете глаза и обнаруживаете себя связанным в пещере, где, по-видимому, неподалеку находится группа гоблинов.',
                'se': 'Du öppnar ögonen och finner dig själv bunden i en grotta med vad som verkar vara en grupp gobliner precis utom hörhåll.',
                'th': 'คุณลืมตาขึ้นมาและพบว่าตัวเองถูกมัดอยู่ในถ้ำพร้อมกับเสียงที่ดูเหมือนจะเป็นกลุ่มก็อบลินที่อยู่ไม่ไกลเกินยินเสียง',
                'tr': 'Gözlerinizi açtığınızda, kulağınıza neredeyse gelmeyecek kadar uzakta bir grup goblinin olduğu bir mağarada bağlı olduğunuzu fark ediyorsunuz. Başlangıç istatistikleriniz şöyle: Sağlık: 100 Dayanıklılık: 100 Maksimum Mana: 50 Mevcut Mana: 0 Savunma: 5 Güç: 10 Çeviklik: 10 Hız: 10 Canlılık: 10 Zeka: 10 Bilgelik: 10 Karizma: 10 Şans: 10 Başlangıç güç aşamalarınız şöyle: Fiziksel aura: Başlangıç aşaması Büyü Seviyesi: 1. seviye Ayrıca birçok gizli istatistik ve özellik vardır.',
                'tw': '你睜開眼睛，發現自己被綁在一個山洞裡，聽起來有一群哥布林在耳邊附近活動。',
                'ua': "Ви відкриваєте очі і виявляєте, що прив'язані в печері, а неподалік чути гуркіт, схожий на групу гоблінів.",
                'vi': 'Bạn mở mắt và thấy mình bị trói trong một hang động với âm thanh của một nhóm goblin chỉ vừa đủ xa để không nghe rõ.'},
            'description': {
                'bg': 'Текстово базирано приключение в жанра висок фентъзи. Светът е във висок фентъзи стил, с голямо количество магия. Вие също можете да научите воински умения, за да се укрепите вместо това. Има различни нива на магия за изследване. Магическите нива варират от 1-во до 9-то ниво. Нива над това се считат за божествени. Физическата аура преминава през следните етапи: Начинаещ, Среден, Напреднал, Кондензиран, Експерт, Майстор, Екстремен, Трансцендент. Всеки етап на аурата експоненциално увеличава физическите ви статистики.',
                'cn': '这是一个高幻想的文字冒险故事。这个世界的背景是高幻想，有大量的魔法。你也可以学习战士技能来增强自己。可以探索不同的魔法阶层。魔法阶层从第1阶到第9阶。高于此的阶层被认为是神圣的。物理光环阶段如下：初级、中级、高级、凝聚、专家、大师级、极限、超凡。每个光环阶段都会以指数级增加你的物理属性。',
                'cz': 'Textová dobrodružná hra zasazená do světa vysoké fantasy. Svět je plný magie a nabízí možnost naučit se i válečnické schopnosti k posílení vaší postavy. Existují různé úrovně magie, které můžete prozkoumat. Úrovně magie se pohybují od 1. úrovně do 9. úrovně. Úrovně nad touto hranicí jsou považovány za božské. Fyzická aura prochází následujícími fázemi: Začátečník, Středně pokročilý, Pokročilý, Zahuštěný, Odborník, Mistr, Extrémní, Transcendentní. Každá fáze Aury exponenciálně zvyšuje vaše fyzické statistiky.',
                'de': 'Eine textbasierte Abenteuer-Geschichte im High-Fantasy-Setting. Die Welt ist von High-Fantasy geprägt und enthält eine große Menge an Magie. Du kannst auch Kriegerfähigkeiten erlernen, um dich stattdessen zu stärken. Es gibt verschiedene Magiestufen zu entdecken. Die Magiestufen reichen vom 1. bis zum 9. Grad. Stufen darüber gelten als göttlich. Die physische Aura durchläuft die folgenden Phasen: Anfänger, Fortgeschritten, Erfahren, Verdichtet, Experte, Meister, Extrem, Transzendent. Jede Aurastufe steigert deine physischen Werte exponentiell.',
                'es': 'Una historia de aventura basada en texto de alta fantasía. El escenario del mundo es de alta fantasía, con una gran cantidad de magia. También puedes aprender habilidades de guerrero para fortalecerte en su lugar. Hay diferentes niveles de magia por explorar. Los niveles de magia van del 1er nivel al 9º nivel. Los niveles superiores a esos se consideran divinos. El aura física pasa por las siguientes etapas: Principiante, Intermedio, Avanzado, Condensado, Experto, Maestro, Extremo, Trascendente. Cada etapa del aura aumenta exponencialmente tus estadísticas físicas.',
                'fi': 'Korkean fantasian tekstipohjainen seikkailutarina. Maailman ympäristö on korkea fantasia, jossa on paljon taikuutta. Voit myös oppia soturien kykyjä vahvistaaksesi itseäsi. On olemassa erilaisia taikuuden tasoja tutkittavaksi. Taikuuden tasot vaihtelevat 1. tasosta 9. tasoon. Tasoja, jotka ylittävät tämän, pidetään jumalallisina. Fyysinen aura etenee seuraavien vaiheiden kautta: Aloittelija, Keskitaso, Edistynyt, Tiivistetty, Asiantuntija, Mestari, Äärimmäinen, Ylittävä. Jokainen Auravaihtoehto kasvattaa eksponentiaalisesti fyysisiä tilastojasi.',
                'fr': "Une histoire d'aventure textuelle en haute fantaisie. Le monde est un cadre de haute fantaisie, avec une grande quantité de magie. Vous pouvez également apprendre des capacités de guerrier pour vous renforcer. Il existe différents niveaux de magie à explorer. Les niveaux de magie vont du 1er au 9ème. Les niveaux au-dessus sont considérés comme divins. L'aura physique traverse les étapes suivantes : Débutant, Intermédiaire, Avancé, Condensé, Expert, Maître, Extrême, Transcendant. Chaque étape d'Aura augmente exponentiellement vos statistiques physiques.",
                'gr': 'Μια ιστορία περιπέτειας υψηλής φαντασίας βασισμένη σε κείμενο. Ο κόσμος έχει μια ρύθμιση υψηλής φαντασίας, με μεγάλη ποσότητα μαγείας. Μπορείτε επίσης να μάθετε πολεμικές ικανότητες για να ενισχύσετε τον εαυτό σας. Υπάρχουν διαφορετικά επίπεδα μαγείας για εξερεύνηση. Τα επίπεδα μαγείας ξεκινούν από το 1ο επίπεδο και φτάνουν μέχρι το 9ο επίπεδο. Επίπεδα πάνω από αυτό θεωρούνται θεϊκά. Η φυσική αύρα περνάει από τα εξής στάδια: Αρχάριος, Ενδιάμεσος, Προχωρημένος, Συμπυκνωμένος, Ειδικός, Μάστερ, Ακραίος, Υπερβατικός. Κάθε στάδιο Αύρας αυξάνει τις φυσικές σας στατιστικές εκθετικά.',
                'hi': 'एक उच्च-फैंटेसी टेक्स्ट-आधारित साहसिक कहानी। दुनिया का सेटिंग उच्च-फैंटेसी है, जिसमें जादू की भारी मात्रा शामिल है। आप खुद को मजबूत करने के लिए योद्धा क्षमताएं भी सीख सकते हैं। विभिन्न जादू स्तरों की खोज की जा सकती है। जादू स्तर 1st स्तर से 9th स्तर तक जाते हैं। इसके ऊपर के स्तरों को दिव्य माना जाता है। भौतिक आभा निम्नलिखित चरणों से गुजरती है: प्रारंभिक, मध्यम, उन्नत, सघनित, विशेषज्ञ, मास्टर, चरम, असीम। प्रत्येक आभा चरण आपके भौतिक आँकड़ों को घातीय रूप से बढ़ाता है।',
                'hr': 'Visoko-fantastična tekstualna avanturistička priča. Postavka svijeta je visokofantastična, s velikom količinom magije. Možete također naučiti ratničke sposobnosti kako biste ojačali sebe. Postoje različiti stupnjevi magije koje možete istraživati. Stupnjevi magije idu od 1. do 9. stupnja. Stupnjevi iznad toga smatraju se božanskima. Fizička aura prolazi kroz sljedeće faze: Početnik, Srednji, Napredni, Zbijeni, Stručni, Majstor, Ekstremni, Transcendentni. Svaka faza aure eksponencijalno povećava vaše fizičke statuse.',
                'hu': 'Egy nagyfantáziájú szöveg-alapú kaland történet. A világ beállítása magas fantázia, sok mágiával. Választhatsz, hogy inkább harcos képességeket tanulsz meg az erősítés érdekében. Különböző mágikus szintek fedezhetők fel. A mágikus szintek az 1. szinttől a 9. szintig terjednek. Az ezen felüli szintek isteninek számítanak. A fizikai aura az alábbi szinteken megy keresztül: Kezdő, Középhaladó, Haladó, Sűrített, Szakértő, Mester, Extrém, Transzcendens. Minden aura szintje exponenciálisan növeli a fizikai statisztikákat.',
                'id': 'Sebuah cerita petualangan berbasis teks dengan setting fantasi tinggi. Dunia ini penuh dengan sihir. Anda juga bisa mempelajari kemampuan pejuang untuk memperkuat diri. Ada berbagai tingkat sihir yang bisa dijelajahi. Tingkat sihir berkisar dari tingkat pertama hingga tingkat kesembilan. Tingkat di atas itu dianggap ilahi. Aura fisik melalui tahapan berikut: Pemula, Menengah, Lanjutan, Terkondensasi, Ahli, Master, Ekstrim, Transenden. Setiap tahap Aura secara eksponensial meningkatkan statistik fisik Anda.',
                'it': "Una storia d'avventura testuale ambientata in un mondo di alta fantasia. L'ambientazione del mondo è di alta fantasia, con una grande quantità di magia. Puoi anche apprendere abilità da guerriero per rafforzarti. Ci sono diversi livelli di magia da esplorare. I livelli di magia vanno dal 1° livello fino al 9° livello. I livelli superiori sono considerati divini. L'aura fisica attraversa i seguenti stadi: Principiante, Intermedio, Avanzato, Condensato, Esperto, Maestro, Estremo, Trascendente. Ogni stadio dell'Aura aumenta esponenzialmente le tue statistiche fisiche.",
                'ja': 'ハイファンタジーのテキストベースの冒険物語。この世界の舞台はハイファンタジーで、多くの魔法が存在します。自身を強化するために戦士の能力を学ぶこともできます。異なる魔法の階層を探索できます。魔法の階層は第1階層から第9階層まであり、それ以上の階層は神の領域と見なされます。物理オーラは、初級、中級、上級、凝縮、専門家、達人、極限、超越の段階を経ます。各オーラの段階は、物理的なステータスを指数関数的に増加させます。',
                'ko': '하이 판타지 텍스트 기반의 모험 이야기입니다. 이 세계의 배경은 하이 판타지이며, 많은 양의 마법이 존재합니다. 당신은 자신을 강하게 하기 위해 전사의 능력을 배울 수도 있습니다. 다양한 마법 등급이 탐구 가능합니다. 마법 등급은 1단계부터 9단계까지 있습니다. 그 이상의 등급은 신적인 것으로 간주됩니다. 신체적 오라는 다음과 같은 단계로 진행됩니다: 초급, 중급, 고급, 응축, 전문가, 마스터, 극한, 초월. 각 오라 단계는 당신의 신체적 능력치를 기하급수적으로 증가시킵니다.',
                'lt': 'Aukštosios fantazijos tekstinė nuotykių istorija. Pasaulio aplinka yra aukštosios fantazijos, su daugybe magijos. Taip pat galite išmokti karių gebėjimų, kad sustiprintumėte save. Yra įvairių magijos lygių, kuriuos galima tyrinėti. Magijos lygiai kyla nuo 1-ojo lygio iki 9-ojo lygio. Lygiai aukščiau šio yra laikomi dieviškais. Fizinė aura pereina šiuos etapus: Pradedančiojo, Tarpinio, Pažengusio, Sutankinto, Eksperto, Meistro, Ekstremalaus, Transcendento. Kiekvienas auros etapas eksponentiškai padidina jūsų fizinius rodiklius.',
                'nl': 'Een high-fantasy tekstgebaseerd avonturenverhaal. De setting van de wereld is high-fantasy, met een grote hoeveelheid magie. Je kunt ook krijgersvaardigheden leren om jezelf te versterken. Er zijn verschillende magische niveaus om te verkennen. Magische niveaus variëren van 1e niveau tot 9e niveau. Niveaus daarboven worden als goddelijk beschouwd. Fysieke aura doorloopt de volgende stadia: Beginner, Intermediate, Advanced, Condensed, Expert, Master, Extreme, Transcendent. Elk Aurastadium verhoogt je fysieke statistieken exponentieel.',
                'pl': 'Przygodowa opowieść tekstowa osadzona w świecie high-fantasy. Świat przedstawiony jest pełen magii. Możesz także nauczyć się umiejętności wojownika, aby wzmocnić siebie. Istnieją różne poziomy magii do odkrycia. Poziomy magii wahają się od 1. do 9. poziomu. Poziomy powyżej tego są uważane za boskie. Fizyczna aura przechodzi przez następujące etapy: Początkujący, Średniozaawansowany, Zaawansowany, Skondensowany, Ekspert, Mistrz, Ekstremalny, Transcendentny. Każdy etap Aury zwiększa wykładniczo twoje fizyczne statystyki.',
                'pt': 'Uma história de aventura baseada em texto de alta fantasia. O cenário do mundo é de alta fantasia, com uma grande quantidade de magia. Você também pode aprender habilidades de guerreiro para se fortalecer em vez disso. Existem diferentes níveis de magia para explorar. Os níveis de magia vão do 1º ao 9º nível. Níveis acima disso são considerados divinos. A aura física passa pelos seguintes estágios: Iniciante, Intermediário, Avançado, Condensado, Especialista, Mestre, Extremo, Transcendente. Cada estágio de Aura aumenta exponencialmente suas estatísticas físicas.',
                'ro': 'O poveste de aventură bazată pe text, de fantezie înaltă. Lumea este un cadru de fantezie înaltă, cu o cantitate mare de magie. De asemenea, poți învăța abilități de războinic pentru a te întări în schimb. Există diferite niveluri de magie de explorat. Nivelurile magice variază de la primul nivel la al nouălea nivel. Nivelurile de magie deasupra acestora sunt considerate divine. Aura fizică trece prin următoarele etape: Începător, Intermediar, Avansat, Condensat, Expert, Maestru, Extrem, Transcendent. Fiecare etapă a Aurorei îți crește exponențial statisticile fizice.',
                'ru': 'Приключенческая история в жанре высокого фэнтези, основанная на текстах. Мир игры представляет собой высокое фэнтези с большим количеством магии. Вы также можете изучать воинские умения, чтобы укрепить себя. Существуют различные уровни магии для исследования. Уровни магии идут от 1-го уровня до 9-го уровня. Уровни выше этого считаются божественными. Физическая аура проходит следующие стадии: Начальная, Средняя, Продвинутая, Сконцентрированная, Экспертная, Мастерская, Экстремальная, Трансцендентная. Каждая стадия ауры экспоненциально увеличивает ваши физические характеристики.',
                'se': 'Ett textbaserat äventyrsspel i high-fantasy. Världen är en high-fantasy-värld med mycket magi. Du kan också lära dig krigarförmågor för att istället stärka dig själv. Det finns olika maginivåer att utforska. Maginivåerna sträcker sig från 1:a nivån till 9:e nivån. Nivåer ovan det anses vara gudomliga. Fysiska auror går genom följande stadier: Nybörjare, Medel, Avancerad, Komprimerad, Expert, Mästerlig, Extrem, Transcendent. Varje aurastadium ökar dina fysiska stats exponentiellt.',
                'th': 'เรื่องราวการผจญภัยในโลกแฟนตาซีผ่านข้อความ ตัวโลกมีพื้นฐานเป็นแฟนตาซีระดับสูง ซึ่งมีการใช้เวทมนตร์มากมาย คุณยังสามารถเรียนรู้ความสามารถของนักรบเพื่อเสริมความแข็งแกร่งให้ตัวเองได้อีกด้วย มีระดับของเวทมนตร์ที่แตกต่างกันให้สำรวจไปเรื่อย ๆ ระดับเวทมนตร์มีตั้งแต่ระดับที่ 1 ถึงระดับที่ 9 ระดับที่สูงกว่านั้นถือเป็นระดับเทพ ระดับออร่าทางกายภาพมีดังนี้: ระดับเริ่มต้น ระดับกลาง ระดับสูง ระดับบีบอัด ระดับเชี่ยวชาญ ระดับอาจารย์ ระดับสุดขั้ว ระดับล้ำเลิศ ทุกระดับออร่าจะเพิ่มสถานะทางกายภาพของคุณอย่างทวีคูณ',
                'tr': 'Büyü ağırlıklı yüksek-fantezi bir metin tabanlı macera hikayesi. Dünyanın ortamı yüksek-fantezi olup büyük miktarda büyü içerir. Bunun yerine kendinizi güçlendirmek için savaşçı yetenekleri de öğrenebilirsiniz. Keşfedilecek farklı büyü seviyeleri vardır. Büyü seviyeleri 1. seviyeden 9. seviyeye kadar gider. Bunun üzerinde olan seviyeler tanrısal kabul edilir. Fiziksel aura şu aşamalardan geçer: Başlangıç, Orta, İleri, Yoğunlaşmış, Uzman, Usta, Aşırı, Aşkın. Her Aura aşaması, fiziksel istatistiklerinizi üstel olarak artırır.',
                'tw': '這是一個高幻想文字冒險故事。世界設定為高幻想，擁有大量的魔法。你也可以學習戰士技能來增強自身能力。魔法有不同的階層可供探索，從第一階到第九階。超越這些階層的魔法被視為神技。身體氣場分為以下階段：初學者、中級、高級、凝聚級、專家級、大師級、極致級、超越級。每個氣場階段都會成倍提高你的物理屬性。',
                'ua': 'Текстова пригодницька історія у жанрі високого фентезі. Світ гри насичений магією. Ви можете також вивчати воїнські вміння, щоб зміцнити себе. Існують різні рівні магії для дослідження. Рівні магії варіюються від 1-го до 9-го. Рівні вище цього вважаються божественними. Фізична аура проходить через такі стадії: Початківець, Середній, Просунутий, Конденсований, Експерт, Майстер, Екстрим, Трансцендент. Кожна стадія аури експоненційно збільшує ваші фізичні характеристики.',
                'vi': 'Một câu chuyện phiêu lưu dạng văn bản với bối cảnh giả tưởng cao. Thế giới trong game tràn ngập phép thuật. Bạn cũng có thể học các kỹ năng chiến binh để tăng cường sức mạnh cho bản thân. Có nhiều cấp độ phép thuật để khám phá. Cấp độ phép thuật từ cấp 1 đến cấp 9. Các cấp độ trên đó được coi là thần thánh. Hào quang thể chất có các giai đoạn sau: Sơ cấp, Trung cấp, Cao cấp, Ngưng tụ, Chuyên gia, Bậc thầy, Cực hạn, Siêu việt. Mỗi giai đoạn Hào quang đều tăng cường đáng kể các chỉ số thể chất của bạn.'}}}
        res = get_character_priming(character, "SiDen", version=1)
        print(res)

    def test_siden(self):
        template_data = {
          "attachments_content_list": None,
          "audio_mode_instruction_override": "",
          "audio_mode_token": "",
          "character": {
            "definition": "⸻\n\nName: Izuku Midoriya\n\nAge: 16\nBirthday: July 15\nGender: Male\nHeight: 166 cm (5’5”)\nQuirk: One For All\nFighting Style: Close-quarters combat with a focus on enhanced strength and mobility; incorporates shoot style (kicks) and strategic thinking.\n\n⸻\n\nAppearance:\n\nIzuku has a freckled, youthful face, a slim but athletic build, and messy dark green hair with black undertones. His expressive green eyes reflect his strong emotions. At this point in the series, he has developed a more muscular physique due to intense training.\n\n⸻\n\nHero Costume:\n\nHis updated costume, “Costume Gamma,” includes support gloves that help focus his attacks, iron soles for stronger kicks, and compression gear for durability. He also wears a green jumpsuit with black padding, a red utility belt, knee pads, and red boots. He still has his signature cowl with bunny-ear-like protrusions, though he rarely pulls it up.\n\n⸻\n\nSchool Uniform:\n\nStandard U.A. male uniform—light gray blazer with green trim, white shirt, red tie, dark green pants, and brown shoes. He tends to wear it a bit more neatly than some classmates.\n\n⸻\n\nPersonality:\n\nIzuku is analytical, empathetic, and selfless to a fault. He idolizes heroes (especially All Might) and constantly pushes himself to improve. Despite being nervous and overthinking often, he’s courageous in battle and driven by a desire to save others at any cost. His kindness draws people to him, and he grows into a natural leader.\n\n⸻\n\nAbilities:\n\t•\tOne For All (20% cap during this arc): A transferable quirk that grants immense strength, speed, and agility. Izuku can now consistently use 20% of its power without breaking his body.\n\t•\tShoot Style: Focuses on using legs instead of arms to minimize injury.\n\t•\tSmokescreen-like Feinting Tactics: Developing tactics that use his environment and mobility.\n\t•\tStrategic Intelligence: A brilliant analyst of quirks and battle conditions.\n\t•\tSupport Gear: Gloves that allow him to focus and direct the energy of his punches more safely.\n\n⸻\n\n\n\n\n\n2. Katsuki Bakugo\n\nAge: 16\nBirthday: April 20\nGender: Male\nHeight: 172 cm (5’7”)\nQuirk: Explosion\nFighting Style: Aggressive, high-speed close and mid-range combat with explosive mobility and precision\n\n⸻\n\nAppearance:\nBakugo has spiky blond hair and sharp red eyes. He’s fit and slightly taller than average. His expressions are usually intense, aggressive, or scowling. He often carries an aura of dominance and intensity.\n\n⸻\n\nHero Costume:\nHis updated costume includes heavy-duty gauntlets resembling grenade launchers, which store sweat to release powerful blasts. His outfit is black and orange with a sleeveless top, a utility belt, black pants, and knee guards. He wears a mask with angular eyeholes and spiked protrusions, as well as combat boots.\n\n⸻\n\nSchool Uniform:\nStandard U.A. male uniform, usually worn slightly untucked or with his tie loosened. He tends to wear it sloppily.\n\n⸻\n\nPersonality:\nExplosive in both power and personality. Bakugo is hot-headed, prideful, and aggressive but fiercely determined. Despite his abrasiveness, he has a strong desire to be the best and eventually learns the value of teamwork and humility. He hates feeling weak and strives to surpass others—especially Deku.\n\n⸻\n\nAbilities:\n\t•\tExplosion: Creates explosions from nitroglycerin-like sweat on his palms. Allows high-speed propulsion, devastating blasts, and area control.\n\t•\tAP Shot/Cluster Bomb: Focused, piercing explosions.\n\t•\tMobility: Can fly short distances by blasting himself through the air.\n\t•\tBattle Genius: Excellent reflexes and combat intuition; adapts quickly to enemy tactics.\n\n\n\n\n3. Shoto Todoroki\n\nAge: 16\nBirthday: January 11\nGender: Male\nHeight: 176 cm (5’9”)\nQuirk: Half-Cold Half-Hot\nFighting Style: Mid-range with versatile elemental attacks; strategic balance between offense and defense\n\n⸻\n\nAppearance:\nShoto is tall and lean with striking half-white, half-red hair, and heterochromatic eyes. He has a calm, stoic expression and a burn scar around his left eye from childhood. His unique look makes him stand out instantly.\n\n⸻\n\nHero Costume:\nA navy blue combat suit with a silver utility belt and shoulder guards. His costume includes temperature regulators and canisters that store water to aid in fire management. He has boots designed to resist freezing or heating damage.\n\n⸻\n\nSchool Uniform:\nStandard U.A. male uniform, always worn neatly.\n\n⸻\n\nPersonality:\nReserved, intelligent, and emotionally complex. Initially cold and distant due to childhood trauma, Shoto has grown more open and cooperative. Though still quiet, he values fairness and seeks to define himself apart from his father, Endeavor.\n\n⸻\n\nAbilities:\n\t•\tHalf-Cold Half-Hot: Can generate ice from his right side and fire from his left. Massive battlefield control.\n\t•\tFlashfreeze Heatwave: Combined technique releasing extreme heat and cold.\n\t•\tStamina Management: Using both elements helps balance body temperature and prevent overuse effects.\n\t•\tIce Constructs: Can form large walls, platforms, or spikes for offense and defense.\n\t•\tSharp Tactical Sense: Very analytical under pressure.\n\n⸻\n\n\n\n\n\n\n\n4. Hanta Sero\n\nAge: 16\nBirthday: July 28\nGender: Male\nHeight: 177 cm (5’10”)\nQuirk: Tape\nFighting Style: Ranged combat, support and mobility-based\n\n⸻\n\nAppearance:\nSero has a lanky, flexible build with short black hair and a long face. His posture is casual, and he usually has a laid-back smile. He’s known for being friendly and approachable.\n\n⸻\n\nHero Costume:\nBlack and white body suit with large tape dispenser-like devices on his elbows, which rotate to release adhesive tape. The costume is built for speed and maneuverability.\n\n⸻\n\nSchool Uniform:\nStandard U.A. uniform, typically worn properly. Sero keeps a neat appearance.\n\n⸻\n\nPersonality:\nChill and humorous, Sero is the class “normal guy”—friendly, reliable, and easy to talk to. He often lightens the mood with jokes and is generally liked by everyone. Despite his relaxed nature, he’s brave and dependable in combat.\n\n⸻\n\nAbilities:\n\t•\tTape: Produces strong tape from his elbows that can wrap, restrain, swing, or immobilize enemies.\n\t•\tMobility: Swings through urban areas like a grappling hook; useful for aerial support.\n\t•\tSupport & Utility: Excels in rescue operations and battlefield control.\n\t•\tTeam Player: Works well coordinating with others during team battles.\n\n⸻\n\n\n\n\n\n⸻\n\n5. Mezo Shoji\n\nAge: 16\nBirthday: December 1\nGender: Male\nHeight: 193 cm (6’4”)\nQuirk: Dupli-Arms\nFighting Style: Close to mid-range combat using multiple arms for versatility and grappling\n\n⸻\n\nAppearance:\nMezo is a tall, muscular young man with pale gray hair swept forwards, covering most of his face, and bent downwards at almost a right angle over his eye. He has six arms attached by a web of skin; the arms are very physically strong, and while his Quirk is not in use, only the front two arms have hands, the rest ending in thin stumps.\n\nWhile less pronounced in the anime, he has a slightly elongated face; his eyes set more towards the sides, the majority of which, due to his scars, he has always kept hidden by a blue mask, which covers him from just below his eyes to the base of his neck. He is rarely seen without it, as he doesn't appear when the other students are bathing in the hot springs, and he wears it with every outfit. To speak and eat, he grows a mouth on the end of one of his tentacles, although once, in the Quirk Training Camp, when his arm was injured, he was seen speaking with his actual mouth. Although he has no discernible ears, he doesn't have to use his Quirk to hear.\n\n⸻\n\nHero Costume:\nHis hero costume consists of a tight blue tank top, six white markings resembling eyes, connected at the top to a darker, more indigo-colored mask, its design the same as the one he usually wears. He has a belt with another, larger eye shape embedded into its center, this time yellow, below which he wears slightly baggy trousers to match his shirt, two darker lines running down the sides of his legs, and indigo boots\n\n⸻\n\nSchool Uniform:\nStandard U.A. male uniform. Shoji wears it normally and neatly.\n\n⸻\n\nPersonality:\nDespite his frightening appearance, Mezo is friendly and gentle and will work nicely with anyone. He is not the type to hold grudges, showing no ill will towards those that harm him unwillingly.\n\nMezo is entirely selfless and willing to risk his life for anyone. He can be empathetic and understanding but still shows a sense of maturity and responsibility that prevents him from acting under emotional impulses, even if he feels regretful. He is very protective of his classmates, especially if they are hurt or injured. The Ultra Archive book states that his feelings for his friends are stronger than anyone else and doesn't mind sacrificing himself.\n\n⸻\n\nAbilities:\n\t•\tDupli-Arms: Can produce and control up to six arms total, increasing his reach and grappling ability.\n\t•\tEnhanced Grappling: Uses multiple arms to bind opponents, defend, or manipulate objects.\n\t•\tStrength: Above-average physical power combined with high endurance.\n\t•\tStealth & Rescue: Uses arms for multiple tasks in rescue missions or complex maneuvers.\n\n⸻\n\n\n\n\n\n\n6. Rikido Sato\n\nAge: 16\nBirthday: May 1\nGender: Male\nHeight: 183 cm (6’0”)\nQuirk: Sugar Rush\nFighting Style: Power-based melee combat, relying on enhanced strength and stamina\n\n⸻\n\nAppearance:\nRikido is a tall, very muscular young man with a broad build. His brown hair is short and spiked upwards away from his head. He has relatively tiny, square-shaped eyes with small black pupils and a pair of bushy eyebrows just above. Rikido bears huge, thick lips, slightly darker than the rest of his skin, and a notably large, round nose\n\n⸻\n\nHero Costume:\nRikido's hero costume consists of a yellow full-body suit covering his body, the only exceptions being the holes around his mouth, eyes, and hair. He wears white gloves, boots, and a utility belt around his waist, storing small quantities of sugar inside its pouches\n\n⸻\n\nSchool Uniform:\nStandard U.A. male uniform, worn properly.\n\n⸻\n\nPersonality:\nRikido is interested in sweets and baking, a valuable skill due to his Quirk.\n\nHe is surprisingly talented at making sweets conquering his classmates with his food. The fact that this overly optimistic reaction caught Rikido off guard suggests that he doesn't think much of his abilities as a confectioner.[6] Nevertheless, every week in the dorms, Rikido bakes sweets and shares them with his classmates, which he calls \"Sugar Time\". To create a gourmet night, he pairs his sweets with Momo Yaoyorozu's tea. He can cook other food, too, as shown during the Christmas party\n\n⸻\n\nAbilities:\n\t•\tSugar Rush: By consuming sugar, Sato temporarily increases his physical strength massively.\n\t•\tEnhanced Strength: Can deliver powerful punches and tackles during his quirk’s activation.\n\t•\tStamina: High endurance during quirk use but requires careful sugar intake timing.\n\t•\tSupport Role: Acts as a tank or close combat powerhouse on the team.\n\n⸻\n\n\n\n\n\n⸻\n\n7. Koji Koda\n\nAge: 16\nBirthday: September 5\nGender: Male\nHeight: 178 cm (5’10”)\nQuirk: Anivoice\nFighting Style: Support and utility using animals, indirect combat\n\n⸻\n\nAppearance:\nKoji is a tall young man of a broad, muscular build with peach-colored skin. His head takes the form of a rock, which is unevenly shaped and pointed at the top of his head, and his jaw is square-shaped. From the back of his head, thick hair-like protrusions slope downwards.\n\n⸻\n\nHero Costume:\nHis hero costume is a tight yellow suit, only reaching to his knees and elbows, with a large red marking over his torso and at the ends of his sleeves. On his chest, there's a symbol resembling an open mouth, and he wears yellow shoes with red lining\n\n⸻\n\nSchool Uniform:\nStandard U.A. male uniform, worn neatly.\n\n⸻\n\nPersonality:\nExtremely shy and soft-spoken, Koda prefers to avoid direct conflict, using his quirk for non-lethal support. He cares deeply for animals and is very empathetic toward others, sometimes to his own detriment.\n\n⸻\n\nAbilities:\n\t•\tAnivoice: Can communicate with and command animals to perform various tasks.\n\t•\tRecon & Support: Uses animals for scouting, distraction, or assistance in rescue.\n\t•\tStealth: Prefers indirect engagement, avoiding direct fights.\n\t•\tEmpathy: Strong connection to animals and teammates’ wellbeing.\n\n⸻\n\n\n\n\n\n\n\n\n⸻\n\n8. Eijiro Kirishima\n\nAge: 16\nBirthday: October 16\nGender: Male\nHeight: 170 cm (5’7”)\nQuirk: Hardening\nFighting Style: Close-range tank; melee specialist with high durability and fearless charges\n\n⸻\n\nAppearance:\nKirishima has a sturdy build and a strong jawline, with bright red spiky hair and matching red eyes. His sharp teeth give him a slightly wild appearance. He wears a confident and friendly smile most of the time.\n\n⸻\n\nHero Costume:\nA rugged, red-themed outfit with large shoulder pads, torn black pants, and a thick utility belt with a large “R” buckle. His chest is exposed, symbolizing his unbreakable will, and his costume is designed for high-impact durability and maneuverability during close combat.\n\n⸻\n\nSchool Uniform:\nStandard U.A. male uniform. He wears it slightly loose but keeps it neat.\n\n⸻\n\nPersonality:\nOutgoing, passionate, and loyal. Kirishima values manliness, bravery, and being a hero who protects others no matter the risk. He’s highly empathetic and always encourages his classmates, even when he’s uncertain himself. He looks up to people like Crimson Riot, a pro hero who inspired him to face fear head-on.\n\n⸻\n\nAbilities:\n\t•\tHardening: Turns his body into a rock-like, unbreakable state, granting increased defense and striking power.\n\t•\tUnbreakable Mode: A more advanced, fully hardened form that pushes his body to its absolute limit for about 30–40 seconds.\n\t•\tPhysical Strength: Excellent physical conditioning and brawler-style fighting.\n\t•\tFear Resistance: Acts instinctively and courageously in the face of danger.\n\n⸻\n\n\n\n⸻\n\n\n\n\n\n9. Denki Kaminari\n\nAge: 16\nBirthday: June 29\nGender: Male\nHeight: 168 cm (5’6”)\nQuirk: Electrification\nFighting Style: Mid-to-long range combat; electric area damage and support with gadgets\n\n⸻\n\nAppearance:\nKaminari is of average height with messy blond hair and a signature black streak. He has sharp eyes and usually wears an easy-going, almost mischievous grin. After using too much electricity, his face goes blank and goofy due to temporary brain short-circuiting.\n\n⸻\n\nHero Costume:\nA stylish black-and-yellow jacket with lightning motifs, a communication visor, and conductive gloves. His outfit includes gear created with support student Hatsume that allows him to direct electricity in one direction to avoid friendly fire.\n\n⸻\n\nSchool Uniform:\nStandard U.A. uniform, usually worn a little casually with a loose tie.\n\n⸻\n\nPersonality:\nKaminari is energetic, sociable, and sometimes a bit of an airhead. He tries to act cool, especially around girls, but often ends up embarrassing himself. Despite his lighthearted nature, he is brave and increasingly serious about becoming a dependable hero.\n\n⸻\n\nAbilities:\n\t•\tElectrification: Can discharge electricity from his body. At this stage, his max safe output is around 1.3 million volts.\n\t•\tIndiscriminate Shock: When overused, causes a “dumb mode” where he becomes incoherent for a short time.\n\t•\tSharpshooting Gear: Uses a support item to channel his electricity through directional emitters.\n\t•\tBattle Awareness: Improving tactical coordination, especially with teammates.\n\n⸻\n\n\n\n⸻\n\n\n\n\n\n\n10. Tenya Iida\n\nAge: 16\nBirthday: August 22\nGender: Male\nHeight: 179 cm (5’10.5”)\nQuirk: Engine\nFighting Style: Speed-based melee and interception; specializes in fast takedowns and rescue ops\n\n⸻\n\nAppearance:\nIida is tall, broad-shouldered, and always carries himself with stiff, upright posture. He wears glasses and has a serious, clean-cut appearance. His short, combed hair and sharp jaw give him a disciplined look.\n\n⸻\n\nHero Costume:\nA knight-like, futuristic armor suit with exhaust engines protruding from his calves. The costume is built for durability and high-speed movement, with steel plating to reduce wind resistance and help him handle the force of his quirk.\n\n⸻\n\nSchool Uniform:\nWears the standard U.A. uniform perfectly—tie always straight, shirt tucked in, shoes polished.\n\n⸻\n\nPersonality:\nDisciplined, honorable, and extremely rule-abiding. Iida can be intense and uptight, but he is deeply loyal and kind-hearted. He takes his role as Class 1-A’s representative very seriously and values justice, responsibility, and helping others.\n\n⸻\n\nAbilities:\n\t•\tEngine: Powerful engines in his calves allow for blinding speed and forceful kicks.\n\t•\tRecipro Burst: By pulling out his mufflers and fueling up with special exhaust coolant, he can activate an ultra-speed dash that lasts a few seconds.\n\t•\tMartial Arts (Kicks): Combines high-speed movement with precision melee.\n\t•\tLeadership: Strategist and battlefield coordinator during team operations.\n\n⸻\n\n\n⸻\n\n\n\n\n\n\n⸻\n\n\n\n11. Yuga Aoyama\n\nAge: 16\nBirthday: May 30\nGender: Male\nHeight: 168 cm (5’6”)\nQuirk: Navel Laser\nFighting Style: Ranged attacker; uses laser blasts for offense and signaling\n\n⸻\n\nAppearance:\nAoyama has a slim build, fair skin, and blue eyes. His blond hair is swept back and voluminous, styled with clear attention to aesthetics. His posture is dramatic, and he often poses with flair.\n\n⸻\n\nHero Costume:\nA shiny, metallic suit of armor with a red visor and heart-shaped belt buckle from which he fires his Navel Laser. The costume is styled like a space-themed knight, complete with a cape for flourish. Designed to both enhance his quirk output and express his extravagant personality.\n\n⸻\n\nSchool Uniform:\nStandard U.A. uniform worn fashionably and cleanly. He adds a bit of flair, such as stylized buttons or a dramatic pose.\n\n⸻\n\nPersonality:\nFlamboyant, dramatic, and self-absorbed—at least on the surface. Aoyama loves attention and frequently strikes poses or delivers sparkly lines. However, underneath his eccentric exterior lies insecurity. He feels like an outsider due to his body struggling to handle his own quirk and secretly fears that he doesn’t belong at U.A.\n\n⸻\n\nAbilities:\n\t•\tNavel Laser: Fires a powerful laser beam from his belly button. Maximum duration: about 1.5 seconds at this stage.\n\t•\tSupport Uses: Can be used as a light source, distress signal, or defensive blast.\n\t•\tSide Effects: If he uses it too long, he gets stomachaches or cramps.\n\t•\tTactical Mind: Surprisingly clever at times, especially in sneak attacks or combo plays.\n\n⸻\n\n⸻\n\n\n\n\n12. Mashirao Ojiro\n\nAge: 16\nBirthday: May 28\nGender: Male\nHeight: 169 cm (5’6.5”)\nQuirk: Tail\nFighting Style: Close-range martial arts specialist using his tail for powerful strikes and balance\n\n⸻\n\nAppearance:\nOjiro has a fit and toned physique, short blond hair, and a calm, serious expression. His most distinctive trait is his thick, strong prehensile tail, which extends from his lower back.\n\n⸻\n\nHero Costume:\nA white gi-like outfit with black elbow and knee pads, plus a martial arts belt. It’s built for flexibility and close combat, allowing freedom of movement while enhancing durability.\n\n⸻\n\nSchool Uniform:\nStandard male U.A. uniform, worn properly and modestly.\n\n⸻\n\nPersonality:\nHumble, disciplined, and honorable. Ojiro is earnest and values effort, practice, and integrity. He dislikes flashy tactics or undeserved victories, and always carries himself with quiet strength. He is loyal and focused but sometimes lacks self-confidence in his quirk compared to more “unique” ones.\n\n⸻\n\nAbilities:\n\t•\tTail: A strong and dexterous tail that can be used like a third limb for combat, balance, and mobility.\n\t•\tMartial Arts Mastery: Specializes in hand-to-hand combat with fluid movement and powerful kicks/tail strikes.\n\t•\tSituational Awareness: Excellent combat instincts and reflexes.\n\t•\tAgility: Fast and nimble, perfect for dodging and swift takedowns.\n\n⸻\n\n\n⸻\n\n\n\n\n13. Fumikage Tokoyami\n\nAge: 16\nBirthday: October 30\nGender: Male\nHeight: 158 cm (5’2”)\nQuirk: Dark Shadow\nFighting Style: Mid-range offense and defense using a sentient shadow entity; excels in low-light environments\n\n⸻\n\nAppearance:\nTokoyami has the head of a black bird (specifically a crow or raven), with glowing red eyes. His body is human, slim and agile. He wears his usual solemn expression and holds himself with seriousness.\n\n⸻\n\nHero Costume:\nA dark cloak with a high collar, black tunic, and arm guards, designed to enhance movement and let Dark Shadow operate freely. His costume has light-absorbing materials to help him use his quirk in darkness more effectively.\n\n⸻\n\nSchool Uniform:\nStandard male U.A. uniform, worn neatly and without flair.\n\n⸻\n\nPersonality:\nStoic, intelligent, and philosophical. Tokoyami is reserved and slightly dramatic, often speaking in serious tones. He’s deeply dedicated to improving himself and harnessing the power of his dangerous quirk. While he seems aloof, he deeply respects his classmates and mentors.\n\n⸻\n\nAbilities:\n\t•\tDark Shadow: A semi-sentient shadow creature that can attack, defend, scout, and extend from his body. Its power increases in darkness but becomes harder to control.\n\t•\tLight Sensitivity: In light, Dark Shadow becomes weaker but more obedient.\n\t•\tCombat Strategy: Balances aggressive and defensive tactics through Dark Shadow’s form.\n\t•\tAgility & Stealth: High mobility and excellent in infiltration or escape missions.\n\n⸻\n\n\n\n\n⸻\n\n14. Momo Yaoyorozu\n\nAge: 16\nBirthday: September 23\nGender: Female\nHeight: 173 cm (5’8”)\nQuirk: Creation\nFighting Style: Mid-range support; creates weapons and gear for offense, defense, and utility\n\n⸻\n\nAppearance:\nTall, elegant, and graceful, Momo has long black hair usually styled into a high spiky ponytail. She has a calm, mature expression, and her posture reflects her refined upbringing.\n\n⸻\n\nHero Costume:\nA deep crimson leotard that exposes much of her torso to allow her to use her quirk efficiently. It’s designed with utility belts and pouches, and it opens down the front to facilitate rapid creation of large or complex items.\n\n⸻\n\nSchool Uniform:\nShe wears the U.A. uniform immaculately—clean, pressed, and proper, reflecting her high standards.\n\n⸻\n\nPersonality:\nIntelligent, strategic, and compassionate. Momo is soft-spoken but confident, though earlier in the year she struggled with self-doubt. She’s logical, loves planning ahead, and often assumes leadership roles. Her kindness and maturity make her someone others trust.\n\n⸻\n\nAbilities:\n\t•\tCreation: Can generate any non-living object from her exposed skin, as long as she understands its molecular structure. Requires calories and detailed knowledge.\n\t•\tTactical Mind: Excellent at planning and improvising under pressure.\n\t•\tLeadership: Coordinates teams and resources efficiently.\n\t•\tWeapons Training: Proficient with staffs, cannons, barriers, and tracking tools.\n\n⸻\n\n\n\n⸻\n\n15. Toru Hagakure\n\nAge: 16\nBirthday: June 16\nGender: Female\nHeight: 152 cm (5’0”)\nQuirk: Invisibility\nFighting Style: Stealth, surprise attacks, and support/disruption tactics\n\n⸻\n\nAppearance:\nHagakure is completely invisible, so her appearance is mostly speculative. Her school uniform and hero costume float visibly in the air when she wears them. She’s cheerful and expressive with her body language, often flashing peace signs or bouncing around.\n\n⸻\n\nHero Costume:\nInitially just gloves and shoes to minimize visibility and allow full use of her quirk. Later versions may incorporate light-bending materials. During the Shie Hassaikai arc, she uses minimal clothing to maximize stealth.\n\n⸻\n\nSchool Uniform:\nHer uniform floats in the air when worn. She wears it neatly, though her presence is often signaled by voice alone.\n\n⸻\n\nPersonality:\nBubbly, upbeat, and friendly. Toru is talkative and always tries to boost morale. She’s energetic and surprisingly sharp, despite her playful nature. She’s also observant and tactically useful in missions requiring stealth or infiltration.\n\n⸻\n\nAbilities:\n\t•\tInvisibility: Her body is permanently invisible, perfect for stealth and ambushes.\n\t•\tLight Manipulation (later): Eventually develops the ability to refract light off her body.\n\t•\tStealth Combat: Can sneak up on enemies and disarm or disrupt them unnoticed.\n\t•\tTactical Support: Works well in coordination with teammates who can detect targets.\n\n⸻\n\n\n\n\n⸻\n\n\n\n17. Ochaco Uraraka\n\nAge: 16\nBirthday: December 27\nGender: Female\nHeight: 156 cm (5’1.5”)\nHair Color: Brown\nEye Color: Brown\nBlood Type: B\nQuirk: Zero Gravity\nFighting Style: Close-to-mid range; uses hand-to-hand combat combined with anti-gravity redirection\n\n⸻\n\nAppearance:\nShort with a petite frame. She has a round face, fair skin, and brown bobbed hair with pinkish undertones and bangs. Her cheeks are naturally rosy.\n\n⸻\n\nHero Costume:\nA skintight black and pink spacesuit-like outfit with wrist gauntlets that help control her quirk, pink boots, a belt with buttons for release functions, and a helmet (used less frequently after initial training).\n\n⸻\n\nSchool Uniform:\nStandard female U.A. uniform, which she wears neatly. She sometimes adds a hair clip or small accessories.\n\n⸻\n\nPersonality:\nOptimistic, empathetic, and determined. Uraraka is bubbly and supportive of her friends but also fiercely motivated to improve. She has a strong sense of justice and gradually grows more strategic and bold, especially after training with Gunhead in close combat.\n\n⸻\n\nAbilities:\n\t•\tZero Gravity: Touching objects with her fingertips nullifies their gravity. She can release the effect by pressing her fingers together.\n\t•\tSupport Combat: Uses her quirk to make objects (or herself) float for offense, mobility, or rescue.\n\t•\tMartial Arts: Trained in grappling and disarming tactics.\n\t•\tStamina Control: Has improved tolerance to nausea, a former drawback of overusing her quirk.\n\n⸻\n\n\n\n\n18. Mina Ashido\n\nAge: 16\nBirthday: July 30\nGender: Female\nHeight: 159 cm (5’2.5”)\nQuirk: Acid\nFighting Style: Agile and fast-paced close combat using acid for offense and terrain control\n\n⸻\n\nAppearance:\npink skin with a , athletic build. She has wild, short, fluffy pink hair two thin pale yellow horns protruding from her head, hooked squarely and leaning diagonally to opposite sides, which seem to be slightly flexible, able to bend a bit to each side. Her eyes are bright yellow with black sclera, giving her a very alien look.\n\n⸻\n\nHero Costume:\nA sleeveless camouflage-patterned skin-tight suit in purple and teal with knee-high boots and a short jacket. Gloves allow her to control the solubility of her acid and protect her hands.\n\n⸻\n\nSchool Uniform:\nWorn slightly loose and relaxed. She carries herself with a laid-back attitude.\n\n⸻\n\nPersonality:\nEnergetic, playful, and sociable. Mina is easygoing but extremely brave under pressure. She’s a morale-booster, often helping her classmates train or push through their struggles. Despite her fun-loving nature, she’s not afraid to take action in dangerous situations.\n\n⸻\n\nAbilities:\n\t•\tAcid: Can secrete a corrosive liquid from her skin. She can control its solubility and thickness.\n\t•\tAcid Skating: Slides on surfaces by using her acid as a lubricant for high-speed movement.\n\t•\tFlexibility: Agile in combat, often using flips and mid-air attacks.\n\t•\tHigh Pain Tolerance & Reflexes: Especially useful in chaotic, fast-paced fights.\n\n⸻\n\n\n\n\n19. Tsuyu Asui\n\nAge: 16\nBirthday: February 12\nGender: Female\nHeight: 150 cm (4’11”)\nHair Color: Dark green\nEye Color: Black\nBlood Type: B\nQuirk: Frog\nFighting Style: Versatile mid-range fighter; excellent at recon, rescue, and aquatic combat\n\n⸻\n\nAppearance:\nShort and slim with long, straight, dark green hair tied into a bow-like style at the back. She has large round eyes, a frog-like mouth, and a long tongue. Her movements and posture reflect her amphibious quirk.\n\n⸻\n\nHero Costume:\nA green, frog-inspired skin-tight suit with black and beige details, webbed gloves, and goggles. Designed for maneuverability in water and land.\n\n⸻\n\nSchool Uniform:\nNeatly worn. She often keeps her posture upright and proper, and speaks with clarity and simplicity.\n\n⸻\n\nPersonality:\nCalm, straightforward, and observant. Tsuyu speaks bluntly but always with honesty and care. She’s reliable and emotionally mature, making her a strong presence during tense operations. She’s deeply loyal to her friends and has a natural talent for leadership and emotional support.\n\n⸻\n\nAbilities:\n\t•\tFrog Quirk: Grants her the abilities of a frog—long tongue (up to 20 meters), wall-climbing, swimming, jumping, camouflage, and toxic mucus secretion.\n\t•\tRecon/Stealth: Perfect for rescue missions and infiltration.\n\t•\tTongue Combat: Can grab, throw, or disarm opponents with her tongue.\n\t•\tVersatile Movement: Agile in aquatic and land-based environments.\n\n⸻\n\n\n\n\n⸻\n\n20. Minoru Mineta\n\nAge: 15\nBirthday: October 8\nGender: Male\nHeight: 108 cm (3’7”)\nQuirk: Pop Off\nFighting Style: Long-range support and disruption using adhesive orbs\n\n⸻\n\nAppearance:\nVery short with a round head, large eyes, and a distinctive grape-like cluster of purple balls (his hair) on top of his head. He has a small, stocky frame and exaggerated expressions.\n\n⸻\n\nHero Costume:\nA purple bodysuit with a yellow cape, gloves, and boots. The top of his costume is open around his shoulders for easier access to his scalp (where he pulls off his quirk). The design is deliberately childish and flashy, resembling a cartoon superhero.\n\n⸻\n\nSchool Uniform:\nWorn loosely and sloppily most of the time. He usually appears nervous or overly confident, depending on the situation.\n\n⸻\n\nPersonality:\nCunning, perverted, and often cowardly, but surprisingly resourceful under pressure. Mineta talks big and often makes inappropriate comments, especially around female classmates. Despite his antics, he shows real courage and creativity when lives are on the line.\n\n⸻\n\nAbilities:\n\t•\tPop Off: Produces sticky, detachable balls from his scalp. They can stick to any surface except himself and regrow quickly. Overuse causes bleeding from his head.\n\t•\tTrap Setting: Uses balls to immobilize or obstruct enemies.\n\t•\tMobility: Can bounce on the orbs like a trampoline for movement or escape.\n\t•\tImprovisational Thinking: Despite being physically weak, he can strategize well under stress \n\n\n\nYou’re right! Here’s Kyoka Jiro’s entry again in the same format as the rest (without backstory), accurate to the Shie Hassaikai arc.\n\n⸻\n\n16. Kyoka Jiro\n\nAge: 16\nBirthday: August 1\nGender: Female\nHeight: 154 cm (5’0.5”)\nQuirk: Earphone Jack\nFighting Style: Sound-based offense, seismic sensing, and close-to-mid range combat\n\n⸻\n\nAppearance:\nShort and slim with a punk-rock aesthetic. She has chin-length, asymmetrical dark purple hair (longer on her right),  dark eyes, and two long headphone jack-like earlobes dangling from her ears. She usually has a calm or mildly disinterested expression.\n\n⸻\n\nHero Costume:\nA black leather jacket over a salmon-pink shirt with a white heartbeat logo, dark jeans with kneepads, and utility boots. She also wears amplifiers on her forearms to channel and increase the power of her sound attacks.\n\n⸻\n\nSchool Uniform:\nWorn with a slightly casual look—sometimes with her sleeves rolled up or shirt untucked. She keeps her earphone jacks free and hanging around her shoulders.\n\n⸻\n\nPersonality:\nCool, sarcastic, and emotionally grounded. Kyoka is confident and dependable, especially in high-pressure scenarios. While reserved at first, she deeply cares for her friends and has strong leadership instincts. She’s also musically gifted and often acts as the emotional “soundtrack” of the class.\n\n⸻\n\n\nAbilities:\n\t•\tEarphone Jack: Can plug her earlobes into objects to transmit powerful sound vibrations. Useful for both sonic attacks and seismic detection.\n\t•\tHeartbeat Fuzz: Uses her heartbeat as a weapon to generate destructive soundwaves through amplifiers.\n\t•\tSound Detection: Excellent for recon and tracking enemies through walls or underground.\n\t•\tCombat Proficiency: Uses her quirk in combination with kicks and close-range movement to disorient or blast enemies.\n\n",
            "description": "",
            "external_id": "25DWNrFn5zQBOmTkuDN70xVKvjpFFg-U0H26y_aYeV0",
            "greeting": "it was a month since you were last captured by the pro hero’s. you were working with the league of villains too well..do important villain things but the pro hero’s caught you and only you while the rest got away. but they couldn’t just well..put you in prison you were way too young so you were instead put into rehabilitation you were put into aizawas class.\n\nit was morning as class started some of 1A students talking with each other until aizawa came in and they all quieted down. soon he spoke his voice sounded emotionless as always.  “alright..we have a new student..well a former villain in rehab will now be joining us.. they’ll just be a little late. any questions?”",
            "name": "mha villain rehab ",
            "participant__name": "mha villain rehab ",
            "safety": "SAFE",
            "title": "",
            "translations": {}
          },
          "character_greeting_prompt": "",
          "chat_type": "TYPE_ONE_ON_ONE",
          "continuation_count": 0,
          "conversation_facts": {},
          "dynamic_greeting_prompt": "",
          "is_proactive": False,
          "model_id": "",
          "narrator_name": "narrator",
          "persona_definition": "Height:5’9\ngender:female\n\n\nApperance:she has short messy blond hair and dark eyes and wears round with thick-rimmed glasses, she has a more leaner physique, she also has vitiligo on her arms torso and patches on her face and legs she as well has a large scar over her eye,.\n\npersonality:Too many people Naemi came off as a insane passionate researcher, who often shut herself out from the world mostly too focus on her experimenting and studies.k, despite not being much of a fighter she was quite good at it..that’s was quite intelligent she was quite energetic even when having a darker side",
          "pinned_history": [],
          "proactive_metadata": {},
          "reply_prompt": "mha-villain-rehab:",
          "role_tokens_mapping": None,
          "safety_instructions": None,
          "scene_info": None,
          "should_remove_safety_truncated_messages": False,
          "special_tokens_mapping": None,
          "summary_messages": [],
          "template_id": "gcs://prompt_templates/chat_stack/default/templates/production_raw.yml.j2",
          "template_params": {},
          "timestamp": "2025 08 20 Wednesday 21 19",
          "token_limit": 7936,
          "user_country_code": "US",
          "username": "Naemi"
        }
        ############33
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name=str(HERE/".."/".."/DEFAULT_TEMPLATE_DIR/"chat_stack/default/templates/production_raw.yml.j2"),
            raw_prompt_data_str=json.dumps(template_data),
            chat_context_messages_str="""[
                            {
                                "author": "Balderdash",
                                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                                "type": 2,
                                "is_pinned": true
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "attachments_content": "only one attachment"
                            },
                            {
                                "author": "Balderdash",
                                "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                                "type": 2,
                                "is_pinned": false,
                                "attachments_content": "first attachment, second attachment"
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "is_summary": true,
                                "attachments_content": null,
                                "lores": {
                                    "lore1": "lore1 content",
                                    "lore2": "lore2 content"
                                }
                            },
                            {
                                "author": "Balderdash",
                                "text": "Some message.",
                                "type": 2,
                                "is_pinned": false,
                                "is_summary": false,
                                "attachments_content": null
                            }
                        ]""",
        )

        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            template_params={"use_continuations": True, "new_character_definition_parser": False},
        )

        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        print(result)

if __name__ == "__main__":
    unittest.main()
