"""Module for lm prefix utils."""

import logging
import os
import random
import re
import string
import zlib
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from itertools import accumulate
from pathlib import Path
from threading import Lock
from typing import NamedTuple

EOM_TOKEN_STR: str = "<|endofmessage|>"  # noqa: S105
NARRATOR_NAME: str = "narrator"
MAX_USED_DEFINITION_LEN: int = 3200
MAX_USED_SCENE_DEFINITION_LEN: int = 4800
TRUNCATION_EXEMPT_EXTERNAL_IDS: list[str] = [
    "FQOYtX09Md-Foi6J2widTJq5zX5sICyhLtjItJKUiv4"  # Coach Sam Shleifer
]

# code path to server/chat/utils/vocab-06-23-2022
VOCAB_DIR: Path = Path(__file__).parent / "vocab-06-23-2022"

# Those vocab files are copied from
#   gs://character-ai-us-central1/vocab/bpe/vocab-06-23-2022
# If model changed to use a different vocab, we need to update here as well!
TOKENIZER_VOCAB: Path = VOCAB_DIR / "bpe-160000-vocab.json"
TOKENIZER_MERGES: Path = VOCAB_DIR / "bpe-160000-merges.txt"

RANDOM_NAMES: set[str] = {
    "Abdullah",
    "Ainsley",
    "Alaina",
    "Allen",
    "Allison",
    "Allyson",
    "Arabella",
    "Aron",
    "Athena",
    "Aubree",
    "Audrey",
    "Aylin",
    "Bentley",
    "Boston",
    "Branson",
    "Brenda",
    "Brennan",
    "Bronson",
    "Brynn",
    "Carina",
    "Carissa",
    "Catalina",
    "Chaya",
    "Conrad",
    "Denise",
    "Destinee",
    "Dominik",
    "Donavan",
    "Elaina",
    "Elisha",
    "Ellis",
    "Emilie",
    "Enrique",
    "Fernanda",
    "Frank",
    "Freddy",
    "Griffin",
    "Hadley",
    "Holly",
    "Houston",
    "Isiah",
    "Jabari",
    "Jacey",
    "Jaliyah",
    "Janiah",
    "Jaquan",
    "Jaylee",
    "Jerome",
    "Jessie",
    "Jewel",
    "Josue",
    "Julien",
    "Kade",
    "Kaleigh",
    "Kamryn",
    "Karlee",
    "Kaylyn",
    "Keira",
    "Kendall",
    "Kylan",
    "Lacey",
    "Lennon",
    "Lila",
    "Lillianna",
    "Madden",
    "Maggie",
    "Maia",
    "Makaila",
    "Malakai",
    "Marcelo",
    "Maryjane",
    "Maxwell",
    "Mckenzie",
    "Melody",
    "Mireya",
    "Moses",
    "Naima",
    "Nick",
    "Odin",
    "Omar",
    "Quintin",
    "Ramon",
    "Raquel",
    "Rene",
    "Roger",
    "Rubi",
    "Samir",
    "Sariah",
    "Scott",
    "Sergio",
    "Shamar",
    "Tara",
    "Tony",
    "Tyrone",
    "Xzavier",
    "Zander",
}


@dataclass(slots=True, frozen=False)
class StructuredPrefixPart:
    """Class for structured prefix part."""

    min_to_include: int
    include_from_start: bool
    messages: list[str]
    included: list[str]
    tokens: list[list[int]]
    granularity: int = 100


@dataclass(slots=True, frozen=False)
class StructuredPrefix:
    """Class for structured prefix."""

    character_definition: StructuredPrefixPart
    pinned_messages: StructuredPrefixPart
    chat_history: StructuredPrefixPart

    def all_parts(self) -> list[StructuredPrefixPart]:
        """Returns all parts of the structured prefix."""
        return [
            self.character_definition,
            self.pinned_messages,
            self.chat_history,
        ]


def get_random_name(avoid_list: Iterable[str], seed: int):
    """Returns a random name from RANDOM_NAMES that is not in avoid_list."""
    random.seed(seed)
    capitalized_avoid_list: set[str] = {s.title() for s in avoid_list}
    return random.choice(sorted(RANDOM_NAMES.difference(capitalized_avoid_list)))


# TODO: make this a dataclass.
MessageDict = dict[str, str]
# A typical example of MessageDict: { "src": "char", "text": "Hello!" }
# Messages also can have additional fields, e.g. "prefix" or "safe".

_TOKENIZER = None
tokenizer_lock = Lock()


class PrefixInjections:
    """Util class to hold the input for constructing prefix for persona."""

    class Placement(Enum):
        """Placement enum for the prefix."""

        BEFORE_CHARACTER_DEFINITION = 1
        AFTER_CHARACTER_DEFINITION = 2

    def __init__(self):
        """Initialize with an empty list of injections."""
        self.message_by_placement = {}
        for placement in PrefixInjections.Placement:
            self.message_by_placement[placement] = []

    def add_message(self, author: str, message: str, placement: Placement):
        """Add a message with an author in a desired placement."""
        new_message = {}
        new_message["src"] = canonicalize_name(author)
        new_message["text"] = message
        self.message_by_placement[placement].append(new_message)

    def get_prefixes_for_placement(self, placement: Placement) -> list[MessageDict]:
        """Get all prefix messages for a certain placement."""
        return self.message_by_placement[placement]


def message_dict_to_str(msg_dict: MessageDict) -> str:
    """Converts a message dict to a string."""
    return f'{msg_dict["src"]}: {msg_dict["text"]}'


def canonicalize_name(name: str | None) -> str:
    """Makes name format consistent with author names we use in training data."""
    if name is None:
        return "-"
    return "-".join(name.split())


def character_definition_truncated(definition: str, truncation_length: int) -> str:
    """Truncates character definition to a certain length."""
    return definition[:truncation_length]


class Canonicalizer:
    """Canonicalizes names in a line."""

    def __init__(self, names: list[str]):
        """Initializes Canonicalizer."""
        self.canonicalized_names = [(name, canonicalize_name(name)) for name in names]

    def canonicalize_line(self, line: str) -> str:
        """Canonicalizes names in a line."""
        for name, canonicalized_name in self.canonicalized_names:
            line = line.replace(name, canonicalized_name)
        return line

    def decanonicalize_line(self, line: str) -> str:
        """Decanonicalizes names in a line."""
        for name, canonicalized_name in self.canonicalized_names:
            line = line.replace(canonicalized_name, name)
        return line


