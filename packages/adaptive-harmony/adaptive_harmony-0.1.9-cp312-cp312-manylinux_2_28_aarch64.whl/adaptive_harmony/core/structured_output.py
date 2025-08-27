import json
from enum import Enum
import re

from pydantic import BaseModel, ValidationError
from typing import Type, get_origin, get_args, Literal, Union

from adaptive_harmony import InferenceModel, StringThread


FIX_OUTPUT_FORMAT = """Below, the COMPLETION did not satisfy the constraints given in the PROMPT. Please rewrite the completion to comply with constraints, nothing else.

PROMPT
The output should be a well-formatted JSON instance that conforms to the JSON schema below. All fields are required. Do not output anything else other than the JSON.

As an example, for the schema 
{{
    "foo": {{
        "items":{{"type": "string"}},
        "type": "array"
    }}, 
    "bar": {{"type": "integer"}}
}}
the object {{"foo": ["hey", "bye"], "bar": 1}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["hey", "bye"], "bar":"1" }}}} is not well-formatted.

Here is the output JSON schema:
{json_schema}

COMPLETION
{completion}
"""


class JsonParseError(ValueError):
    def __init__(self, message: str, completion: str):
        super().__init__(message)
        self.completion = completion


def get_pydantic_schema(base_model: Type[BaseModel]) -> str:
    schema = base_model.model_json_schema()
    for prop in schema.get("properties", {}).values():
        prop.pop("title", None)
    return json.dumps(schema, indent=2)


class OutputParserException(Exception):
    """Exception raised for parsing errors."""

    def __init__(self, message: str, llm_output: str | None = None):
        super().__init__(message)
        self.llm_output = llm_output


def pydantic_parse[T: BaseModel](text: str, pydantic_object: type[T]) -> T:
    """Parse the output of an LLM call to a pydantic object.

    Args:
        text: The output of the LLM call.
        pydantic_object: The pydantic model to parse into.

    Returns:
        The parsed pydantic object.
    """
    # Strip initial whitespace
    text = text.strip()

    def parse_json_with_completion(json_text):
        """Parse JSON, handling partial JSON by completing missing brackets."""
        # Strip whitespace and backticks
        json_text = json_text.strip(" \n\r\t`")

        # Handle action_input special case - escape special chars
        if '"action_input"' in json_text:

            def fix_action_input(match):
                value = match.group(2)
                value = re.sub(r"\n", r"\\n", value)
                value = re.sub(r"\r", r"\\r", value)
                value = re.sub(r"\t", r"\\t", value)
                value = re.sub(r'(?<!\\)"', r"\"", value)
                return match.group(1) + value + match.group(3)

            json_text = re.sub(r'("action_input"\:\s*")(.*?)(")', fix_action_input, json_text, flags=re.DOTALL)

        # Try parsing as-is first
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            pass

        # Handle partial JSON - complete missing brackets and quotes
        chars = list(json_text)
        stack = []
        in_string = False
        escaped = False

        for i, char in enumerate(chars):
            if in_string:
                if char == '"' and not escaped:
                    in_string = False
                elif char == "\n" and not escaped:
                    chars[i] = "\\n"
                escaped = char == "\\" and not escaped
            elif char == '"':
                in_string = True
                escaped = False
            elif char == "{":
                stack.append("}")
            elif char == "[":
                stack.append("]")
            elif char in {"}", "]"}:
                if stack and stack[-1] == char:
                    stack.pop()

        # Close unterminated string
        if in_string:
            if escaped and chars:
                chars.pop()
            chars.append('"')

        # Add missing closing brackets
        chars.extend(reversed(stack))

        # Try parsing with progressively fewer characters
        while chars:
            try:
                return json.loads("".join(chars))
            except json.JSONDecodeError:
                chars.pop()

        # If nothing worked, raise with original
        raise json.JSONDecodeError("Invalid JSON", json_text, 0)

    # Try parsing the original text first
    try:
        json_object = parse_json_with_completion(text)
    except json.JSONDecodeError:
        # Try extracting from markdown blocks
        markdown_match = re.search(r"```(json)?(.*)", text, re.DOTALL)
        if markdown_match:
            try:
                json_object = parse_json_with_completion(markdown_match.group(2))
            except json.JSONDecodeError:
                msg = f"Invalid json output: {text}"
                raise OutputParserException(msg, llm_output=text)
        else:
            msg = f"Invalid json output: {text}"
            raise OutputParserException(msg, llm_output=text)

    try:
        return pydantic_object.model_validate(json_object)
    except ValidationError as e:
        json_string = json.dumps(json_object)
        msg = f"Failed to parse {pydantic_object.__name__} from completion {json_string}. Got: {e}"
        raise OutputParserException(msg, llm_output=json_string) from e


