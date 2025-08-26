from adaptive_harmony.adaptive_harmony import HarmonyClient
from adaptive_harmony.graders.base_grader import Grader, Grade
from adaptive_harmony.core.reward_client.client import RewardClient, Turn, Request
from adaptive_harmony import StringThread


class RewardServerGrader(Grader):

    def __init__(self, grader_key: str, grader_id: str, reward_server_ip: str):
        super().__init__(grader_key)
        self.reward_client = RewardClient(reward_server_ip)
        self.grader_id_or_key = grader_id or grader_key

    async def setup(self):
        await self.reward_client.setup()

    async def teardown(self):
        await self.reward_client.drop_websocket()

    async def grade(self, sample: StringThread) -> Grade:
        response = await self.reward_client.score(
            Request(
                turns=[Turn(content=turn.content, role=turn.role) for turn in sample.turns()],
                metadata=sample.metadata,
            )
        )
        return Grade(value=response.reward, grader_key=self.grader_id_or_key, reasoning=response.metadata.get("reason"))
