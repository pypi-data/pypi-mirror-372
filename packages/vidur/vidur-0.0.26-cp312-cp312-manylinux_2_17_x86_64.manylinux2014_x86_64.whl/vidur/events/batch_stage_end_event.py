from typing import List, Union

from vidur.entities import Batch, BatchStage, KVParallelBatch, KVParallelBatchStage
from vidur.events import BaseEvent
from vidur.logger import init_logger
from vidur.metrics import MetricsStore
from vidur.scheduler import BaseGlobalScheduler
from vidur.types import EventType, ReplicaId

logger = init_logger(__name__)


class BatchStageEndEvent(BaseEvent):
    def __init__(
        self,
        time: float,
        replica_id: ReplicaId,
        stage_id: int,
        is_last_stage: bool,
        batch: Union[Batch, KVParallelBatch],
        batch_stage: Union[BatchStage, KVParallelBatchStage],
    ):
        super().__init__(time, EventType.BATCH_STAGE_END)

        self._replica_id = replica_id
        self._stage_id = stage_id
        self._is_last_stage = is_last_stage

        self._batch = batch
        self._batch_stage = batch_stage

    def handle_event(
        self, scheduler: BaseGlobalScheduler, metrics_store: MetricsStore
    ) -> List[BaseEvent]:
        from vidur.events.batch_end_event import BatchEndEvent
        from vidur.events.batch_stage_arrival_event import BatchStageArrivalEvent
        from vidur.events.replica_schedule_event import ReplicaScheduleEvent
        from vidur.events.replica_stage_schedule_event import ReplicaStageScheduleEvent

        self._batch_stage.on_stage_end(self.time)
        scheduler.get_replica_stage_scheduler(
            self._replica_id, self._stage_id
        ).on_stage_end()
        scheduler.get_replica_scheduler(self._replica_id).on_stage_end(
            self._stage_id, self._batch_stage
        )
        metrics_store.on_batch_stage_end(
            self.time,
            self._batch_stage,
            self._replica_id,
            self._stage_id,
        )

        next_events = [
            ReplicaStageScheduleEvent(
                self.time,
                self._replica_id,
                self._stage_id,
            ),
        ]

        if self._is_last_stage:
            next_events += [BatchEndEvent(self.time, self._replica_id, self._batch)]
        else:
            # schedule the next stage for the current batch if sequence pipeline parallel is not enabled
            next_events += [
                BatchStageArrivalEvent(
                    self.time,
                    self._replica_id,
                    self._stage_id + 1,
                    self._batch,
                )
            ]

        if self._stage_id == 0:
            next_events += [ReplicaScheduleEvent(self.time, self._replica_id)]

        return next_events

    def to_dict(self):
        return {
            "time": self.time,
            "event_type": self.event_type,
            "replica_id": self._replica_id,
            "stage_id": self._stage_id,
            "batch_id": self._batch.id,
            "batch_stage_id": self._batch_stage.id,
            "is_last_stage": self._is_last_stage,
        }

    def to_chrome_trace_events(self) -> dict:
        return self._batch_stage.to_chrome_trace_events(self.time)