def _truncate_scene_messages(character_definition_messages: list[str], scene_messages: list[str], max_chars: int = MAX_USED_SCENE_DEFINITION_LEN) -> list[str]:
    """
    Truncate a list of messages to keep the total character count under the specified limit.
    Messages are accumulated from the end of the list.

    Args:
        parsed_messages: List of message strings
        max_chars: Maximum total character count (default: 3200)

    Returns:
        List of messages that fit within the character limit
    """
    scene_truncated_messages = []
    char_count = 0

    for message in scene_messages:
        # Calculate new character count if we add this message
        new_count = char_count + len(message)
        # If adding this message would exceed the limit, stop
        if new_count > max_chars:
            up_to = max_chars - char_count
            scene_truncated_messages.append(message[:up_to])
            return scene_truncated_messages

        # Otherwise, add the message and update the count
        scene_truncated_messages.append(message)
        char_count = new_count

    character_definition_truncated_messages = []
    for message in character_definition_messages:
        new_count = char_count + len(message)
        if new_count > max_chars:
            up_to = max_chars - char_count
            character_definition_truncated_messages.append(message[:up_to])
            break

        # Otherwise, add the message and update the count
        character_definition_truncated_messages.append(message)
        char_count = new_count

    return character_definition_truncated_messages + scene_truncated_messages


def get_scene_definition(character: dict, username: str, scene_info: dict) -> list[str]:
    """Get scene definition and parse it into the message format."""
    scene_messages = scene_info.get("scene", {}).get("additional_context", {}).get("messages")
    charname = canonicalize_name(character["participant__name"])

    parsed_scene_messages = []
    for message in scene_messages:
        message = message.replace("{{char}}", charname).replace("{{user}}", username)
        parsed_scene_messages.append(message)
    character_definition_messages: list[MessageDict] = get_character_priming(character, username)

    parsed_character_definition_messages = []
    for message in character_definition_messages:
        parsed_character_definition_messages.append(message.get("src", "") + ":" + message.get("text", ""))
    return _truncate_scene_messages(character_definition_messages=parsed_character_definition_messages,
                                    scene_messages=parsed_scene_messages)


def get_character_pre_priming(
        charname: str, username: str, description: str, title: str, version: int = 0
) -> list[MessageDict]:
    if version == 1:
        return get_character_pre_priming_v1(charname, username, description, title)
    return get_character_pre_priming_v0(charname, description, title)

def get_character_pre_priming_v0(
    charname: str, description: str, title: str,
) -> list[MessageDict]:
    """Returns messages made from character name and description."""
    pre_priming = []
    if description:
        if title:
            description = f"{title} - {description}"
        description_message = {
            "src": charname,
            "text": f"{description}",
        }
        pre_priming.append(description_message)
    elif title:
        title_message = {"src": charname, "text": f"{title}"}
        pre_priming.append(title_message)
    return pre_priming


def get_character_pre_priming_v1(
        charname: str, username: str, description: str, title: str,
) -> list[MessageDict]:
    """Returns messages made from character name and description."""
    pre_priming = []
    if description:
        if username is None:
            description = description.replace("{{user}}", "{{random_user_1}}")
            authors = {"char": charname}
        else:
            authors = {"char": charname, "user": username}
        description = replace_definition_placeholders(description, authors)

        if title:
            description = f"{title} - {description}"
        description_message = {
            "src": charname,
            "text": f"{description}",
        }
        pre_priming.append(description_message)
    elif title:
        title_message = {"src": charname, "text": f"{title}"}
        pre_priming.append(title_message)
    return pre_priming


def get_character_priming(
    character: dict,
    username: str,
    *,
    truncation_length: int = MAX_USED_DEFINITION_LEN,
    unsanitized: bool = False,
    remove_example_convos: bool = False,
    skip_character_pre_priming: bool = False,
    prefix_injections: PrefixInjections = None,
    smart_truncation: bool = True,
    version: int = 0,
) -> list[MessageDict]:
    """Returns messages made from character name, description and definition."""
    definition = _get_character_definition(
        character,
        unsanitized=unsanitized,
        truncation_length=truncation_length,
        smart_truncation=smart_truncation,
    )

    charname = canonicalize_name(character["participant__name"])

    messages = []
    if not skip_character_pre_priming:
        messages = get_character_pre_priming(
            charname, username, character["description"], character["title"], version=version,
        )

    # Experiment on adding persona prefix before character definition
    if prefix_injections:
        messages.extend(
            prefix_injections.get_prefixes_for_placement(
                PrefixInjections.Placement.BEFORE_CHARACTER_DEFINITION
            )
        )

    if definition and not remove_example_convos:
        if username is None:
            definition = definition.replace("{{user}}", "{{random_user_1}}")
            authors = {"char": charname}
        else:
            authors = {"char": charname, "user": username}
        definition_msgs, _ = parse_character_definition(definition, authors=authors, version=version)
        messages.extend(definition_msgs)

    # Experiment on adding persona prefix after character definition
    if prefix_injections:
        messages.extend(
            prefix_injections.get_prefixes_for_placement(
                PrefixInjections.Placement.AFTER_CHARACTER_DEFINITION
            )
        )

    return messages


def create_character_priming_from_args(
    character_name,
    *,
    short_description="",
    long_description="",
    definition="",
    definition_username="",
    smart_truncation: bool = True,
):
    """Returns messages made from character name, descrption and definition."""
    if "{{user}}" in definition and not definition_username:
        raise ValueError(
            "definition_username is required when definition contains {{user}}"
        )
    return get_character_priming(
        character={
            "participant__name": character_name,
            "definition": definition,
            "title": short_description,
            "description": long_description,
            "sanitized_definition": "",  # TODO: call sanitizer.
        },
        username=definition_username,
        smart_truncation=smart_truncation,
    )


