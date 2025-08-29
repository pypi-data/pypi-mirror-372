import logging
from typing import Any

import grpc
from langgraph._internal._config import ensure_config
from langgraph.errors import GraphInterrupt, GraphRecursionError
from langgraph.pregel import Pregel
from langgraph.runtime import get_runtime
from langgraph.types import Interrupt
from pydantic import ValidationError

from langgraph_executor.client.utils import (
    SERDE,
    config_to_pb,
    context_to_pb,
    create_runopts_pb,
    decode_response,
    input_to_pb,
)
from langgraph_executor.common import var_child_runnable_config
from langgraph_executor.pb import runtime_pb2
from langgraph_executor.pb.runtime_pb2 import OutputChunk
from langgraph_executor.pb.runtime_pb2_grpc import LangGraphRuntimeStub


def _patch_pregel(runtime_client: LangGraphRuntimeStub, logger: logging.Logger):
    async def patched_ainvoke(pregel_self, input, config=None, **kwargs):
        return await _ainvoke_wrapper(
            runtime_client, logger, pregel_self, input, config, **kwargs
        )

    def patched_invoke(pregel_self, input, config=None, **kwargs):
        return _invoke_wrapper(
            runtime_client, logger, pregel_self, input, config, **kwargs
        )

    Pregel.ainvoke = patched_ainvoke  # type: ignore[invalid-assignment]
    Pregel.invoke = patched_invoke  # type: ignore[invalid-assignment]


async def _ainvoke_wrapper(
    runtime_client: LangGraphRuntimeStub,
    logger: logging.Logger,
    pregel_self: Pregel,  # This is the actual Pregel instance
    input,
    config=None,
    context=None,
    stream_mode=["values"],
    output_keys=None,
    interrupt_before=None,
    interrupt_after=None,
    durability=None,
    debug=None,
    subgraphs=False,
) -> dict[str, Any] | Any:
    """Wrapper that handles the actual invoke logic."""

    # subgraph names coerced when initializing executor
    graph_name = pregel_self.name

    logger.info(f"SUBGRAPH INVOKE ENCOUNTERED: {graph_name}")

    # TODO: Hacky way of retrieving runtime from runnable context
    if not context:
        try:
            runtime = get_runtime()
            if runtime.context:
                context = runtime.context
        except Exception as e:
            logger.error(f"failed to retrive parent runtime for subgraph: {e}")

    if parent_config := var_child_runnable_config.get({}):
        config = ensure_config(config, parent_config)

    try:
        # create request
        invoke_request = runtime_pb2.InvokeRequest(
            graph_name=graph_name,
            input=input_to_pb(input),
            config=config_to_pb(config),
            context=context_to_pb(context),
            run_opts=create_runopts_pb(
                stream_mode,
                output_keys,
                interrupt_before,
                interrupt_after,
                durability,
                debug,
                subgraphs,
            ),
        )

        # get response - if this blocks, you might need to make it async
        try:
            # Option 1: If runtime_client.Invoke is synchronous and might block:
            import asyncio

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, runtime_client.Invoke, invoke_request
            )

            if response.WhichOneof("message") == "error":
                error = response.error.error

                if error.WhichOneof("error_type") == "graph_interrupt":
                    graph_interrupt = error.graph_interrupt

                    interrupts = []

                    for interrupt in graph_interrupt.interrupts:
                        interrupts.append(
                            Interrupt(
                                value=SERDE.loads_typed(
                                    (
                                        interrupt.value.base_value.method,
                                        interrupt.value.base_value.value,
                                    )
                                ),
                                id=interrupt.id,
                            )
                        )

                    raise GraphInterrupt(interrupts)

                else:
                    raise ValueError(
                        f"Unknown subgraph error from orchestrator: {error!s}"
                    )

        except grpc.RpcError as e:
            # grpc_message is inside str(e)
            details = str(e)
            if details and "recursion limit exceeded" in details.lower():
                raise GraphRecursionError
            if details and "invalid context format" in details.lower():
                raise TypeError
            if details and "invalid pydantic context format" in details.lower():
                import json

                # Extract the JSON error data from the error message
                error_msg = str(e)
                if ": {" in error_msg:
                    json_part = "{" + error_msg.split(": {")[1]
                    try:
                        error_data = json.loads(json_part)
                        raise ValidationError.from_exception_data(
                            error_data["title"], error_data["errors"]
                        )
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.error(f"JSONDecodeError: {e}")
                # Fallback if parsing fails
                raise ValidationError.from_exception_data(
                    "ValidationError",
                    [
                        {
                            "type": "value_error",
                            "loc": ("context",),
                            "msg": "invalid pydantic context format",
                            "input": None,
                        }
                    ],
                )
            raise

        # decode response
        return decode_response(response, stream_mode)

    except Exception as e:
        if isinstance(e, grpc.RpcError):
            logger.error(f"gRPC client/runtime error: {e!s}")
        raise e


