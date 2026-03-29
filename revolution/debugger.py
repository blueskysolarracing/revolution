import asyncio
import dataclasses
import json
import math
import threading
from dataclasses import dataclass, fields
from logging import getLogger
from typing import Any, ClassVar

import websockets

from revolution.application import Application
from revolution.environment import Endpoint
from revolution.worker import Worker

_logger = getLogger(__name__)

_DEBUGGER_HOST = '0.0.0.0'
_DEBUGGER_PORT = 8765
_DEBUGGER_INTERVAL = 0.1  # seconds between WebSocket broadcasts


def _serialize_contexts(ctx: Any) -> dict[str, Any]:
    """
    Serialize a Contexts instance to a JSON-safe dict.
    """
    result: dict[str, Any] = {}

    # Dataclass fields (excludes @property)
    for f in fields(ctx):
        value = getattr(ctx, f.name)
        result[f.name] = _coerce(value)

    # Computed @property fields defined directly on the Contexts class
    for name, obj in vars(type(ctx)).items():
        if isinstance(obj, property) and name not in result:
            try:
                result[name] = _coerce(getattr(ctx, name))
            except Exception:  # noqa: BLE001
                result[name] = None

    return result


def _coerce(value: Any) -> Any:
    """Recursively convert a value to something json.dumps can handle."""
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return None if math.isinf(value) or math.isnan(value) else value
    if isinstance(value, dict):
        return {str(k): _coerce(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_coerce(v) for v in value]
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return _serialize_contexts(value)
    # Enums, custom objects — fall back to their string name/value
    if hasattr(value, 'value'):
        return value.value
    return str(value)


@dataclass
class Debugger(Application):
    """WebSocket server that streams the full Contexts snapshot to clients.

    Conforms to the Application lifecycle:
      _setup()    → starts background Worker thread running the asyncio server
      _teardown() → joins the Worker thread
    """

    endpoint: ClassVar[Endpoint] = Endpoint.DEBUGGER

    # ------------------------------------------------------------------
    # Application lifecycle hooks
    # ------------------------------------------------------------------

    def _setup(self) -> None:
        super()._setup()

        self._debugger_worker = Worker(target=self._run_server, daemon=True)
        self._debugger_worker.start()

    def _teardown(self) -> None:
        self._debugger_worker.join()

    # ------------------------------------------------------------------
    # Server implementation
    # ------------------------------------------------------------------

    def _run_server(self) -> None:
        """Entry point for the Worker thread.  Runs the asyncio event loop."""
        asyncio.run(self._serve())

    async def _serve(self) -> None:
        async with websockets.serve(self._handler, _DEBUGGER_HOST, _DEBUGGER_PORT):
            _logger.info(
                'Debugger WebSocket server running on '
                f'ws://{_DEBUGGER_HOST}:{_DEBUGGER_PORT}'
            )
            # Keep the server alive until the stoppage event is set.
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._stoppage.wait)

    async def _handler(self, websocket: Any) -> None:
        """Broadcast the full Contexts snapshot to one connected client."""
        _logger.info('Debugger client connected: %s', websocket.remote_address)

        try:
            while not self._stoppage.is_set():
                with self.environment.contexts() as ctx:
                    snapshot = _serialize_contexts(ctx)

                payload = json.dumps(snapshot)
                await websocket.send(payload)
                await asyncio.sleep(_DEBUGGER_INTERVAL)

        except websockets.exceptions.ConnectionClosed:
            _logger.info(
                'Debugger client disconnected: %s', websocket.remote_address
            )
        except Exception:
            _logger.exception('Unexpected error in debugger WebSocket handler')