def parse_character_definition(
        definition: str, authors: dict[str, str], version: int = 0,
) -> tuple[list[MessageDict], list[int]]:
    if version == 1:
        return parse_character_definition_v1(definition, authors=authors)
    return parse_character_definition_v0(definition, authors=authors)


def parse_character_definition_v0(
    definition: str, authors: dict[str, str],
) -> tuple[list[MessageDict], list[int]]:
    """Parses the character definition.

    Returns a tuple, the list of MessageDicts and
    an auxiliary list of ints. This list maps the definition
    line number to the index of the corresponding MessageDict.
    """

    definition = replace_definition_placeholders(definition, authors)

    lines = definition.split("\n")
    msg_idxs = [-1] * len(lines)
    messages: list[MessageDict] = []

    prev_text = ""
    prev_line_idx: list[int] = []  # lines that are included in prev_text
    prev_author = ""

    # Any time we get a line that begins name: or {{char}}: or {{user}}: that ends whatever happened
    # prior any additional lines that follow directly are added to the prior person.

    for i, line in enumerate(lines):
        # Beginning of new user/char line.
        match_name = re.match(r"^(\S+):\s*(.*)$", line)
        if match_name:
            author, text = match_name.groups()

            if not is_empty(prev_text):
                append_message(messages, msg_idxs, prev_text, prev_author, prev_line_idx)

            prev_author, prev_text, prev_line_idx = (author, text, [i])

        elif line.startswith("END_OF_DIALOG"):
            if not is_empty(prev_text):
                append_message(messages, msg_idxs, prev_text, prev_author, prev_line_idx)
            prev_author, prev_text, prev_line_idx = ("", "", [])
        elif not prev_text and not is_empty(line):
            prev_text, prev_line_idx = line, [i]
        elif prev_text:
            prev_text = prev_text + "\n" + line
            prev_line_idx.append(i)

    if not is_empty(prev_text):
        append_message(messages, msg_idxs, prev_text, prev_author, prev_line_idx)

    return messages, msg_idxs


def parse_character_definition_v1(
        definition: str, authors: dict[str, str],
) -> tuple[list[MessageDict], list[int]]:
    lines = definition.split("\n")
    blocks = []
    dialog_idxs = []
    last_processed_idx = -1
    from_idx = 0
    for i, line in enumerate(lines):
        line = line.strip(" \r")
        if line == "END_OF_DIALOG":
            if dialog_idxs:
                for j, dialog_idx in enumerate(dialog_idxs):
                    if j == 0:
                        blocks.append((0, from_idx, dialog_idx - 1))
                        from_idx = dialog_idx
                    else:
                        blocks.append((1, from_idx, dialog_idx - 1))
                        from_idx = dialog_idx
                blocks.append((1, from_idx, i-1))
                from_idx = i + 1
                dialog_idxs = []
            else:
                blocks.append((0, from_idx, i-1))
                from_idx = i
            last_processed_idx = i
        elif re.match(r'^\s*{{.*?}}\s*:', line):
            dialog_idxs.append(i)

    if last_processed_idx != len(lines) - 1:
        blocks.append((0, from_idx, len(lines) - 1))

    definition = replace_definition_placeholders(definition, authors)
    new_lines = definition.split("\n")
    msg_idxs = [-1] * len(new_lines)
    messages: list[MessageDict] = []
    for block_type, from_idx, last_idx in blocks:
        text = "\n".join([l.strip(" \n\r") for l in new_lines[from_idx:last_idx + 1] if l.strip(" \n\r") != ""])
        if is_empty(text):
            continue
        if block_type == 0:
            append_message(messages, msg_idxs, text, "", list(range(from_idx, last_idx + 1)))
        else:
            match_name = re.match(r"^(\S+):\s*(.*)$", text, flags=re.DOTALL)
            if match_name:
                author, text = match_name.groups()
                append_message(messages, msg_idxs, text, author, list(range(from_idx, last_idx + 1)))
            else:
                append_message(messages, msg_idxs, text, "", list(range(from_idx, last_idx + 1)))

    return messages, msg_idxs


def replace_definition_placeholders(definition: str, authors: dict[str, str]) -> str:
    random_seed = zlib.adler32(definition.encode("utf-8"))

    def replace_name(match):
        name = match.group()
        assert name.startswith("{{"), f"{name=}"
        assert name.endswith("}}"), f"{name=}"
        name = name[2:-2]
        if name in authors:
            return authors[name]
        if name.startswith("random_user_"):
            author_names = authors.values()
            random_name = get_random_name(avoid_list=author_names, seed=random_seed)
            authors[name] = random_name
            return random_name

        return name

    def replace_name_canonic(match):
        return canonicalize_name(replace_name(match))

    return re.sub(
        r"{{.*?}}", replace_name_canonic, definition, flags=re.MULTILINE
    )


def is_empty(line: str) -> bool:
    return not line or line.isspace()


def append_message(messages: list[MessageDict], msg_idxs: list[int], text: str, author: str, line_idx: list[int]):
    msg_idx = len(messages)
    src = canonicalize_name(author) if author else NARRATOR_NAME
    messages.append({"src": src, "text": text.rstrip()})

    for i in line_idx:
        msg_idxs[i] = msg_idx


def sanitize_definition(
    definition: str, line_safety: list[bool], deleted_text: str = "[deleted]"
):
    """Sanitizes the definition by removing lines that are not safe."""

    def sanitize(line: str, *, safe: bool) -> str:
        if safe:
            return line
        match_name = re.match(r"^(\S+):\s*(.*)$", line)
        if match_name:
            author, _ = match_name.groups()
            return message_dict_to_str({"src": author, "text": deleted_text})

        return ""

    lines = definition.split("\n")
    if len(lines) != len(line_safety):
        raise ValueError(f"{len(lines)=} != {len(line_safety)=}")

    return "\n".join(
        [
            sanitize(text, safe=safe)
            for text, safe in zip(lines, line_safety, strict=False)
        ]
    )


REPLY_TEMPLATE = "%(author)s:"
MESSAGE_TEMPLATE = "%(author)s: %(text)s"
USER_IMAGE_TEMPLATE = "\n![%(image_description)s](image.jpg)"