def _invoke_wrapper(
    runtime_client: LangGraphRuntimeStub,
    logger: logging.Logger,
    pregel_self: Pregel,  # This is the actual Pregel instance
    input,
    config=None,
    context=None,
    stream_mode=["values"],
    output_keys=None,
    interrupt_before=None,
    interrupt_after=None,
    durability=None,
    debug=None,
    subgraphs=False,
) -> dict[str, Any] | Any:
    """Wrapper that handles the actual invoke logic."""

    # subgraph names coerced when initializing executor
    graph_name = pregel_self.name

    logger.info(f"SUBGRAPH INVOKE ENCOUNTERED: {graph_name}")

    # TODO: Hacky way of retrieving runtime from runnable context
    if not context:
        try:
            runtime = get_runtime()
            if runtime.context:
                context = runtime.context
        except Exception as e:
            logger.error(f"failed to retrive parent runtime for subgraph: {e}")

    # need to get config of parent because wont be available in orchestrator
    if parent_config := var_child_runnable_config.get({}):
        config = ensure_config(config, parent_config)

    try:
        # create request
        invoke_request = runtime_pb2.InvokeRequest(
            graph_name=graph_name,
            input=input_to_pb(input),
            config=config_to_pb(config),
            context=context_to_pb(context),
            run_opts=create_runopts_pb(
                stream_mode,
                output_keys,
                interrupt_before,
                interrupt_after,
                durability,
                debug,
                subgraphs,
            ),
        )

        try:
            response: OutputChunk = runtime_client.Invoke(invoke_request)

            if response.WhichOneof("message") == "error":
                error = response.error.error

                if error.WhichOneof("error_type") == "graph_interrupt":
                    graph_interrupt = error.graph_interrupt

                    interrupts = []

                    for interrupt in graph_interrupt.interrupts:
                        interrupts.append(
                            Interrupt(
                                value=SERDE.loads_typed(
                                    (
                                        interrupt.value.base_value.method,
                                        interrupt.value.base_value.value,
                                    )
                                ),
                                id=interrupt.id,
                            )
                        )

                    raise GraphInterrupt(interrupts)

                else:
                    raise ValueError(
                        f"Unknown subgraph error from orchestrator: {error!s}"
                    )

        except grpc.RpcError as e:
            # grpc_message is inside str(e)
            details = str(e)
            if details and "recursion limit exceeded" in details.lower():
                raise GraphRecursionError
            if details and "invalid context format" in details.lower():
                raise TypeError
            if details and "invalid pydantic context format" in details.lower():
                import json

                # Extract the JSON error data from the error message
                error_msg = str(e)
                if ": {" in error_msg:
                    json_part = "{" + error_msg.split(": {")[1]
                    try:
                        error_data = json.loads(json_part)
                        raise ValidationError.from_exception_data(
                            error_data["title"], error_data["errors"]
                        )
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.error(f"JSONDecodeError: {e}")
                # Fallback if parsing fails
                raise ValidationError.from_exception_data(
                    "ValidationError",
                    [
                        {
                            "type": "value_error",
                            "loc": ("context",),
                            "msg": "invalid pydantic context format",
                            "input": None,
                        }
                    ],
                )
            raise

        # decode response
        return decode_response(response, stream_mode)

    except Exception as e:
        if isinstance(e, grpc.RpcError):
            logger.error(f"gRPC client/runtime error: {e!s}")
        raise e


__all__ = [
    "_patch_pregel",
]
