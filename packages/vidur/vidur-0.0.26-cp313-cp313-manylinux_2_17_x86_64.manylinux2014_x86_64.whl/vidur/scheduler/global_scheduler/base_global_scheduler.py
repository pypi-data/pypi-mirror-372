from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from vidur.config import SimulationConfig
from vidur.entities import Replica, Request
from vidur.execution_time_predictor import ExecutionTimePredictorRegistry
from vidur.logger import init_logger
from vidur.scheduler.replica_scheduler.replica_scheduler_registry import (
    ReplicaSchedulerRegistry,
)
from vidur.types import ReplicaSchedulerType
from vidur.types.replica_id import ReplicaId

logger = init_logger(__name__)


class BaseGlobalScheduler(ABC):
    def __init__(self, config: SimulationConfig, replicas: Dict[ReplicaId, Replica]):
        self._config = config
        self._replicas = replicas

        self._num_replicas = len(self._replicas)

        logger.info(f"Number of replicas: {self._num_replicas}")

        execution_time_predictor = ExecutionTimePredictorRegistry.get(
            config.execution_time_predictor_config.get_type(),
            predictor_config=config.execution_time_predictor_config,
            replica_config=config.cluster_config.replica_config,
            cache_config=config.cluster_config.cache_config,
        )
        self._replica_schedulers = {
            replica_id: ReplicaSchedulerRegistry.get(
                config.cluster_config.replica_scheduler_config.get_type(),
                replica_config=config.cluster_config.replica_config,
                replica_scheduler_config=config.cluster_config.replica_scheduler_config,
                cache_config=config.cluster_config.cache_config,
                request_generator_config=config.request_generator_config,
                replica=replica,
                num_stages=config.cluster_config.replica_config.num_pipeline_stages,
                execution_time_predictor=execution_time_predictor,
            )
            for replica_id, replica in replicas.items()
        }
        self._request_queue = []

    def sort_requests(self) -> None:
        self._request_queue.sort(key=lambda request: request._arrived_at)

    def add_request(self, request: Request) -> None:
        self._request_queue.append(request)

    def get_replica_scheduler(self, replica_id: ReplicaId):
        return self._replica_schedulers[replica_id]

    def get_replica_stage_scheduler(self, replica_id: ReplicaId, stage_id: int):
        return self._replica_schedulers[replica_id].get_replica_stage_scheduler(
            stage_id
        )

    def is_empty(self) -> bool:
        return len(self._request_queue) == 0 and all(
            replica_scheduler.is_empty()
            for replica_scheduler in self._replica_schedulers.values()
        )

    def get_pending_requests(self) -> List[Request]:
        return self._request_queue + sum(
            [
                replica_scheduler.get_pending_requests()
                for replica_scheduler in self._replica_schedulers.values()
            ],
            [],
        )

    @abstractmethod
    def schedule(self) -> List[Tuple[ReplicaId, Request]]:
        pass