def _get_character_definition(
    character: dict,
    *,
    unsanitized: bool,
    truncation_length: int = MAX_USED_DEFINITION_LEN,
    smart_truncation: bool = True,
) -> str:
    definition = character.get("sanitized_definition", "")

    # If the sanitized_definition is not populated, use the definition instead.
    # Also, use the unsanitized definition if unsanitized is True.
    if not definition or unsanitized:
        definition = character.get("definition", "")

    # TODO(james): Refactor this into a character schema change for truncation overrides.
    if character.get("external_id", "") in TRUNCATION_EXEMPT_EXTERNAL_IDS:
        logging.info(
            f"Character definition exempt from truncation: {character['external_id']=}\n\n{definition=}"
        )
        return definition

    # For certain language, character count truncation will consume way more tokens than
    # English, leaving less room for chat history and potentially bad memory
    # e.g. Chinese character takes up to 2 tokens while English takes down to 1/4 tokens
    if smart_truncation and truncation_length / 4 < len(definition) < truncation_length:
        full_tokens = get_ntokens(definition)
        estimated_truncation_tokens = int(truncation_length / 4)
        ratio = min(estimated_truncation_tokens / full_tokens, 1.0)
        truncation_length = int(len(definition) * ratio)

    return character_definition_truncated(definition, truncation_length)


def format_each_message_with_author_name(
    msgs: list[MessageDict],
    reply_src: str | None = None,
    add_space_first_msg=False,
) -> list[str]:
    """Turn a message history into a formated list of message strings."""
    prefix_messages: list[str] = []
    for i, msg in enumerate(msgs):
        msg_filled = MESSAGE_TEMPLATE % {
            "author": msg["src"],
            "text": msg["text"],
        }
        if i == 0 and add_space_first_msg:
            msg_filled = f" {msg_filled}"
        if msg.get("image_description"):
            msg_filled += USER_IMAGE_TEMPLATE % {
                "image_description": msg["image_description"]
            }

        prefix_messages.append(msg_filled)

    if reply_src is not None:
        # note the following allows histories that end with the character.
        # that's equivalent to allowing the character to reply to themselves.
        if ":" in reply_src:
            prefix_messages.append(reply_src)
        else:
            prefix_messages.append(REPLY_TEMPLATE % {"author": reply_src})

    return prefix_messages


INVINCIBLE_TOKENIZER: str = os.getenv("INVINCIBLE_TOKENIZER", "")


def get_tokenizer():
    """Get the tokenizer, initializing it if necessary."""
    from chartok import heather, invincible  # pylint: disable=import-error

    global _TOKENIZER  # noqa: PLW0603
    with tokenizer_lock:
        if _TOKENIZER is None:
            logging.info(f"Initializing tokenizer from {TOKENIZER_VOCAB}")
            _TOKENIZER = invincible() if len(INVINCIBLE_TOKENIZER) > 0 else heather()
            # _TOKENIZER = chartok_tokenizer.build_tokenizer_offline(
            #     TOKENIZER_MERGES, TOKENIZER_VOCAB, tokenization_split_numbers=True
            # )
            logging.info("Tokenizer successfully initialized.")
    return _TOKENIZER


def get_ntokens(input_str: str) -> int:
    """Get the number of tokens in the input string."""
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(input_str)
    return len(tokens)


class PrefixBuilder:
    """Builds a prefix from a list of messages."""

    def __init__(
        self,
        preamble_msgs: list[MessageDict],
        body_msgs: list[MessageDict] | None = None,
        prefix_token_limit: int | None = None,
        reserve_space_for_extra: str | None = None,
        author_name_to_add: str = "",
    ):
        """Initialize the prefix builder."""
        assert prefix_token_limit is not None  # change signature?
        if not body_msgs:
            raise NotImplementedError(f"{len(body_msgs)=}")

        def get_len(input_str: str) -> int:
            return get_ntokens(input_str) + 1  # +1 for BOM

        preamble_strangs = [
            f"{m['src']}: {m['text']}{EOM_TOKEN_STR}" for m in preamble_msgs
        ]
        self.preamble_toklens = [get_len(m) for m in preamble_strangs]
        body_messages = [f"{m['src']}: {m['text']}{EOM_TOKEN_STR}" for m in body_msgs]
        self.message_toklens = [get_len(x) for x in body_messages]
        lens = [len(x) for x in body_messages]
        lens = [0, *lens]
        self.prefix_lens = list(accumulate(lens))
        self.full_preamble = "".join(preamble_strangs)
        self.full_body = "".join(body_messages)
        self.suffix = author_name_to_add
        if author_name_to_add and ":" not in author_name_to_add:
            self.suffix = REPLY_TEMPLATE % {"author": author_name_to_add}
        self.body_messages = body_messages
        self.len_limit = prefix_token_limit
        # add 1 for BOD
        self.length_wo_messages = sum(self.preamble_toklens) + get_len(self.suffix) + 1

        if reserve_space_for_extra:
            self.length_wo_messages += get_len(reserve_space_for_extra)

    def get_last(self):
        """Get the prefix for the last message."""
        return self.get_prefix_for_ith_message(len(self.body_messages))

    def get_prefix_for_ith_message(self, i):
        """Get the prefix for the ith message."""
        num_messages_to_include = self._msgs_to_include(i)
        if num_messages_to_include == 0:
            return f"{self.full_preamble}{self.suffix}"
        start, end = self.prefix_lens[i - num_messages_to_include], self.prefix_lens[i]
        return f"{self.full_preamble}{self.full_body[start:end]}{self.suffix}"

    def _msgs_to_include(self, i) -> int:
        prefix_length = self.length_wo_messages
        num_messages_to_include = 0
        for j in range(i - 1, -1, -1):
            prefix_length += self.message_toklens[j]
            if prefix_length > self.len_limit:
                break
            num_messages_to_include += 1
        return num_messages_to_include


