# universal_message/utils/messages_to_sharegpt.py
import hashlib
import logging
import pathlib
import typing

import durl
import pydantic
from openai.types.shared.function_definition import FunctionDefinition
from rich.pretty import pretty_repr

if typing.TYPE_CHECKING:
    from universal_message import Message

logger = logging.getLogger(__name__)

ListFunctionDefinitionAdapter = pydantic.TypeAdapter(typing.List[FunctionDefinition])


def messages_to_sharegpt(
    messages: typing.List["Message"],
    media_dir: pathlib.Path | str | None = None,
    *,
    tool_definitions: typing.List[FunctionDefinition] | None = None,
    tools_column: str = "tools",
    images_column: str = "images",
    videos_column: str = "videos",  # Not implemented
    audios_column: str = "audios",
    role_tag: str = "role",
    content_tag: str = "content",
    user_tag: str = "user",
    assistant_tag: str = "assistant",
    observation_tag: str = "observation",
    function_tag: str = "function_call",
    system_tag: str = "system",
    messages_tag: str = "messages",
) -> dict:
    """Convert messages to ShareGPT format with media extraction."""
    output = {}
    output_messages: list[dict] = []
    output_tools: list[dict] = []
    output_images: list[str] = []
    output_audios: list[str] = []
    output[messages_tag] = output_messages
    media_dir = pathlib.Path(media_dir) if media_dir else pathlib.Path("./data")
    media_dir.mkdir(parents=True, exist_ok=True)

    # Handle message content
    for msg in messages:
        if msg.role in ("system", "developer"):
            output_messages.append({role_tag: system_tag, content_tag: msg.content})
        elif msg.role == "user":
            if durl.DataURL.is_data_url(msg.content):
                _content_data_url = durl.DataURL.from_url(msg.content)
                if _content_data_url.is_audio_content:
                    __content_bytes = (
                        _content_data_url.data_decoded.encode("utf-8")
                        if isinstance(_content_data_url.data_decoded, str)
                        else _content_data_url.data_decoded
                    )
                    __content_md5 = hashlib.md5(__content_bytes).hexdigest()
                    __ext = {mime: ext for ext, mime in durl.ExtensionMIMEType.items()}[
                        _content_data_url.mime_type
                    ]
                    __content_file_name = f"{__content_md5}.{__ext}"
                    __content_path = media_dir.joinpath(__content_file_name)
                    __content_path.write_bytes(__content_bytes)
                    output_messages.append({role_tag: user_tag, content_tag: "<audio>"})
                    output_audios.append(str(__content_path))
                elif _content_data_url.is_image_content:
                    __content_bytes = (
                        _content_data_url.data_decoded.encode("utf-8")
                        if isinstance(_content_data_url.data_decoded, str)
                        else _content_data_url.data_decoded
                    )
                    __content_md5 = hashlib.md5(__content_bytes).hexdigest()
                    __ext = {mime: ext for ext, mime in durl.ExtensionMIMEType.items()}[
                        _content_data_url.mime_type
                    ]
                    __content_file_name = f"{__content_md5}.{__ext}"
                    __content_path = media_dir.joinpath(__content_file_name)
                    __content_path.write_bytes(__content_bytes)
                    output_messages.append({role_tag: user_tag, content_tag: "<image>"})
                    output_images.append(str(__content_path))
                elif _content_data_url.is_text_content:
                    output_messages.append(
                        {
                            role_tag: user_tag,
                            content_tag: str(_content_data_url.data_decoded),
                        }
                    )
                else:
                    raise ValueError(
                        "Unsupported data URL: "
                        + f"{pretty_repr(_content_data_url, max_string=100)}"
                    )
            else:
                output_messages.append({role_tag: user_tag, content_tag: msg.content})
        elif msg.role == "assistant":
            # Function call
            if msg.call_id or msg.tool_name or msg.channel == "commentary":
                output_messages.append(
                    {role_tag: function_tag, content_tag: msg.arguments or "{}"}
                )
            # Assistant answer
            else:
                output_messages.append(
                    {role_tag: assistant_tag, content_tag: msg.content}
                )
        elif msg.role == "tool":
            output_messages.append(
                {role_tag: observation_tag, content_tag: msg.content}
            )
        else:
            logger.warning(f"Not supported role '{msg.role}' in sharegpt format")

    # Handle tools definitions
    if tool_definitions:
        output_tools.extend(ListFunctionDefinitionAdapter.dump_python(tool_definitions))
    # Try to get tools definitions from messages
    else:
        for msg in messages:
            __meta = msg.metadata or {}
            __tool_defs_json = __meta.get("dialogue_tools_definitions") or __meta.get(
                "tools"
            )
            if __tool_defs_json:
                output_tools.extend(
                    ListFunctionDefinitionAdapter.dump_python(
                        ListFunctionDefinitionAdapter.validate_json(
                            str(__tool_defs_json)
                        )
                    )
                )
                break

    if output_tools:
        output[tools_column] = output_tools
    if output_images:
        output[images_column] = output_images
    if output_audios:
        output[audios_column] = output_audios
    return output
