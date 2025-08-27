from sklearn.ensemble import RandomForestRegressor

from vidur.config import (
    CacheConfig,
    RandomForrestExecutionTimePredictorConfig,
    ReplicaConfig,
)
from vidur.entities import Batch
from vidur.execution_time_predictor.sklearn_execution_time_predictor import (
    SklearnExecutionTimePredictor,
)


class RandomForrestExecutionTimePredictor(SklearnExecutionTimePredictor):
    def __init__(
        self,
        predictor_config: RandomForrestExecutionTimePredictorConfig,
        replica_config: ReplicaConfig,
        cache_config: CacheConfig,
    ) -> None:
        # will trigger model training
        super().__init__(
            predictor_config=predictor_config,
            replica_config=replica_config,
            cache_config=cache_config,
        )

    def _get_grid_search_params(self):
        return {
            "n_estimators": self._config.num_estimators,
            "max_depth": self._config.max_depth,
            "min_samples_split": self._config.min_samples_split,
        }

    def _get_estimator(self):
        return RandomForestRegressor()

    def _get_kv_parallel_communication_time(self, batch: Batch) -> float:
        return super()._get_kv_parallel_communication_time(batch)