# TODO: remove prefix_char_limit, because prefix_token_limit has superseded it.
def get_lm_prefix(
    preamble_msgs: list[MessageDict],
    reply_src: str | None = None,
    body_msgs: list[MessageDict] | None = None,
    prefix_char_limit: int | None = None,
    prefix_token_limit: int | None = None,
    reserve_space_for_extra: str | None = None,
) -> str:
    """Get the prefix for the LM.

    Iff prefix_limit is set, cap the number of characters returned,
    by starting with the last message of body_msgs.

    prefix_token_limit:
      length limit defined in number of tokens. If set, it overrides
      prefix_char_limit (which is defined in number of characters).

    reserve_space_for_extra:
      If set, reserve enough space to allow adding reserve_space_for_extra later.
    """
    if body_msgs:
        prefix_messages = format_each_message_with_author_name(preamble_msgs)
        body_messages = format_each_message_with_author_name(
            body_msgs, reply_src=reply_src
        )
    else:
        prefix_messages = format_each_message_with_author_name(
            preamble_msgs, reply_src=reply_src
        )
        body_messages = []

    len_limit = prefix_token_limit if prefix_token_limit else prefix_char_limit
    if len_limit is None:
        return EOM_TOKEN_STR.join(prefix_messages + body_messages)

    def get_len(input_str: str):
        if prefix_token_limit:
            return get_ntokens(input_str) + 2  # Add 2 for EOM and BOM tokens.

        return len(input_str) + 2

    prefix_length = sum(get_len(m) for m in prefix_messages)

    # Add 1 for BOD token.
    # if reply_src: this gets cancelled out, because it wont get an EOM.
    if reply_src is None:
        prefix_length += 1
    if reserve_space_for_extra:
        prefix_length += get_len(reserve_space_for_extra)

    # see how many messages from the back we can use
    num_messages_to_include = 0
    for msg in reversed(body_messages):
        prefix_length += get_len(msg)
        if prefix_length > len_limit:
            break
        num_messages_to_include += 1

    # just use last messages
    if num_messages_to_include > 0:
        return EOM_TOKEN_STR.join(
            prefix_messages + body_messages[-num_messages_to_include:]
        )
    # TODO: raise warning(couldn't include any messages from body.)
    # get prefix messages once again, this time with the reply_src
    prefix_messages = format_each_message_with_author_name(
        preamble_msgs, reply_src=reply_src
    )
    return EOM_TOKEN_STR.join(prefix_messages)


class TokenizedContext(NamedTuple):
    """Tokenized context."""

    tokens: list[str]
    idx_after_timestamp: int
    context_num_msg: int
    truncated_num_msg: int


def tokenize_structured_prefix(
    structured_prefix: dict,
    token_limit: int | None = None,
    tokenizer=None,
    cache_friendly_truncation_step=1000,
    *,
    cache_friendly: bool,
    close_last_message=True,
) -> TokenizedContext:
    """Tokenize structured prefix."""
    if tokenizer is None:
        tokenizer = get_tokenizer()

    # Get inputs.
    sp = structured_prefix
    timestamp_str = sp.get("timestamp", "")
    char_def_strs: list[str] = sp.get("character_definitions", [])
    chat_history_strs: list[str] = sp.get("chat_history", [])
    chat_hist_global_index = sp.get("chat_hist_global_index", 0)
    reply_prompt_str = sp.get("reply_prompt", "")
    space_added = sp.get("space_added", False)
    timestamp_tokens: list[int] = sp.pop(
        "timestamp_tokens", tokenizer.tokenize(timestamp_str)
    )

    # TODO(SS): Delete after character server deploy 2023-02-23
    # TODO(SS): can delete comment too, copied over.
    # Add space between timestamp and following messages.
    # Most messages are separated by eom and bom, but timestamp is only separated by space.
    # Attach to the next available msg, to mimic how tokenizer works during training.
    if timestamp_str and not space_added:
        if char_def_strs:
            char_def_strs = char_def_strs.copy()  # Avoid modifying the original list.
            char_def_strs[0] = " " + char_def_strs[0]
        elif chat_history_strs:
            chat_history_strs = chat_history_strs.copy()
            chat_history_strs[0] = " " + chat_history_strs[0]
        else:
            reply_prompt_str = " " + reply_prompt_str

    reply_prompt: list[int] = sp.pop(
        "reply_prompt_tokens", tokenizer.tokenize(reply_prompt_str)
    )
    # Tokenize all input strings.

    char_defs = sp.pop(
        "character_definition_tokens", [tokenizer.tokenize(x) for x in char_def_strs]
    )
    chat_history = sp.pop(
        "chat_history_tokens", [tokenizer.tokenize(x) for x in chat_history_strs]
    )
    # Messages in char_defs and char_history are always followed by eom and bom.
    eom_bom: list[int] = [tokenizer.eom_id, tokenizer.bom_id]
    for msg in char_defs:
        msg.extend(eom_bom)
    for idx, msg in enumerate(chat_history):
        if idx != len(chat_history) - 1 or close_last_message:
            msg.extend(eom_bom)
    # for x in char_defs:  assert_unnested(x)
    # for x in chat_history: assert_unnested(x)
    # Build output token list: bod, timestamp, char_def, chat_history, reply_prompt.
    tokens = [tokenizer.bod, *timestamp_tokens]
    # assert_unnested(tokens)
    idx_after_timestamp = len(tokens)

    for msg in char_defs:
        if not token_limit or len(tokens) + len(msg) + len(reply_prompt) <= token_limit:
            tokens += msg

    def _num_msgs_to_add__no_cache():
        if not token_limit:
            return len(chat_history)
        msgs_to_add = 0
        history_len = 0
        budget = token_limit - len(tokens) - len(reply_prompt)
        for msg in reversed(chat_history):
            if history_len + len(msg) <= budget:
                history_len += len(msg)
                msgs_to_add += 1
            else:
                break
        return msgs_to_add

    def _num_msgs_to_add__cache_friendly():
        if not token_limit:
            return len(chat_history)

        # test if no truncation needed.
        history_total_len = sum(len(msg) for msg in chat_history)

        budget = token_limit - len(tokens) - len(reply_prompt)
        if history_total_len <= budget:
            return len(chat_history)

        # ignore msgs until next the first full hundred global index
        if chat_hist_global_index % 100 == 0:
            start_idx = 0
        else:
            start_idx = 100 - (chat_hist_global_index % 100)
        chat_history2 = chat_history[start_idx:]
        history_total_len = sum(len(x) for x in chat_history2)

        # consider truncation every cache_friendly_truncation_step tokens
        tokens_eliminated = 0
        time_to_test = 0
        for idx, msg in enumerate(chat_history2):
            if tokens_eliminated >= time_to_test:
                if history_total_len - tokens_eliminated <= budget:
                    return len(chat_history2) - idx

                time_to_test += cache_friendly_truncation_step
            tokens_eliminated += len(msg)
        return 0

    # Add chat history for as long as possible.
    if cache_friendly:
        msgs_to_add = _num_msgs_to_add__cache_friendly()
    else:
        msgs_to_add = _num_msgs_to_add__no_cache()
    if msgs_to_add > 0:
        for msg in chat_history[-msgs_to_add:]:
            tokens += msg

    # Add reply prompt.
    if close_last_message:
        tokens += reply_prompt
    return TokenizedContext(
        tokens=tokens,
        idx_after_timestamp=idx_after_timestamp,
        context_num_msg=msgs_to_add,
        truncated_num_msg=len(chat_history) - msgs_to_add,
    )


