import httpx
from typing import Any, Final
from httpx import Limits
from jsonschema import validate, ValidationError as JsonSchemaValidationError
from websockets.asyncio.client import connect, ClientConnection
import asyncio
import json
from loguru import logger
from adaptive_harmony.core.reward_client.websocket_utils import ResponseAccumulator
from adaptive_harmony.core.reward_client.reward_types import (
    MetadataValidationResponse,
    Request,
    Response,
    ServerInfo,
    Turn,
)

SCORE_PATH: Final = "/score"
INFO_PATH: Final = "/info"
METADATA_SCHEMA_PATH: Final = "/metadata_schema"


async def read_task(client: ClientConnection, responses: dict[int, Response | asyncio.Event]):
    response_accumulators: dict[int, ResponseAccumulator] = {}
    while True:
        try:
            msg = await client.recv()
            obj = json.loads(msg)
            id = obj["id"]
            if total_num_chunks := obj.get("total_num_chunks"):
                assert id not in response_accumulators
                response_accumulators[id] = ResponseAccumulator(total_num_chunks)
            else:
                assert (acc := response_accumulators.get(id))
                acc.add_chunk(obj["chunk"])
                if acc.is_complete():
                    del response_accumulators[id]
                    response = Response.model_validate_json(acc.get_full_data())  # type: ignore
                    # sanity check
                    assert response.id == id
                    event: asyncio.Event = responses.pop(id)  # type: ignore
                    responses[id] = response
                    event.set()
        except Exception as e:
            logger.error(f"{e}")
            break


class RewardClient:
    def __init__(self, base_url: str, max_connections: int = 32, timeout: float | None = None):
        self.base_url = base_url.removeprefix("http://").removeprefix("https://")
        self._client = httpx.AsyncClient(
            headers=dict(),
            base_url=f"http://{self.base_url}",
            timeout=timeout,
            limits=Limits(max_connections=max_connections),
        )
        self._metadata_json_schema: None | dict[str, Any] = None
        self.use_websocket = False
        self.max_connections = max_connections

    async def setup(self):
        await self.connect_websocket()

    async def connect_websocket(self):
        self.use_websocket = True
        self.ws_client: ClientConnection = await connect(f"ws://{self.base_url}/ws", ping_timeout=None)
        self.ws_responses: dict[int, Response | asyncio.Event] = dict()
        logger.info("Spawning_read_task")
        self.read_task = asyncio.create_task(read_task(self.ws_client, self.ws_responses))
        self.request_id = 0
        # no need to blast 2x more than the amount of workers
        self.semaphore = asyncio.Semaphore(self.max_connections)
        return self

    async def drop_websocket(self):
        assert self.use_websocket
        logger.info("Cancelling_read_task")
        self.read_task.cancel()
        await self.ws_client.close()

    async def _post(self, path: str, data: dict) -> httpx.Response:
        response = await self._client.post(path, json=data)
        response.raise_for_status()
        return response

    async def _ws_post(self, req: Request) -> Response:
        async with self.semaphore:
            request_id = self.request_id
            self.request_id += 1
            req.id = request_id
            event = asyncio.Event()
            self.ws_responses[request_id] = event
            await self.ws_client.send(req.model_dump_json())
            await event.wait()
            response: Response = self.ws_responses.pop(request_id)  # type: ignore
            assert response.id == request_id
            return response

    async def score(self, req: Request) -> Response:
        if not self.use_websocket:
            response = await self._post(SCORE_PATH, req.model_dump())
            return Response(**response.json())
        else:
            return await self._ws_post(req)

    async def validate_metadata(self, metadata: dict[Any, Any]):
        if self._metadata_json_schema is None:
            response = await self._client.get(METADATA_SCHEMA_PATH)
            self._metadata_json_schema = response.json()

        try:
            validate(instance=metadata, schema=self._metadata_json_schema)  # type: ignore
            return MetadataValidationResponse(is_valid=True)
        except JsonSchemaValidationError as e:
            return MetadataValidationResponse(is_valid=False, error_message=str(e))

    async def info(self) -> ServerInfo:
        response = await self._client.get(INFO_PATH)
        response.raise_for_status()
        return ServerInfo(**response.json())

    def blocking_info(self) -> ServerInfo:
        return ServerInfo(**httpx.get(self._client.base_url.join(INFO_PATH), timeout=self._client.timeout).json())


async def main():
    # client = RewardClient("0.0.0.0:50056")
    client = await RewardClient("0.0.0.0:50056").connect_websocket()
    tasks = []
    for _ in range(1024):
        task = client.score(Request(turns=[Turn(role="assistant", content="hello")]))
        tasks.append(task)
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