async def generate_and_validate[T: BaseModel](
    model: InferenceModel,
    thread: StringThread,
    pydantic_model: Type[T],
    max_parsing_retries: int = 1,
) -> tuple[str, T]:
    """
    Generates with InferenceModel, validates completion against Pydantic model and retries
    if validation fails. It's recommended you use a StructuredJSONOutputBaseModel as
    the pydantic_object to clean up the JSON schema for the LLM. Does not support RootModel.
    """

    json_schema = get_pydantic_schema(pydantic_model)

    response_thread = await model.generate(thread)
    completion = response_thread.last_content()

    current_retries = 0
    while current_retries <= max_parsing_retries:
        try:
            parsed = pydantic_parse(completion, pydantic_model)
            return (completion, parsed)
        except Exception:
            if current_retries == max_parsing_retries:
                break

            # Create repair prompt
            repair_thread = StringThread(
                [("user", FIX_OUTPUT_FORMAT.format(json_schema=json_schema, completion=completion))]
            )
            response_thread = await model.generate(repair_thread)
            completion = response_thread.last_content()
            current_retries += 1

    raise JsonParseError(f"Could not parse json output after {max_parsing_retries} retries", completion)


def _get_simplified_type(field_type):
    origin = get_origin(field_type)
    args = get_args(field_type)

    if origin is list:
        if args:
            return [_get_simplified_type(args[0])]
        else:
            return "array"
    elif origin is dict:
        if len(args) == 2:
            key_type = _get_simplified_type(args[0])
            value_type = _get_simplified_type(args[1])
            return f"Dict[{key_type}, {value_type}]"
        else:
            return "dict"
    elif origin is tuple:
        if args:
            if len(args) == 2 and args[1] is ...:
                # Variable length tuple like Tuple[str, ...]
                element_type = _get_simplified_type(args[0])
                return f"Tuple[{element_type}, ...]"
            else:
                # Fixed length tuple like Tuple[str, int]
                element_types = [_get_simplified_type(arg) for arg in args]
                return f"Tuple[{', '.join(element_types)}]"
        else:
            return "tuple"
    elif origin is set:
        if args:
            element_type = _get_simplified_type(args[0])
            return f"Set[{element_type}]"
        else:
            return "set"
    elif origin is type(None):
        return "null"
    elif origin is Literal:
        # Handle Literal types by showing them as Literal["value1", "value2"]
        # Use double quotes for strings to match JSON format and prevent LLM confusion
        literal_values = []
        for arg in args:
            if isinstance(arg, str):
                # Use double quotes for strings to match JSON format
                literal_values.append(f'"{arg}"')
            else:
                # Use repr() for non-strings (numbers, booleans, etc.)
                literal_values.append(repr(arg))
        return f"Literal[{', '.join(literal_values)}]"
    elif origin is Union:
        # Handle Union types by showing all possible types
        if len(args) == 2 and type(None) in args:
            # This is Optional[T] which is Union[T, None]
            non_none_type = [arg for arg in args if arg is not type(None)][0]
            simplified_type = _get_simplified_type(non_none_type)
            # Convert to string representation if needed
            if isinstance(simplified_type, (list, dict)):
                simplified_type = str(simplified_type).replace("'", '"')
            return f"Optional[{simplified_type}]"
        else:
            # Regular Union with multiple types
            union_types = []
            for arg in args:
                simplified = _get_simplified_type(arg)
                # Convert to string representation if needed
                if isinstance(simplified, (list, dict)):
                    union_types.append(str(simplified).replace("'", '"'))
                else:
                    union_types.append(str(simplified))
            return f"Union[{', '.join(union_types)}]"
    elif origin is not None:
        return str(origin.__name__) if origin else str(field_type.__name__)
    elif hasattr(field_type, "__bases__") and issubclass(field_type, BaseModel):
        return get_simple_pydantic_schema(field_type)
    elif hasattr(field_type, "__bases__") and issubclass(field_type, Enum):
        # Handle Enum types by showing possible values
        enum_values = [f'"{value.value}"' for value in field_type]
        return f"Enum[{', '.join(enum_values)}]"
    elif field_type is str:
        return "str"
    elif field_type is int:
        return "int"
    elif field_type is float:
        return "float"
    elif field_type is bool:
        return "bool"
    else:
        return str(field_type.__name__)