def get_structured_lm_prefix(
    preamble_msgs: list[MessageDict],
    reply_src: str,
    body_msgs: list[MessageDict],
    prefix_token_limit: int,
    use_reply_template=True,
    cache_friendly=True,
) -> dict:
    """Get structured lm prefix."""
    structured_prefix = prepare_structured_prefix(
        preamble_msgs,
        reply_src,
        body_msgs,
        prefix_token_limit,
        use_reply_template=use_reply_template,
    )
    return _get_structured_lm_prefix(
        structured_prefix, prefix_token_limit, cache_friendly=cache_friendly
    )


def get_structured_chat_prefix(
    preamble_messages: list[str],
    body_messages: list[str],
    reply_prompt: str,
    timestamp_utc: str,
    prefix_token_limit: int,
    cache_friendly=True,
    close_last_message=True,
) -> dict:
    """Used by chat service."""
    # This is a hack to get around the fact that the tokenizer doesn't work correctly with space_added=False.
    # The space is added in prepare_structured_prefix(), which is called from get_structured_lm_prefix()
    # but not from this function. So we just append a space to the timestamp here.
    if timestamp_utc and not timestamp_utc.endswith(" "):
        timestamp_utc += " "

    structured_prefix = _prepare_structured_prefix(
        preamble_messages,
        body_messages,
        reply_prompt,
        timestamp_utc,
        prefix_token_limit,
    )
    return _get_structured_lm_prefix(
        structured_prefix,
        prefix_token_limit,
        cache_friendly=cache_friendly,
        close_last_message=close_last_message,
    )


def get_structured_pinned_chat_prefix(
    preamble_messages: list[str],
    pinned_messages: list[str],
    body_messages: list[str],
    reply_prompt: str,
    timestamp_utc: str,
    prefix_token_limit: int,
    cache_friendly=True,
    close_last_message=True,
) -> dict:
    """Used by chat service."""
    # This is a hack to get around the fact that the tokenizer doesn't work correctly with space_added=False.
    # The space is added in prepare_structured_prefix(), which is called from get_structured_lm_prefix()
    # but not from this function. So we just append a space to the timestamp here.
    if timestamp_utc and not timestamp_utc.endswith(" "):
        timestamp_utc += " "

    structured_prefix = _prepare_structured_pinned_prefix(
        StructuredPrefix(
            character_definition=StructuredPrefixPart(
                min_to_include=0,
                include_from_start=True,
                messages=preamble_messages if preamble_messages else [],
                included=[],
                tokens=[],
            ),
            pinned_messages=StructuredPrefixPart(
                min_to_include=0,
                include_from_start=False,
                messages=pinned_messages if pinned_messages else [],
                included=[],
                tokens=[],
            ),
            chat_history=StructuredPrefixPart(
                min_to_include=1,
                include_from_start=False,
                messages=body_messages if body_messages else [],
                included=[],
                tokens=[],
            ),
        ),
        reply_prompt,
        timestamp_utc,
        prefix_token_limit,
    )
    return _get_structured_lm_prefix(
        structured_prefix,
        prefix_token_limit,
        cache_friendly=cache_friendly,
        close_last_message=close_last_message,
    )


def _get_structured_lm_prefix(
    structured_prefix: dict,
    prefix_token_limit: int,
    *,
    cache_friendly: bool,
    close_last_message=True,
) -> dict:
    tokenized_context = tokenize_structured_prefix(
        structured_prefix,
        cache_friendly=cache_friendly,
        token_limit=prefix_token_limit,
        close_last_message=close_last_message,
    )
    # average timings: prepare: 11ms, tokenize 8ms (sam)

    structured_prefix["token_limit"] = prefix_token_limit
    structured_prefix["tokenized_context"] = tokenized_context
    for k in [
        "chat_history_tokens",
        "character_definition_tokens",
        "timestamp_tokens",
        "reply_prompt_tokens",
    ]:
        structured_prefix.pop(k, None)
    return structured_prefix


def prepare_structured_prefix(
    preamble_msgs: list[MessageDict],
    reply_src: str,
    body_msgs: list[MessageDict],
    prefix_token_limit: int,
    use_reply_template=True,
) -> dict:
    """Prepare structured prefix.

    Return a dict with following fields:
    character_definitions: list[str] character definitions formatted as messages.
    chat_history: list[str] messages in the chat history.
    chat_hist_global_index: The index of body_messages[0] in the actual dialog.
    reply_prompt: The promt like "<CharName>: " for the current message to generate.
    timestamp: The timestamp in string format.

    Re Truncation: if the full history is too long to return, we return such a
    list that:
        * it consists of msg_id range starting from a multiples of 100 till the end
        * it contains AT LEAST prefix_token_limit tokens in the body_messages.
    """
    if use_reply_template:
        reply_prompt = REPLY_TEMPLATE % {"author": reply_src}
    else:
        reply_prompt = reply_src

    if not (body_msgs or preamble_msgs):
        reply_prompt = f" {reply_prompt}"

    preamble_messages = format_each_message_with_author_name(
        preamble_msgs, add_space_first_msg=True
    )
    add_space_first_chat = not preamble_messages
    body_messages = (
        None
        if not body_msgs
        else format_each_message_with_author_name(
            body_msgs, add_space_first_msg=add_space_first_chat
        )
    )
    timestamp_utc = current_utc_timestamp()
    return _prepare_structured_prefix(
        preamble_messages,
        body_messages,
        reply_prompt,
        timestamp_utc,
        prefix_token_limit,
    )


