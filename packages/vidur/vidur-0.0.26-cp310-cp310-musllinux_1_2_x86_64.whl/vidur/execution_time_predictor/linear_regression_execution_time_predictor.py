from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

from vidur.config import (
    CacheConfig,
    LinearRegressionExecutionTimePredictorConfig,
    ReplicaConfig,
)
from vidur.execution_time_predictor.sklearn_execution_time_predictor import (
    SklearnExecutionTimePredictor,
)


class LinearRegressionExecutionTimePredictor(SklearnExecutionTimePredictor):
    def __init__(
        self,
        predictor_config: LinearRegressionExecutionTimePredictorConfig,
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
            "polynomialfeatures__degree": self._config.polynomial_degree,
            "polynomialfeatures__include_bias": self._config.polynomial_include_bias,
            "polynomialfeatures__interaction_only": self._config.polynomial_interaction_only,
            "linearregression__fit_intercept": self._config.fit_intercept,
        }

    def _get_estimator(self):
        return make_pipeline(PolynomialFeatures(), LinearRegression())
