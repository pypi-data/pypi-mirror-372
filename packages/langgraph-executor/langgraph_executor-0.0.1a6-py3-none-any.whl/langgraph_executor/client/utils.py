import base64
import copy
import re
from collections.abc import Sequence
from typing import Any, cast

from google.protobuf.json_format import MessageToDict
from langchain_core.messages import AIMessageChunk, BaseMessage
from langchain_core.messages.utils import convert_to_messages
from langchain_core.runnables import RunnableConfig
from langgraph._internal._config import _is_not_empty
from langgraph._internal._constants import (
    CONFIG_KEY_CHECKPOINT_ID,
    CONFIG_KEY_CHECKPOINT_MAP,
    CONFIG_KEY_CHECKPOINT_NS,
    CONFIG_KEY_DURABILITY,
    CONFIG_KEY_RESUMING,
    CONFIG_KEY_TASK_ID,
    CONFIG_KEY_THREAD_ID,
)
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.pregel.debug import CheckpointMetadata
from langgraph.types import StateSnapshot

from langgraph_executor.common import reconstruct_config, val_to_pb
from langgraph_executor.pb import runtime_pb2, types_pb2

SERDE = JsonPlusSerializer()


def input_to_pb(input):
    return val_to_pb(None, input)


def _is_present_and_not_empty(config: RunnableConfig, key: Any) -> bool:
    return key in config and _is_not_empty(config[key])


def maybe_update_reserved_configurable(
    key: str, value: Any, reserved_configurable: types_pb2.ReservedConfigurable
) -> bool:
    if key == CONFIG_KEY_RESUMING:
        reserved_configurable.resuming = bool(value)
    elif key == CONFIG_KEY_TASK_ID:
        reserved_configurable.task_id = str(value)
    elif key == CONFIG_KEY_THREAD_ID:
        reserved_configurable.thread_id = str(value)
    elif key == CONFIG_KEY_CHECKPOINT_MAP:
        reserved_configurable.checkpoint_map.update(cast(dict[str, str], value))
    elif key == CONFIG_KEY_CHECKPOINT_ID:
        reserved_configurable.checkpoint_id = str(value)
    elif key == CONFIG_KEY_CHECKPOINT_NS:
        reserved_configurable.checkpoint_ns = str(value)
    # elif key == CONFIG_KEY_PREVIOUS:
    #     serde = JsonPlusSerializer()
    #     meth, ser = serde.dumps_typed(value)
    #     reserved_configurable.previous = types_pb2.SerializedValue(method=meth, value=bytes(ser))
    elif key == CONFIG_KEY_DURABILITY:
        reserved_configurable.durability = str(value)
    else:
        return False

    return True


def merge_configurables(
    config: RunnableConfig, pb_config: types_pb2.RunnableConfig
) -> None:
    if not _is_present_and_not_empty(config, "configurable"):
        return

    configurable = pb_config.configurable
    reserved_configurable = pb_config.reserved_configurable

    for k, v in config["configurable"].items():
        if not maybe_update_reserved_configurable(k, v, reserved_configurable):
            try:
                configurable.update({k: v})
            except ValueError:  # TODO handle this
                print(f"could not pass config field {k}:{v} to proto")


def config_to_pb(config: RunnableConfig) -> types_pb2.RunnableConfig:
    if not config:
        return types_pb2.RunnableConfig()

    # Prepare kwargs for construction
    kwargs = {}

    if _is_present_and_not_empty(config, "run_name"):
        kwargs["run_name"] = config["run_name"]

    if _is_present_and_not_empty(config, "run_id"):
        kwargs["run_id"] = str(config["run_id"]) if config["run_id"] else ""

    if _is_present_and_not_empty(config, "max_concurrency"):
        kwargs["max_concurrency"] = int(config["max_concurrency"])

    if _is_present_and_not_empty(config, "recursion_limit"):
        kwargs["recursion_limit"] = config["recursion_limit"]

    # Create the config with initial values
    pb_config = types_pb2.RunnableConfig(**kwargs)

    # Handle collections after construction
    if _is_present_and_not_empty(config, "tags"):
        if isinstance(config["tags"], list):
            pb_config.tags.extend(config["tags"])
        elif isinstance(config["tags"], str):
            pb_config.tags.append(config["tags"])

    if _is_present_and_not_empty(config, "metadata"):
        pb_config.metadata.update(config["metadata"])

    merge_configurables(config, pb_config)

    return pb_config


def context_to_pb(context: dict[str, Any] | Any) -> types_pb2.Context | None:
    if context is None:
        return None

    # Convert dataclass or other objects to dict if needed
    if hasattr(context, "__dict__") and not hasattr(context, "items"):
        # Convert dataclass to dict
        context_dict = context.__dict__
    elif hasattr(context, "items"):
        # Already a dict-like object
        context_dict = context
    else:
        # Try to convert to dict using vars()
        context_dict = vars(context) if hasattr(context, "__dict__") else {}

    return types_pb2.Context(context=context_dict)