def _prepare_structured_prefix(
    preamble_messages: list[str],
    body_messages: list[str],
    reply_prompt: str,
    timestamp_utc: str,
    prefix_token_limit: int,
) -> dict:
    tokenizer = get_tokenizer()
    reply_prompt_tokens = tokenizer.tokenize(reply_prompt)
    timestamp_tokens = tokenizer.tokenize(timestamp_utc)
    preamble_tokens = [tokenizer.tokenize(m) for m in preamble_messages]
    if not body_messages:
        return {
            "character_definitions": preamble_messages,  # Useless soon
            "character_definition_tokens": preamble_tokens,
            "chat_history": [],  # Useless soon
            "chat_history_tokens": [],
            "chat_hist_global_index": None,
            "reply_prompt": reply_prompt,  # Useless soon
            "reply_prompt_tokens": reply_prompt_tokens,
            "timestamp": timestamp_utc,  # Useless soon
            "timestamp_tokens": timestamp_tokens,
            "space_added": True,
            "token_limit": prefix_token_limit,
        }

    prefix_length = 0
    num_messages_to_include = 0
    # TODO(Bowen): there is a risk of sending too much load here. The length limit
    # for user messages is very high, like 100k chars (?), so in the worst scenario
    # we could be sending an extra of 100/2*100k = 5Mb here. The fix could be just
    # send a token count instead of the full message for the extra messages beyond
    # prefix_token_limit.

    prefix_tokens_reversed = []
    budget = (
        prefix_token_limit
        - len(reply_prompt_tokens)
        - len(timestamp_tokens)
        - len(preamble_tokens)
        - 1
    )  # -1 for BOD

    for msg_id, msg in reversed(list(enumerate(body_messages))):
        tokens = tokenizer.tokenize(msg)
        prefix_tokens_reversed.append(tokens)
        prefix_length += len(tokens) + 2  # +2 for EOM and BOM tokens
        num_messages_to_include += 1
        if prefix_length >= budget and msg_id % 100 == 0:
            break

    # just use last messages
    index_start = len(body_messages) - num_messages_to_include
    return {
        "character_definitions": preamble_messages,
        "character_definition_tokens": preamble_tokens,
        "chat_history": body_messages[index_start:],
        "chat_history_tokens": list(reversed(prefix_tokens_reversed)),
        "chat_hist_global_index": index_start,
        "reply_prompt": reply_prompt,
        "reply_prompt_tokens": reply_prompt_tokens,
        "timestamp": timestamp_utc,
        "timestamp_tokens": timestamp_tokens,
        "space_added": True,
        "token_limit": prefix_token_limit,
    }


def _prepare_structured_pinned_prefix(
    structured_prefix: StructuredPrefix,
    reply_prompt: str,
    timestamp_utc: str,
    prefix_token_limit: int,
) -> dict:
    tokenizer = get_tokenizer()
    reply_prompt_tokens = tokenizer.tokenize(reply_prompt)
    timestamp_tokens = tokenizer.tokenize(timestamp_utc)
    budget = prefix_token_limit - len(reply_prompt_tokens) - len(timestamp_tokens) - 1

    # Include minimum number of messages for each part
    for part in structured_prefix.all_parts():
        if part.min_to_include > 0:
            if part.include_from_start:
                messages = part.messages[: part.min_to_include]
            else:
                messages = part.messages[-part.min_to_include :]
            process, consumed_budget = _add_messages_and_tokens(
                tokenizer, budget, messages, part
            )
            budget -= consumed_budget
            if not process:
                break

    # Include rest of messages until budget is reached
    for part in structured_prefix.all_parts():
        consumed_messages = len(part.included)
        if part.include_from_start:
            messages = part.messages[consumed_messages:]
        else:
            messages = (
                part.messages[:-consumed_messages]
                if consumed_messages > 0
                else part.messages
            )
        process, consumed_budget = _add_messages_and_tokens(
            tokenizer, budget, messages, part
        )
        budget -= consumed_budget
        if not process:
            break

    preamble_messages = (
        structured_prefix.character_definition.included
        + structured_prefix.pinned_messages.included
    )
    preamble_tokens = (
        structured_prefix.character_definition.tokens
        + structured_prefix.pinned_messages.tokens
    )

    chat_hist_start_index = len(structured_prefix.chat_history.messages) - len(
        structured_prefix.chat_history.included
    )

    return {
        "character_definitions": preamble_messages,
        "character_definition_tokens": preamble_tokens,
        "chat_history": structured_prefix.chat_history.included,
        "chat_history_tokens": structured_prefix.chat_history.tokens,
        "chat_hist_global_index": chat_hist_start_index,
        "reply_prompt": reply_prompt,
        "reply_prompt_tokens": reply_prompt_tokens,
        "timestamp": timestamp_utc,
        "timestamp_tokens": timestamp_tokens,
        "space_added": True,
        "token_limit": prefix_token_limit,
    }


def _add_messages_and_tokens(
    tokenizer, budget: int, messages: list[str], part: StructuredPrefixPart
) -> tuple[bool, int]:
    prefix_length = 0
    prefix_tokens = []
    num_messages_to_include = 0
    process = True
    msgs = enumerate(messages)
    if not part.include_from_start:
        msgs = reversed(list(msgs))
    for msg_id, msg in msgs:
        tokens = tokenizer.tokenize(msg)
        prefix_tokens.append(tokens)
        prefix_length += len(tokens) + 2  # +2 for EOM and BOM tokens
        num_messages_to_include += 1
        if prefix_length >= budget and msg_id % part.granularity == 0:
            process = False
            break

    if part.include_from_start:
        part.included.extend(messages[:num_messages_to_include])
        part.tokens.extend(prefix_tokens)
    else:
        index_start = len(messages) - num_messages_to_include
        part.included = messages[index_start:] + part.included
        part.tokens = list(reversed(prefix_tokens)) + part.tokens

    consumed = sum(len(x) + 2 for x in prefix_tokens)
    return process, consumed


