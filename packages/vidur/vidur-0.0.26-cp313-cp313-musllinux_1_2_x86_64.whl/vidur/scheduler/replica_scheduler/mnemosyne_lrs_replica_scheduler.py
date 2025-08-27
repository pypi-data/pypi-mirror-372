from typing import Any, List, Tuple

from vidur.entities import Request
from vidur.logger import init_logger
from vidur.scheduler.replica_scheduler.mnemosyne_edf_replica_scheduler import (
    MnemosyneEDFReplicaScheduler,
)

logger = init_logger(__name__)


class MnemosyneLRSReplicaScheduler(MnemosyneEDFReplicaScheduler):

    def _get_remaining_slack_fraction(self, time: float, request: Request) -> float:
        remaining_prefill_time = self._prefill_time_calculator.get_prefill_time(
            request.num_prefill_tokens,
            self._get_num_processed_tokens(request),
        )
        slack = request.deadline - time - remaining_prefill_time
        return slack / request.deadline_time

    def _sort_request_queue(
        self, time: float, request_queue: List[Tuple[Any, Request]]
    ) -> None:
        request_queue.sort(key=lambda x: self._get_remaining_slack_fraction(time, x[1]))