def get_simple_pydantic_schema(model: type[BaseModel]):
    representation = {}
    for field_name, field in model.model_fields.items():
        representation[field_name] = _get_simplified_type(field.annotation)
    return representation


def _format_schema_value(value, indent=0):
    """Format a schema value for display, handling nested structures."""
    indent_str = "  " * indent
    if isinstance(value, dict):
        if not value:
            return "{}"
        lines = ["{"]
        for k, v in value.items():
            formatted_value = _format_schema_value(v, indent + 1)
            lines.append(f'  {indent_str}"{k}": {formatted_value},')
        # Remove trailing comma from last item
        if lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]
        lines.append(f"{indent_str}" + "}")
        return "\n".join(lines)
    elif isinstance(value, list):
        if not value:
            return "[]"
        elif len(value) == 1:
            formatted_item = _format_schema_value(value[0], indent)
            return f"[{formatted_item}]"
        else:
            lines = ["["]
            for item in value:
                formatted_item = _format_schema_value(item, indent + 1)
                lines.append(f"  {indent_str}{formatted_item},")
            # Remove trailing comma from last item
            if lines[-1].endswith(","):
                lines[-1] = lines[-1][:-1]
            lines.append(f"{indent_str}]")
            return "\n".join(lines)
    elif isinstance(value, str) and (
        value.startswith(("Literal[", "Union[", "Optional[", "Dict[", "Tuple[", "Set[", "Enum["))
        or value in ("str", "int", "float", "bool")
    ):
        # Don't add quotes around type annotations or basic type names
        return value
    else:
        # Regular string values get quotes
        return f'"{value}"'


def render_schema(pydantic_model: type[BaseModel], with_field_descriptions: bool = True) -> str:
    simplified_schema = get_simple_pydantic_schema(pydantic_model)
    # Use custom formatting instead of json.dumps to handle Literal types properly
    schema_str = _format_schema_value(simplified_schema)

    if not with_field_descriptions:
        return schema_str

    descriptions = []
    for field_name, field in pydantic_model.model_fields.items():
        if not field.description:
            raise ValueError(f"Field '{field_name}' in model '{pydantic_model.__name__}' is missing a description.")
        descriptions.append(f"{field_name}: {field.description}")

    for field_name, field in pydantic_model.model_fields.items():
        if isinstance(field.annotation, type) and issubclass(field.annotation, BaseModel):
            nested_model = field.annotation
            for nested_field_name, nested_field in nested_model.model_fields.items():
                if not nested_field.description:
                    raise ValueError(
                        f"Field '{nested_field_name}' in nested model '{nested_model.__name__}' is missing a description."
                    )
                descriptions.append(f"{field_name}.{nested_field_name}: {nested_field.description}")
        elif get_origin(field.annotation) is list and get_args(field.annotation):
            list_item_type = get_args(field.annotation)[0]
            if isinstance(list_item_type, type) and issubclass(list_item_type, BaseModel):
                for nested_field_name, nested_field in list_item_type.model_fields.items():
                    if not nested_field.description:
                        raise ValueError(
                            f"Field '{nested_field_name}' in list item model '{list_item_type.__name__}' is missing a description."
                        )
                    descriptions.append(f"{field_name}[].{nested_field_name}: {nested_field.description}")

    return f"{schema_str}\n\n{'\n'.join(descriptions)}"


def render_pydantic_model(pydantic_model: BaseModel) -> str:
    return pydantic_model.model_dump_json()
