# Project Description

### Hermes

Defining and constructing production-grade LLM prompts via rich structured templates.

---

### Usage (INTERNAL ONLY)
```
import datetime

from hermes_cai import build_structured_prefix
from hermes_cai.structured_prefix import StructuredPrefix, ChatContextMessage

# Retrieve Data.

# chat: dict
# character: dict
# user: dict
# persona_character: dict
# turns: List[dict]
# candidates: dict[str, dict]

# Parse persona data.
persona_definition = None
username = user.name
if persona_character:
    persona_definition = (
        persona_character.get("sanitized_definition")
        if persona_character.get("sanitized_definition")
        else persona_character.get("definition")
    )
    if persona_character.get("name") != "My Persona":
        username = persona_cahracter.get("name")


chat_context_messages = []
for turn in turns:
    candidate = candidates.get(turn["primary_candidate_id"])
    ccm = ChatContextMessage(
        author=turn.author_name,
        text=candidate.raw_content,
        is_pinned=turn.is_pinned,
        type=0,  # unused
    )
    chat_context_messages.append(ccm)


# Prepare the raw data.
raw_prompt_data = {
    "character": character,
    "chat_type": chat.chat_type,
    "user_id": user.id,
    "character_id": character.id,
    "chat_id": chat.id,
    "persona_definition": persona_definition,
    "username": username,
}

# Prepare structured prefix for hermes-cai package.
structured_prefix = StructuredPrefix(
    # METADATA
    "reply_prompt": f"{character.get('name')}:",
    "timestamp": datetime.utcnow(),
    "space_added": True,
    "use_hermes_generation": True,
    "hermes_generation_template_name": "production_raw.yml.j2",
    "token_limit": TOKEN_LIMIT,  # IMPORTANT: this must not result in mismatch on model server otherwise it will fallback to legacy prompt.
    # DATA
    "raw_prompt_data_dict": raw_prompt_data,
    "chat_context_messages": chat_context_messages,
)

hermes_structured_prefix = build_structured_prefix(
    contextual_logger=logging.getLogger(__name__),  # Provides contextual logging.
    structured_prefix=structured_prefix,
    close_last_message=True,
)
```

---

### Goals & Requirements

1. Centralized: By centralizing the prompt construction into one place, Hermes aims to simplify the prompt construction mechanics.
2. Extensible: Make it as easy as possible to create new prompts for new use cases.
3. Experimentation: Must be easy to experiment with wholly different prompt formats and content.

Fundamentally, Hermes is split into two layers -- the Templating Layer and the Logical Layer. We aim to keep a clear separation between these layers such that the Templating Layer exclusively handles the representation of the prompt and the Logical Layer handles the mechanics of constructing the prompt.

---

### Templating Layer

#### Templates
Prompt templates are expressive and human-readable files that define the prompt structure, data placements, and formatting of the final prompt. The templating engine aims to strike a balance between being readable and explicit with no magic under-the-hood. As such, we have chosen to use a combination of YAML and Jinja syntax to represent prompt templates -- a common templating language for DevOps tools like Ansible.

Fundamentally, prompt templates are YAML files. Once the jinja syntax is fully rendered they contain a repeating sequence of prompt parts. Each part contains the following fields:
- `name`: a unique name given to the prompt part used for readability and sometimes used functionally such as for truncation.
- `content`: the string payload representing the content to be tokenized for this prompt part.
- `truncation_priority`: the priority given to the prompt part during truncation.

We construct the final prompt by concatenating the `content` of these parts together to form the final prompt and do a best effort attempt at following the truncation policy implicit in the `truncation_priority` field. In the future we may support additional fields. We use Jinja syntax to express arbitrary complexity in the templates such as control flow and function calls.

##### Alternatives considered
- Langchain: PromptTemplate, AIMessage, SystemMessage, and HumanMessage abstractions. Basically just f-strings wrapped in a Python class, not very readable or expressive enough.
- LMQL: Not very readable, non-trivial to reason about what the final interpolated prompt would look like.
- Raw Python f-strings: Better readability but not very expressive.
- Jinja: Probably the best standalone bet found so far but leaves several things to be desired. See an example here.
- YAML: Could also work by rolling our own basic interpreter. See an example here.
- Several OSS “prompt management” solutions: Pezzo, Agenta, PromptHub (paid), Langflow. These all miss the mark in terms of extensibility of the core templating language and infrastructure and focus on using external APIs rather than needing to truncate and tokenize, which is crucial for us as we host our own models.

#### Template Registry:
The Template Registry is a central repository where all prompt templates are stored. It serves as a single source of truth for prompt definitions, ensuring consistency and ease of access. The registry allows users to:

- Browse existing templates.
- Add new templates.
- Update existing templates.
- Version control templates to track changes over time.
- Validate templates to ensure they meet required standards.

---

### Logical Layer

The Logical Layer contains the necessary logic for rendering templates and performing tokenization and truncation. It handles the dynamic aspects of prompt construction, ensuring that the final prompts adhere to specified length constraints and are correctly formatted.

#### 1. Rendering:
The rendering process takes a template and fills in the necessary data to produce a final prompt. This involves:

- Data binding: Inserting data into the template.
- Evaluation: Processing any conditional logic or loops defined in the template.
- Formatting: Ensuring the final output is correctly structured.

#### 2. Tokenization
Tokenization is the process of breaking down the final prompt into tokens that the LLM can understand. This involves:

- Identifying token boundaries: Ensuring the prompt is split into meaningful units.
- Handling special characters: Properly encoding or escaping characters that have special meaning in the model's tokenization scheme.

#### 3. Truncation
Truncation ensures the prompt fits within the model's maximum `token_limit`.
This involves:
- Prioritizing parts: Using the `truncation_priority` field to determine which parts of the prompt can be truncated if necessary.
- Smart truncation: Preserving the most important parts of the prompt while removing less critical ones.

#### 4. Validation
Validation ensures the final prompt adheres to all specified constraints and formatting rules.
This involves:
- Schema validation: Ensuring the prompt meets the defined schema requirements.
- Token limit validation: Ensuring the prompt does not exceed the model's maximum token limit.

---

By adhering to these principles and design choices, Hermes aims to provide a robust, flexible, and easy-to-use system for constructing high-quality LLM prompts.