# TODO
def create_runopts_pb(
    stream_mode,
    output_keys,
    interrupt_before,
    interrupt_after,
    durability,
    debug,
    subgraphs,
) -> runtime_pb2.RunOpts:
    # Prepare kwargs for construction
    kwargs = {}

    if durability is not None:
        kwargs["durability"] = durability

    if debug is not None:
        kwargs["debug"] = debug

    if subgraphs is not None:
        kwargs["subgraphs"] = subgraphs

    if output_keys is not None:
        string_or_slice_pb = None
        if isinstance(output_keys, str):
            string_or_slice_pb = types_pb2.StringOrSlice(
                is_string=True, values=[output_keys]
            )
        elif isinstance(output_keys, list[str]):
            string_or_slice_pb = types_pb2.StringOrSlice(
                is_string=False, values=output_keys
            )

        if string_or_slice_pb is not None:
            kwargs["output_keys"] = string_or_slice_pb

    # Create the RunOpts with initial values
    run_opts = runtime_pb2.RunOpts(**kwargs)

    # Handle repeated fields after construction
    if stream_mode is not None:
        if isinstance(stream_mode, str):
            run_opts.stream_mode.append(stream_mode)
        elif isinstance(stream_mode, list):
            run_opts.stream_mode.extend(stream_mode)

    if interrupt_before is not None:
        run_opts.interrupt_before.extend(interrupt_before)

    if interrupt_after is not None:
        run_opts.interrupt_after.extend(interrupt_after)

    # Note: checkpoint_during field doesn't exist in RunOpts proto
    # Ignoring it as it's not in the proto definition

    return run_opts


def decode_response(response, stream_mode):
    which = response.WhichOneof("message")
    if which == "error":
        raise ValueError(response.error)
    if which == "chunk":
        return decode_chunk(response.chunk, stream_mode)
    if which == "chunk_list":
        return [
            decode_chunk(chunk.chunk, stream_mode)
            for chunk in response.chunk_list.chunks
        ]

    raise ValueError("No stream response")


VAL_KEYS = {"method", "value"}


def deser_vals(chunk: dict[str, Any]):
    return _deser_vals(copy.deepcopy(chunk))


def _deser_vals(current_chunk):
    if isinstance(current_chunk, list):
        return [_deser_vals(v) for v in current_chunk]
    if not isinstance(current_chunk, dict):
        return current_chunk
    if set(current_chunk.keys()) == VAL_KEYS:
        return SERDE.loads_typed(
            (current_chunk["method"], base64.b64decode(current_chunk["value"]))
        )
    for k, v in current_chunk.items():
        if isinstance(v, dict | Sequence):
            current_chunk[k] = _deser_vals(v)
    return current_chunk


def decode_state_history_response(response):
    if not response:
        return

    return [reconstruct_state_snapshot(state_pb) for state_pb in response.history]


def decode_state_response(response):
    if not response:
        return

    return reconstruct_state_snapshot(response.state)


# TODO finish reconstructing these
def reconstruct_state_snapshot(state_pb: types_pb2.StateSnapshot) -> StateSnapshot:
    return StateSnapshot(
        values=deser_vals(MessageToDict(state_pb.values)),
        next=tuple(state_pb.next),
        config=reconstruct_config(state_pb.config),
        metadata=CheckpointMetadata(**MessageToDict(state_pb.metadata)),
        created_at=state_pb.created_at,
        parent_config=reconstruct_config(state_pb.parent_config),
        tasks=tuple(),
        interrupts=tuple(),
    )


def decode_chunk(chunk, stream_mode):
    d = cast(dict[str, Any], deser_vals(MessageToDict(chunk)))
    stream_mode = stream_mode or ()
    mode = d.get("mode")
    ns = d.get("ns")
    # Handle messages mode specifically - we don't always send the stream mode in the chunk
    # Because if user only has 1 mode, we exclude it since it is implied
    if mode == "messages" or (mode is None and "messages" in stream_mode):
        return (ns, extract_message_chunk(d["payload"]))

    # Handle custom mode primitive extraction
    payload = d.get("payload")

    # For custom mode, unwrap primitives from "data" wrapper
    if mode == "custom" or (mode is None and "custom" in stream_mode):
        if isinstance(payload, dict) and len(payload) == 1 and "data" in payload:
            payload = payload["data"]

    # Regular logic for all modes
    if ns:
        if mode:
            return (ns, mode, payload)
        return (ns, payload)
    if mode:
        return (mode, payload)

    return payload


class AnyStr(str):
    def __init__(self, prefix: str | re.Pattern = "") -> None:
        super().__init__()
        self.prefix = prefix

    def __eq__(self, other: object) -> bool:
        return isinstance(other, str) and (
            other.startswith(self.prefix)
            if isinstance(self.prefix, str)
            else self.prefix.match(other)
        )

    def __hash__(self) -> int:
        return hash((str(self), self.prefix))


def extract_message_chunk(
    payload: dict[str, Any],
) -> tuple[BaseMessage, dict[str, Any]]:
    """Extract (BaseMessage, metadata) tuple from messages mode payload"""

    # Extract writes from payload and deserialize the message data
    message_data = payload.get("message", {}).get("message", {})
    metadata = payload.get("metadata", {})
    message_type = message_data.get("type", "ai")
    if message_type.endswith("Chunk"):
        message_id = message_data.get("id")
        content = message_data.get("content", "")
        additional_kwargs = message_data.get("additional_kwargs", {})
        usage_metadata = message_data.get("usage_metadata", None)
        tool_calls = message_data.get("tool_calls", [])
        name = message_data.get("name")
        tool_call_chunks = message_data.get("tool_call_chunks", [])
        response_metadata = message_data.get("response_metadata", {})
        if message_type == "AIMessageChunk":
            message = AIMessageChunk(
                content=content,
                id=message_id,
                additional_kwargs=additional_kwargs,
                tool_calls=tool_calls,
                name=name,
                usage_metadata=usage_metadata,
                tool_call_chunks=tool_call_chunks,
                response_metadata=response_metadata,
            )
            return (message, metadata)
        else:
            raise ValueError(f"Unknown message type: {message_type}")

    else:
        return convert_to_messages([message_data])[0], metadata