def populate_lm_prefixes(
    messages: list[MessageDict],
    character_definition: str | None = None,
    prefix_char_limit: int | None = None,
    *,
    filter_alternative_from_prefix: bool = False,
):
    """Adds "prefix" field to all the messages."""
    # TODO(SS): use prefix token limit
    for i, msg in enumerate(messages):
        prefix_messages = [
            m
            for m in messages[:i]
            if not (filter_alternative_from_prefix and m["is_alternative"])
        ]
        if character_definition:
            prefix = get_lm_prefix(
                character_definition,
                body_msgs=prefix_messages,
                reply_src=msg["src"],
                prefix_char_limit=prefix_char_limit,
            )
        else:
            prefix = get_lm_prefix(preamble_msgs=prefix_messages, reply_src=msg["src"])
        msg["prefix"] = prefix


def text_to_lm_prefix(
    text: str,
    default_author: str = NARRATOR_NAME,
    authors: list[str] | None = None,
    *,
    timestamp_prefix: bool = True,
) -> str:
    """Converst a text representation of a dialog to lm_prefix.

    Inserts EOM token between messages.
    If dialog starts without a explicit author, the first
    message is assigned to default_author.
    """
    if authors is None:
        authors = []
    canonicalizer = Canonicalizer(authors)
    result = []
    for line in text.splitlines():
        match_name = re.match(r"^(.+?:)(.*)$", line)
        if result:
            result.append(EOM_TOKEN_STR if match_name else "\n")
        elif not match_name:
            result.append(default_author + ": ")
        result.append(canonicalizer.canonicalize_line(line))
    if timestamp_prefix:
        result = [current_utc_timestamp(), " ", *result]
    return "".join(result)


def messages_to_lm_prefix(
    messages: list[tuple[str, str]],
    char_name: str,
    canonicalizer: Canonicalizer,
    *,
    timestamp_prefix: bool = True,
) -> str:
    """Converst a list of (author, text) tuples to lm prefix."""
    turns: list[str] = []
    for author, text in messages:
        line = f"{author}: {text}"
        turns.append(canonicalizer.canonicalize_line(line))
    turns.append(canonicalize_name(char_name) + ":")
    result = EOM_TOKEN_STR.join(turns)
    if timestamp_prefix:
        result = current_utc_timestamp() + " " + result
    return result


def current_utc_timestamp():
    """Returns a timestamp in UTC timezone."""
    return datetime.now(timezone.utc).strftime("%Y %m %d %A %H %M")  # noqa: UP017


# Unit test helpers


def random_string(nchar=10):
    """Returns a random string of lowercase letters."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(nchar))


def assert_no_double_space(strang):
    """Raises ValueError if there is a double space in the string."""
    for i in range(1, len(strang)):
        if strang[i] == " " and strang[i - 1] == " ":
            raise ValueError(f"double space at position {i}: {strang[:i]=}")


# temporary duplicate proposed method of creating prefix for mu rooms for testing


def construct_system_message_text(
    op,
    updated_chat_properties_dict,
    added_human_participant_names,
    removed_human_participant_names,
    added_character_infos,
    removed_character_infos,
    responsible_human_participant_or_character_name,
):
    """Construct system message.

    Args:
        op: What operation took place: create_muroom, update_muroom, join_muroom, etc.
        updated_chat_properties_dict: Properties like room title, description, visibility, etc.
        added_human_participant_names: names of human participants added to the chat with
            operation op.
        removed_human_participant_names: names of human participants removed from the chat with
            operation op.
        added_character_infos: details of characters added to the chat with operation op.
        removed_character_infos: details of characters removed from the chat with operation op.
        responsible_human_participant_or_character_name: One who took this action.

    Note: For now, system messages are in english only. Extend this to foreign languages as
        well as part of the internationalization effort.

    """

    def names_join(names):
        names_str = ", ".join(names[:-1])
        if len(names) > 1:
            names_str += f" and {names[-1]}"
        elif len(names) == 1:
            names_str += names[-1]
        return names_str

    def pluralize(text, count):
        if count > 1:
            if text == "is":
                return "are"
            if text == "has":
                return "have"
        return text

    def concat_desc(short_desc, long_desc):
        if short_desc and long_desc:
            return short_desc + " - " + long_desc
        return short_desc + long_desc

    system_message = ""
    if op == "create_muroom":
        system_message += (
            f"{responsible_human_participant_or_character_name} created the room"
        )
        if "title" in updated_chat_properties_dict:
            system_message += (
                f" with the title: {updated_chat_properties_dict['title']}"
            )
        system_message += ".\n\n"
    elif op == "update_muroom":
        if "title" in updated_chat_properties_dict:
            system_message += f"""{
            responsible_human_participant_or_character_name
            } changed the title of the room to: {updated_chat_properties_dict['title']}.\n\n"""

    if added_human_participant_names:
        system_message += (
            names_join(added_human_participant_names)
            + f" {pluralize('has', len(added_human_participant_names))} joined the chat.\n\n"
        )

    if added_character_infos:
        added_character_names = [c["name"] for c in added_character_infos]
        system_message += (
            names_join(added_character_names)
            + f" {pluralize('is', len(added_character_names))} added to the chat"
        )
        if responsible_human_participant_or_character_name:
            system_message += f" by {responsible_human_participant_or_character_name}"
        system_message += ".\n\n"
        for c in added_character_infos:
            short_desc = c.get("short_description", "")
            long_desc = c.get("long_description", "")
            if short_desc or long_desc:
                system_message += f"""{c['name']} is described as: {
                concat_desc(short_desc, long_desc)
                }.\n\n"""

    if removed_human_participant_names:
        system_message += (
            names_join(removed_human_participant_names)
            + f" {pluralize('has', len(removed_human_participant_names))} left the chat.\n\n"
        )

    if removed_character_infos:
        removed_character_names = [c["name"] for c in removed_character_infos]
        system_message += (
            names_join(removed_character_names)
            + f" {pluralize('is', len(removed_character_names))} removed from the chat"
        )
        if responsible_human_participant_or_character_name:
            system_message += f" by {responsible_human_participant_or_character_name}"
        system_message += ".\n\n"

    return system_message
