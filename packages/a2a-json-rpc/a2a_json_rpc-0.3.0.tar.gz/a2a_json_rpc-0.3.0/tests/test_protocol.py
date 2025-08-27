# tests/test_protocol.py
"""
JSON-RPC 2.0 dispatcher for A2A (Agent-to-Agent) interoperability.
Transport-agnostic: parse, validate, dispatch, serialize responses.
"""
from __future__ import annotations
import json
import logging
import pkgutil
import anyio
from inspect import iscoroutinefunction
from typing import Any, Awaitable, Callable, Dict, Optional, Union
from typing_extensions import ParamSpec, Concatenate

# a2a
from a2a_json_rpc.models import Request, Response, Json
from a2a_json_rpc.json_rpc_errors import (
    JSONRPCError,
    ParseError,
    InvalidRequestError,
    MethodNotFoundError,
    InternalError,
)
from a2a_json_rpc.a2a_errors import (
    TaskNotFoundError,
    TaskNotCancelableError,
    PushNotificationsNotSupportedError,
    UnsupportedOperationError,
)

# logging
logger = logging.getLogger(__name__)

P = ParamSpec("P")
Handler = Callable[Concatenate[str, P], Any | Awaitable[Any]]


class JSONRPCProtocol:
    """Dispatch JSON-RPC 2.0 requests to registered handlers."""

    def __init__(self) -> None:
        # Load the A2A JSON‑RPC schema from the bundled file (or create empty)
        try:
            data = pkgutil.get_data(__package__, "a2a_spec.json")
            if data is None:
                logger.warning("Could not load bundled a2a_spec.json")
                self._schema = {}
            else:
                self._schema = json.loads(data)
        except Exception as e:
            logger.warning(f"Error loading schema: {e}")
            self._schema = {}

        # Method registry and ID counter
        self._methods: Dict[str, Handler] = {}
        self._id_counter = 0

    def register(self, name: str, func: Handler, /) -> None:
        """Register a handler for the given method name."""
        self._methods[name] = func

    def method(self, name: str):
        """Decorator to register a method handler."""
        def decorator(func: Handler) -> Handler:
            self.register(name, func)
            return func
        return decorator

    def next_id(self) -> int:
        """Generate a new unique request ID."""
        self._id_counter += 1
        return self._id_counter

    def create_request(
        self, method: str, params: Any = None, *, id: Optional[Union[int, str]] = None
    ) -> Json:
        """Build a JSON-RPC request object as a dict."""
        if id is None:
            id = self.next_id()
        return Request(id=id, method=method, params=params).model_dump(exclude_none=True)

    def create_notification(self, method: str, params: Any = None) -> Json:
        """Build a JSON-RPC notification (no ID)."""
        return Request(method=method, params=params).model_dump(exclude_none=True)

    def handle_raw(self, raw: str | bytes | Json) -> Optional[Json]:
        """Synchronous wrapper to parse and dispatch via anyio."""
        return anyio.run(self._handle_raw_async, raw)

    async def _handle_raw_async(self, raw: str | bytes | Json) -> Optional[Json]:
        # 1) PARSE: JSON or schema errors get id=None
        try:
            req = self._parse(raw)
        except JSONRPCError as exc:
            return self._error_response(None, exc)

        # 2) DISPATCH: preserve req.id on errors
        try:
            if req.id is None:
                # notification → invoke and drop result
                await self._invoke(req)
                return None
            result = await self._invoke(req)
            return Response(id=req.id, result=result).model_dump(exclude_none=True)
        except JSONRPCError as exc:
            return self._error_response(req.id, exc)

    def _parse(self, raw: str | bytes | Json) -> Request:
        if isinstance(raw, (str, bytes)):
            try:
                text = raw.decode() if isinstance(raw, bytes) else raw
                data = json.loads(text)
            except Exception as e:
                raise ParseError(f"Invalid JSON payload: {e}")
        else:
            data = raw
        try:
            return Request.model_validate(data)
        except Exception as e:
            raise InvalidRequestError(f"Request validation error: {e}")

    async def _invoke(self, req: Request) -> Any:
        """Invoke the registered handler, raising JSONRPCError or returning result."""
        if req.method not in self._methods:
            raise MethodNotFoundError(f"Method '{req.method}' not found")
        handler = self._methods[req.method]
        try:
            if iscoroutinefunction(handler):
                return await handler(req.method, req.params)
            return handler(req.method, req.params)
        except JSONRPCError:
            raise
        except Exception as e:
            logger.exception("Error in handler %s", req.method)
            raise InternalError(f"Internal error: {e}")

    @staticmethod
    def _error_response(req_id: Optional[Union[int, str]], exc: JSONRPCError) -> Json:
        """Format a JSON-RPC error response object."""
        return Response(id=req_id, error=exc.to_dict()).model_dump(exclude_none=True)

    # A2A-specific helpers

    @staticmethod
    def task_not_found(task_id: str) -> TaskNotFoundError:
        """Helper to create a TaskNotFoundError with the task ID in data."""
        return TaskNotFoundError("Task not found", data={"id": task_id})

    @staticmethod
    def task_not_cancelable(task_id: str) -> TaskNotCancelableError:
        """Helper to create a TaskNotCancelableError with the task ID in data."""
        return TaskNotCancelableError("Task cannot be canceled", data={"id": task_id})

    @staticmethod
    def push_notifications_not_supported() -> PushNotificationsNotSupportedError:
        """Helper to create a PushNotificationsNotSupportedError."""
        return PushNotificationsNotSupportedError("Push notification is not supported")

    @staticmethod
    def unsupported_operation(op: str) -> UnsupportedOperationError:
        """Helper to create an UnsupportedOperationError with the operation in data."""
        return UnsupportedOperationError("This operation is not supported", data={"operation": op})