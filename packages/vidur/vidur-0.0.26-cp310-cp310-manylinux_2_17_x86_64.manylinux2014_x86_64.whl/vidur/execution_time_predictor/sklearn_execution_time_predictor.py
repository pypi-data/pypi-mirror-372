import hashlib
import json
import os
import pickle
from abc import abstractmethod
from enum import Enum
from itertools import product
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from fasteners import InterProcessReaderWriterLock
from huggingface_hub import snapshot_download
from sklearn.base import BaseEstimator
from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV

from vidur._native.config import (
    ExecutionTimePredictorConfig as ExecutionTimePredictorConfigC,
)
from vidur._native.config import ModelConfig as ModelConfigC
from vidur._native.config import ReplicaConfig as ReplicaConfigC
from vidur._native.execution_time_predictor import (
    ExecutionTimePredictor as ExecutionTimePredictorC,
)
from vidur.config import BaseExecutionTimePredictorConfig, CacheConfig, ReplicaConfig
from vidur.entities import Batch
from vidur.execution_time_predictor.base_execution_time_predictor import (
    BaseExecutionTimePredictor,
)
from vidur.logger import init_logger
from vidur.utils import sanitize_name
from vidur.utils.hf_dataset_utils import upload_dataset
from vidur.utils.parallel import parallel_map

logger = init_logger(__name__)


class ModelType(Enum):
    COMPUTE = "compute"
    NETWORK = "network"


def _store_prediction_file(file_path: str, predictions: Dict[Tuple, float]) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df = pd.DataFrame(
        [(*k, v) for k, v in predictions.items()],
        columns=[f"X_{i}" for i in range(len(next(iter(predictions))))]
        + ["prediction"],
    )
    df.to_csv(file_path, index=False, compression="xz")


def _load_prediction_file(file_path: str) -> Dict[Tuple, float]:
    """
    Load with tuple keys
    """
    df = pd.read_csv(file_path)
    pred_col = df.pop("prediction")
    return {tuple(row): pred for row, pred in zip(df.values, pred_col)}


class SklearnExecutionTimePredictor(BaseExecutionTimePredictor):
    def __init__(
        self,
        predictor_config: BaseExecutionTimePredictorConfig,
        replica_config: ReplicaConfig,
        cache_config: CacheConfig,
    ) -> None:
        super().__init__(
            predictor_config=predictor_config,
            replica_config=replica_config,
            cache_config=cache_config,
        )
        os.makedirs(self._cache_dir, exist_ok=True)

        # These overheads are only for GQA models
        self._attention_decode_batching_overhead_fraction = (
            (self._config.attention_decode_batching_overhead_fraction)
            if self._model_config.num_q_heads > self._model_config.num_kv_heads
            else 0
        )
        # TODO(amey): this won't work for orca scheduler
        self._max_tokens = self._config.prediction_max_tokens_per_request

        num_workers = (
            self._replica_config.num_pipeline_stages
            * self._replica_config.tensor_parallel_size
        )
        devices_per_node = self._replica_config.node_config.num_devices_per_node
        assert (
            num_workers < devices_per_node or num_workers % devices_per_node == 0
        ), "Number of workers should be less than devices per node or a multiple of devices per node"

        self._is_multi_node = num_workers > devices_per_node

        loaded_predictions_from_hf = False
        try:
            self._predictions = self._load_predictions_from_hf()
            loaded_predictions_from_hf = True
        except Exception as e:
            logger.error(f"Failed to load predictions from HF: {e}")

        if not loaded_predictions_from_hf:
            models = self._train_models()
            self._predictions = self._predict_from_models(models)

            if self._config.upload_predictions and not self._config.no_cache:
                assert self._config.prediction_hf_org is not None
                assert self._config.prediction_hf_collection is not None
                self._upload_predictions_to_hf()

        if self._config.use_native_execution_time_predictor:
            self._native_execution_time_predictor = (
                self._init_native_execution_time_predictor()
            )

    def _init_native_execution_time_predictor(self) -> None:
        predictor_config = ExecutionTimePredictorConfigC(
            kv_cache_prediction_granularity=self._config.kv_cache_prediction_granularity,
            prediction_max_prefill_chunk_size=self._config.prediction_max_prefill_chunk_size,
            prediction_max_batch_size=self._config.prediction_max_batch_size,
            prediction_max_tokens_per_request=self._config.prediction_max_tokens_per_request,
            attention_decode_batching_overhead_fraction=self._config.attention_decode_batching_overhead_fraction,
            nccl_cpu_launch_overhead_ms=self._config.nccl_cpu_launch_overhead_ms,
            nccl_cpu_skew_overhead_per_device_ms=self._config.nccl_cpu_skew_overhead_per_device_ms,
            use_native_execution_time_predictor=self._config.use_native_execution_time_predictor,
            disable_kvp_communication=self._config.disable_kvp_communication,
            cache_dir=self._config.cache_dir,
        )

        replica_config = ReplicaConfigC(
            num_pipeline_stages=self._replica_config.num_pipeline_stages,
            tensor_parallel_size=self._replica_config.tensor_parallel_size,
            kv_parallel_size=self._replica_config.kv_parallel_size,
        )

        model_config = ModelConfigC(
            num_layers=self._replica_config.model_config.num_layers,
            num_q_heads=self._replica_config.model_config.num_q_heads,
            num_kv_heads=self._replica_config.model_config.num_kv_heads,
            embedding_dim=self._replica_config.model_config.embedding_dim,
            mlp_hidden_dim=self._replica_config.model_config.mlp_hidden_dim,
            max_model_len=self._replica_config.model_config.max_model_len,
            use_gated_mlp=self._replica_config.model_config.use_gated_mlp,
            use_bias=self._replica_config.model_config.use_bias,
            use_qkv_bias=self._replica_config.model_config.use_qkv_bias,
            post_attn_norm=self._replica_config.model_config.post_attn_norm,
            vocab_size=self._replica_config.model_config.vocab_size,
        )

        prediction_ops = []
        prediction_keys = []
        prediction_values = []

        for prediction_op, prediction_dict in self._predictions.items():
            prediction_ops.append(prediction_op)
            prediction_keys.append([])
            prediction_values.append([])
            for key, value in prediction_dict.items():
                if len(key) == 1:
                    prediction_keys[-1].append((int(key[0]), -1))
                elif len(key) == 2:
                    prediction_keys[-1].append((int(key[0]), int(key[1])))
                else:
                    raise Exception(f"Key has more than 2 dimensions: {type(key)}")
                prediction_values[-1].append(value)

        native_execution_time_predictor = ExecutionTimePredictorC(
            config=predictor_config,
            replica_config=replica_config,
            model_config=model_config,
            prediction_keys=prediction_keys,
            prediction_values=prediction_values,
            prediction_ops=prediction_ops,
            hash=self.get_hash(),
        )

        return native_execution_time_predictor

    def _get_input_files(self) -> Tuple[str, str, str, str, str]:
        # Download the compute and network profile dataset from the huggingface datasets
        # specified in the config into cache directory
        compute_dataset_path = snapshot_download(
            repo_id=self._config.model_profiling_dataset,
            repo_type="dataset",
            cache_dir=f"{self._cache_dir}/profiling_data/compute/",
        )

        logger.info(f"🔽 Downloaded compute data to: {compute_dataset_path}")

        compute_dataset_config = json.load(
            open(f"{compute_dataset_path}/config.json", "r")
        )

        assert compute_dataset_config["model"] == self._replica_config.model_name
        assert compute_dataset_config["device_sku"] == self._replica_config.device

        network_dataset_path = snapshot_download(
            repo_id=self._config.network_profiling_dataset,
            repo_type="dataset",
            cache_dir=f"{self._cache_dir}/profiling_data/network/",
        )

        logger.info(f"🔽 Downloaded network data to: {network_dataset_path}")

        network_dataset_config = json.load(
            open(f"{network_dataset_path}/config.json", "r")
        )

        assert network_dataset_config["sku"] == self._replica_config.network_device

        return (
            f"{compute_dataset_path}/mlp.csv.xz",
            f"{compute_dataset_path}/attention.csv.xz",
            f"{network_dataset_path}/all_reduce.csv.xz",
            f"{network_dataset_path}/send_recv.csv.xz",
        )

    def _load_compute_df(self, file_path: str) -> pd.DataFrame:
        df = self._read_input_file(file_path)
        df = df.drop_duplicates()

        logger.debug(f"Length of complete compute df: {len(df)} {file_path}")
        logger.debug(f"num_q_heads: {self._model_config.num_q_heads}")
        logger.debug(f"embedding_dim: {self._model_config.embedding_dim}")
        logger.debug(f"mlp_hidden_dim: {self._model_config.mlp_hidden_dim}")
        logger.debug(f"use_gated_mlp: {self._model_config.use_gated_mlp}")
        logger.debug(f"vocab_size: {self._model_config.vocab_size}")
        logger.debug(
            f"num_tensor_parallel_workers: {self._replica_config.tensor_parallel_size}"
        )

        if (
            self._replica_config.tensor_parallel_size
            not in df["num_tensor_parallel_workers"].unique()
        ):
            raise Exception(
                f"Tensor parallel size {self._replica_config.tensor_parallel_size} not found in profile data: {file_path}\nAvailable TP sizes include:",
                df["num_tensor_parallel_workers"].unique(),
            )

        df = df[
            (df["n_head"] == self._model_config.num_q_heads)
            & (df["n_kv_head"] == self._model_config.num_kv_heads)
            & (df["n_embd"] == self._model_config.embedding_dim)
            & (df["n_expanded_embd"] == self._model_config.mlp_hidden_dim)
            & (df["use_gated_mlp"] == self._model_config.use_gated_mlp)
            & (df["vocab_size"] == self._model_config.vocab_size)
            & (
                df["num_tensor_parallel_workers"]
                == self._replica_config.tensor_parallel_size
            )
        ]

        for column in [
            "time_stats.post_attention_layernorm.median",
            "time_stats.add.median",
            "time_stats.input_layernorm.median",
        ]:
            if column not in df.columns:
                df[column] = 0
            else:
                df.fillna({column: 0}, inplace=True)
        return df

    def _load_attention_df(self, file_path: str) -> pd.DataFrame:
        df = pd.read_csv(file_path)
        df = df.drop_duplicates()

        for column in [
            "time_stats.attn_kv_cache_save.median",
        ]:
            if column not in df.columns:
                df[column] = 0
            else:
                df.fillna({column: 0}, inplace=True)

        if (
            self._replica_config.tensor_parallel_size
            not in df["num_tensor_parallel_workers"].unique()
        ):
            raise Exception(
                f"Tensor parallel size {self._replica_config.tensor_parallel_size} not found in profile data: {file_path}\nAvailable TP sizes include:",
                df["num_tensor_parallel_workers"].unique(),
            )

        return df[
            (df["n_embd"] == self._model_config.embedding_dim)
            & (df["n_q_head"] == self._model_config.num_q_heads)
            & (df["n_kv_head"] == self._model_config.num_kv_heads)
            & (df["block_size"] == self._block_size)
            & (
                df["num_tensor_parallel_workers"]
                == self._replica_config.tensor_parallel_size
            )
        ]

    def _load_all_reduce_df(self, file_path: str) -> pd.DataFrame:
        df = self._read_input_file(file_path)

        if self._replica_config.tensor_parallel_size not in df["num_workers"].unique():
            raise Exception(
                f"Tensor parallel size {self._replica_config.tensor_parallel_size} not found in profile data: {file_path}\nAvailable TP sizes include:",
                df["num_workers"].unique(),
            )

        return df[
            (df["num_workers"] == self._replica_config.tensor_parallel_size)
            & (df["devices_per_node"] == self._replica_config.tensor_parallel_size)
            & (df["collective"] == "all_reduce")
        ]

    def _load_all_reduce_kvp_df(self, file_path: str) -> pd.DataFrame:
        df = self._read_input_file(file_path)
        # TODO(amey): We are assuming that KVP workers are always going to be staggered
        return df[(df["devices_per_node"] == 1) & (df["collective"] == "all_reduce")]

    def _load_send_recv_df(self, file_path: str) -> pd.DataFrame:
        # TODO(Amey): We are making a simplifying assumption here that if
        # we go cross node in the model, pp communication is going to happen
        # over inter-node network. This is not always true of course.
        if self._is_multi_node:
            devices_per_node = 1
        else:
            devices_per_node = 2

        df = self._read_input_file(file_path)
        filtered_df = df[
            (df["collective"] == "send_recv")
            & (df["devices_per_node"] == devices_per_node)
        ]
        return filtered_df

    def _read_input_file(self, file_path: str) -> pd.DataFrame:
        df = pd.read_csv(file_path)
        df = df.drop_duplicates()
        return df

    def _get_compute_df_with_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df_with_derived_features = df.copy()
        return df_with_derived_features

    def _get_attention_df_with_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df_with_derived_features = df.copy()
        df_with_derived_features["num_tokens"] = df_with_derived_features[
            ["prefill_chunk_size", "batch_size"]
        ].max(axis=1)
        df_with_derived_features["is_decode"] = (
            df_with_derived_features["prefill_chunk_size"] == 0
        )
        df_with_derived_features["prefill_chunk_size_squared"] = (
            df_with_derived_features["prefill_chunk_size"] ** 2
        )
        return df_with_derived_features

    def _get_all_reduce_df_with_derived_features(
        self, df: pd.DataFrame
    ) -> pd.DataFrame:
        df_with_derived_features = df.copy()
        # convert bytes to num tokens
        # each token is of size 2 * h bytes
        df_with_derived_features["num_tokens"] = (
            df_with_derived_features["size"] / self._model_config.embedding_dim / 2
        )
        return df_with_derived_features

    def _get_send_recv_df_with_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df_with_derived_features = df.copy()
        df_with_derived_features["num_tokens"] = (
            df_with_derived_features["size"] / self._model_config.embedding_dim / 2
        )
        return df_with_derived_features

    def _get_compute_prediction_repo_id(self) -> str:
        model_hash = sanitize_name(self._get_hash(ModelType.COMPUTE))
        # Create standardized repo identifier
        org = sanitize_name(self._config.prediction_hf_org)
        collection = sanitize_name(self._config.prediction_hf_collection)
        profile_dataset_name = sanitize_name(self._config.model_profiling_dataset)

        repo_id = f"{org}/predictions-{collection}-{profile_dataset_name}-{model_hash}"

        return repo_id

    def _get_network_prediction_repo_id(self) -> str:
        model_hash = sanitize_name(self._get_hash(ModelType.NETWORK))
        # Create standardized repo identifier
        org = sanitize_name(self._config.prediction_hf_org)
        collection = sanitize_name(self._config.prediction_hf_collection)
        profile_dataset_name = sanitize_name(self._config.network_profiling_dataset)

        repo_id = f"{org}/predictions-{collection}-{profile_dataset_name}-{model_hash}"

        return repo_id

    def _load_predictions_from_hf(self) -> bool:
        compute_repo_id = self._get_compute_prediction_repo_id()
        network_repo_id = self._get_network_prediction_repo_id()

        # try to download the predictions from HF
        compute_output_dir = snapshot_download(
            repo_id=compute_repo_id,
            repo_type="dataset",
            cache_dir=f"{self._cache_dir}/hf_predictions/compute/",
        )
        logger.info(f"✅ Downloaded compute predictions from: {compute_repo_id}")

        network_output_dir = snapshot_download(
            repo_id=network_repo_id,
            repo_type="dataset",
            cache_dir=f"{self._cache_dir}/hf_predictions/network/",
        )
        logger.info(f"✅ Downloaded network predictions from: {network_repo_id}")

        all_prediction_files: List[str] = []
        model_names: List[str] = []
        for output_dir in [compute_output_dir, network_output_dir]:
            for file in os.listdir(output_dir):
                if file.endswith(".csv.xz"):
                    all_prediction_files.append(f"{output_dir}/{file}")
                    model_names.append(file.split(".")[0])

        predictions_dicts = parallel_map(_load_prediction_file, all_prediction_files)

        return {
            model_name: predictions
            for model_name, predictions in zip(model_names, predictions_dicts)
        }

    def _upload_predictions_to_hf(self) -> None:
        compute_repo_id = self._get_compute_prediction_repo_id()
        network_repo_id = self._get_network_prediction_repo_id()

        # Create config.json
        compute_model_config = {
            "schema_version": "1.0",
            **self._get_compute_model_config(),
        }

        upload_dataset(
            repo_id=compute_repo_id,
            config=compute_model_config,
            data_path=f"{self._cache_dir}/predictions/{self._get_hash(ModelType.COMPUTE)}",
            use_private_repo=self._config.upload_to_private_repo,
        )

        logger.info(f"✅ Published compute predictions to: {compute_repo_id}")

        network_model_config = {
            "schema_version": "1.0",
            **self._get_network_model_config(),
        }

        upload_dataset(
            repo_id=network_repo_id,
            config=network_model_config,
            data_path=f"{self._cache_dir}/predictions/{self._get_hash(ModelType.NETWORK)}",
            use_private_repo=self._config.upload_to_private_repo,
        )

        logger.info(f"✅ Published network predictions to: {network_repo_id}")

    @staticmethod
    def mean_absolute_percentage_error(y_true: np.array, y_pred: np.array) -> float:
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        # Handling the case where y_true is 0 separately to avoid division by zero
        zero_true_mask = y_true == 0
        non_zero_true_mask = ~zero_true_mask

        # For non-zero true values, calculate the absolute percentage error
        error = np.zeros_like(y_true, dtype=float)  # using float instead of np.float
        error[non_zero_true_mask] = (
            np.abs(
                (y_true[non_zero_true_mask] - y_pred[non_zero_true_mask])
                / y_true[non_zero_true_mask]
            )
            * 100
        )

        # For zero true values, if prediction is also 0, error is 0, else it is 100
        error[zero_true_mask] = np.where(y_pred[zero_true_mask] == 0, 0, 100)

        # Return the mean of the absolute percentage errors
        return np.mean(error)

    def _get_scorer(self) -> Any:
        return make_scorer(
            SklearnExecutionTimePredictor.mean_absolute_percentage_error,
            greater_is_better=False,
        )

    @abstractmethod
    def _get_grid_search_params(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _get_estimator(self) -> BaseEstimator:
        pass

    def _get_hash(self, model_type: ModelType) -> str:
        if model_type == ModelType.COMPUTE:
            config_str = str(self._get_compute_model_config())
        elif model_type == ModelType.NETWORK:
            config_str = str(self._get_network_model_config())
        else:
            raise ValueError(f"Invalid model type: {model_type}")

        return hashlib.md5(config_str.encode("utf-8")).hexdigest()[0:8]

    def _load_model_from_cache(self, model_name: str, model_hash: str) -> BaseEstimator:
        with InterProcessReaderWriterLock(
            f"{self._cache_dir}/{model_name}_{model_hash}_model_lock.file"
        ).read_lock():
            if self._config.no_cache:
                return
            # check if model is in cache
            cache_file = f"{self._cache_dir}/predictors/{model_hash}/{model_name}.pkl"

            if not os.path.exists(cache_file):
                return

            logger.debug(f"Found model {model_name} in cache")
            model = pickle.load(open(cache_file, "rb"))
            return model

    def _store_model_in_cache(
        self, model_name: str, model_hash: str, model: BaseEstimator
    ) -> None:
        with InterProcessReaderWriterLock(
            f"{self._cache_dir}/{model_hash}_model_lock.file"
        ).write_lock():
            # store model in cache
            cache_file = f"{self._cache_dir}/predictors/{model_hash}/{model_name}.pkl"
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            pickle.dump(model, open(cache_file, "wb"), protocol=pickle.HIGHEST_PROTOCOL)

    def _store_training_prediction_data(
        self,
        model_name: str,
        model_hash: str,
        df: pd.DataFrame,
        feature_cols: List[str],
        target_col: str,
        model: BaseEstimator,
    ) -> None:
        df = df.copy()

        # convert the df to list of tuples
        df["prediction"] = model.predict(df[feature_cols])

        # store the prediction data
        output_file = (
            f"{self._cache_dir}/training_predictions/{model_hash}/{model_name}.csv"
        )

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        df[feature_cols + [target_col, "prediction"]].to_csv(
            output_file,
            index=False,
        )

    def _train_model(
        self,
        model_name: str,
        model_type: ModelType,
        df: pd.DataFrame,
        feature_cols: List[str],
        target_col: str,
    ) -> BaseEstimator:
        if len(df) == 0:
            raise Exception(f"Training data for model {model_name} is empty")

        model_hash = self._get_hash(model_type)

        cached_model = self._load_model_from_cache(model_name, model_hash)
        if cached_model:
            return cached_model

        model = self._get_estimator()
        grid_search_params = self._get_grid_search_params()

        if len(df) < self._config.k_fold_cv_splits:
            cv = 2
        else:
            cv = self._config.k_fold_cv_splits

        grid_search = GridSearchCV(
            estimator=model,
            param_grid=grid_search_params,
            scoring=self._get_scorer(),
            cv=cv,
            n_jobs=self._config.num_training_job_threads,
        )

        # we don't create a train/test split, because we want to use all data for training
        # and we don't care about overfitting, because we only want to predict execution time within the same domain
        X, y = df[feature_cols], df[target_col]

        grid_search.fit(X, y)
        score = grid_search.score(X, y)

        logger.info(
            f"Trained model {model_name} and found best parameters: {grid_search.best_params_} "
            f"with mean absolute percentage error (MEAP) {-score}%"
        )

        self._store_model_in_cache(model_name, model_hash, grid_search.best_estimator_)

        self._store_training_prediction_data(
            model_name=model_name,
            model_hash=model_hash,
            df=df,
            feature_cols=feature_cols,
            target_col=target_col,
            model=grid_search.best_estimator_,
        )
        return grid_search.best_estimator_

    def _store_model_prediction_cache(
        self, model_name: str, model_hash: str, predictions: Dict[Tuple, float]
    ) -> None:
        with InterProcessReaderWriterLock(
            f"{self._cache_dir}/{model_hash}_prediction_lock.file"
        ).write_lock():
            cache_file = (
                f"{self._cache_dir}/predictions/{model_hash}/{model_name}.csv.xz"
            )
            _store_prediction_file(cache_file, predictions)

    def _load_model_prediction_cache(
        self, model_name: str, model_hash: str
    ) -> Dict[Tuple, float]:
        with InterProcessReaderWriterLock(
            f"{self._cache_dir}/{model_hash}_prediction_lock.file"
        ).read_lock():
            if self._config.no_cache:
                return {}
            cache_file = (
                f"{self._cache_dir}/predictions/{model_hash}/{model_name}.csv.xz"
            )

            if not os.path.exists(cache_file):
                return {}

            logger.debug(f"Found model {model_name} predictions in cache")

            return _load_prediction_file(cache_file)

    def _get_model_prediction(
        self,
        model_name: str,
        model_type: ModelType,
        model: BaseEstimator,
        X: pd.DataFrame,
    ) -> Dict[Tuple, float]:
        X = X.copy()

        model_hash = self._get_hash(model_type)

        cached_predictions = self._load_model_prediction_cache(model_name, model_hash)
        if cached_predictions:
            return cached_predictions

        logger.info(f"Predicting execution time for model {model_name}")

        predictions_array = model.predict(X)

        # turn this into a dict, so we can store use it as a cache
        # the key is tuple for each row of X
        predictions = dict(zip([tuple(x) for x in X.values], predictions_array))

        self._store_model_prediction_cache(model_name, model_hash, predictions)

        return predictions

    def _train_general_models(
        self,
        compute_input_file: str,
        attention_input_file: str,
        all_reduce_input_file: str,
        send_recv_input_file: str,
    ) -> Dict[str, BaseEstimator]:

        compute_df = self._load_compute_df(compute_input_file)
        compute_df = self._get_compute_df_with_derived_features(compute_df)

        models = {}
        model_names = [
            "attn_pre_proj",
            "attn_post_proj",
            "mlp_up_proj",
            "mlp_down_proj",
            "mlp_act",
            "input_layernorm",
            "post_attention_layernorm",
            "attn_rope",
            "add",
        ]

        for model_name in model_names:
            logger.debug(
                f"Training model {model_name}, size of training data: {len(compute_df)}"
            )
            models[model_name] = self._train_model(
                model_name=model_name,
                model_type=ModelType.COMPUTE,
                df=compute_df,
                feature_cols=["num_tokens"],
                target_col=f"time_stats.{model_name}.median",
            )

        attention_df = self._load_attention_df(attention_input_file)
        attention_df = self._get_attention_df_with_derived_features(attention_df)

        model_names = [
            "attn_kv_cache_save",
        ]

        for model_name in model_names:
            models[model_name] = self._train_model(
                model_name=model_name,
                model_type=ModelType.COMPUTE,
                df=attention_df,
                feature_cols=["num_tokens"],
                target_col=f"time_stats.{model_name}.median",
            )

        if self._replica_config.num_pipeline_stages > 1:
            send_recv_df = self._load_send_recv_df(send_recv_input_file)
            send_recv_df = self._get_send_recv_df_with_derived_features(send_recv_df)

            models["send_recv"] = self._train_model(
                model_name="send_recv",
                model_type=ModelType.NETWORK,
                df=send_recv_df,
                feature_cols=["num_tokens"],
                target_col="time_stats.send_recv.median",
            )

        if self._replica_config.tensor_parallel_size > 1:
            all_reduce_df = self._load_all_reduce_df(all_reduce_input_file)
            all_reduce_df = self._get_all_reduce_df_with_derived_features(all_reduce_df)

            models["all_reduce"] = self._train_model(
                model_name="all_reduce",
                model_type=ModelType.NETWORK,
                df=all_reduce_df,
                feature_cols=["num_tokens"],
                target_col="time_stats.all_reduce.median",
            )

        if (
            self._replica_config.kv_parallel_size > 1
            and not self._config.disable_kvp_communication
        ):
            all_reduce_kvp_df = self._load_all_reduce_kvp_df(all_reduce_input_file)
            all_reduce_kvp_df = self._get_all_reduce_df_with_derived_features(
                all_reduce_kvp_df
            )

            models["all_reduce_kvp"] = self._train_model(
                model_name="all_reduce_kvp",
                model_type=ModelType.NETWORK,
                df=all_reduce_kvp_df,
                feature_cols=["num_tokens", "num_workers"],
                target_col="time_stats.all_reduce.median",
            )

        return models

    def _train_attention_layer_models(
        self, attention_input_file: str
    ) -> Dict[str, BaseEstimator]:
        attention_df = self._load_attention_df(attention_input_file)
        attention_df = self._get_attention_df_with_derived_features(attention_df)
        prefill_df = attention_df[~attention_df["is_decode"]]
        decode_df = attention_df[attention_df["is_decode"]]

        models = {}

        chunked_prefill_df = prefill_df[prefill_df["kv_cache_size"] > 0].copy()
        chunked_prefill_df["total_prefill_tokens"] = (
            chunked_prefill_df["kv_cache_size"]
            + chunked_prefill_df["prefill_chunk_size"]
        )

        models["attn_prefill"] = self._train_model(
            model_name="attn_prefill",
            model_type=ModelType.COMPUTE,
            df=prefill_df,
            feature_cols=["kv_cache_size", "prefill_chunk_size"],
            target_col="time_stats.attn_prefill.median",
        )

        models["attn_decode"] = self._train_model(
            model_name="attn_decode",
            model_type=ModelType.COMPUTE,
            df=decode_df,
            feature_cols=["batch_size", "kv_cache_size"],
            target_col="time_stats.attn_decode.median",
        )

        return models

    def _train_models(self) -> Dict[str, BaseEstimator]:
        (
            compute_input_file,
            attention_input_file,
            all_reduce_input_file,
            send_recv_input_file,
        ) = self._get_input_files()

        models = self._train_general_models(
            compute_input_file,
            attention_input_file,
            all_reduce_input_file,
            send_recv_input_file,
        )
        models.update(self._train_attention_layer_models(attention_input_file))

        return models

    def _predict_for_general_models(self, models: Dict[str, Any]) -> Dict[str, Any]:
        predictions = {}

        model_names = [
            "attn_pre_proj",
            "attn_post_proj",
            "mlp_up_proj",
            "mlp_down_proj",
            "mlp_act",
            "attn_rope",
            "attn_kv_cache_save",
            "input_layernorm",
            "post_attention_layernorm",
            "add",
        ]

        num_token_range = np.arange(1, self._max_tokens + 1)
        X = pd.DataFrame({"num_tokens": num_token_range})

        for model_name in model_names:
            model = models[model_name]
            predictions[model_name] = self._get_model_prediction(
                model_name, ModelType.COMPUTE, model, X
            )

        network_model_names = []
        if self._replica_config.num_pipeline_stages > 1:
            network_model_names.append("send_recv")

        if self._replica_config.tensor_parallel_size > 1:
            network_model_names.append("all_reduce")

        for model_name in network_model_names:
            model = models[model_name]
            predictions[model_name] = self._get_model_prediction(
                model_name, ModelType.NETWORK, model, X
            )

        if self._replica_config.kv_parallel_size > 1:
            # we need to iterate over all possible number of workers and tokens
            num_workers_range = np.arange(1, self._replica_config.kv_parallel_size + 1)
            num_token_range = np.arange(1, self._max_tokens + 1)

            X = pd.DataFrame(
                list(product(num_token_range, num_workers_range)),
                columns=["num_tokens", "num_workers"],
            )

            if not self._config.disable_kvp_communication:
                model = models["all_reduce_kvp"]
                predictions["all_reduce_kvp"] = self._get_model_prediction(
                    "all_reduce_kvp", ModelType.NETWORK, model, X
                )

        return predictions

    def _predict_for_attention_layer_models(
        self, models: Dict[str, Any]
    ) -> Dict[str, Any]:
        predictions = {}

        decode_batch_size_range = np.arange(
            1, self._config.prediction_max_batch_size + 1
        )
        decode_kv_cache_size_range = np.arange(
            0,
            self._config.prediction_max_tokens_per_request + 1,
            self._config.kv_cache_prediction_granularity,
        )
        decode_prefill_chunk_size_range = [0]
        decode_batch_size, decode_kv_cache_size, decode_prefill_chunk_size = zip(
            *product(
                decode_batch_size_range,
                decode_kv_cache_size_range,
                decode_prefill_chunk_size_range,
            )
        )

        prefill_batch_size_range = [1]
        prefill_kv_cache_size_range = np.arange(
            0,
            self._config.prediction_max_tokens_per_request + 1,
            self._config.kv_cache_prediction_granularity,
        )
        prefill_prefill_chunk_size_range = np.arange(
            32, self._config.prediction_max_prefill_chunk_size + 1, 32
        )
        prefill_batch_size, prefill_kv_cache_size, prefill_prefill_chunk_size = zip(
            *product(
                prefill_batch_size_range,
                prefill_kv_cache_size_range,
                prefill_prefill_chunk_size_range,
            )
        )

        attention_df = pd.DataFrame(
            {
                "batch_size": decode_batch_size + prefill_batch_size,
                "kv_cache_size": decode_kv_cache_size + prefill_kv_cache_size,
                "prefill_chunk_size": decode_prefill_chunk_size
                + prefill_prefill_chunk_size,
            }
        )

        attention_df["is_decode"] = attention_df["prefill_chunk_size"] == 0
        attention_df["num_tokens"] = attention_df[
            ["prefill_chunk_size", "batch_size"]
        ].max(axis=1)
        attention_df["prefill_chunk_size_squared"] = (
            attention_df["prefill_chunk_size"] ** 2
        )

        prefill_df = attention_df[~attention_df["is_decode"]]
        decode_df = attention_df[attention_df["is_decode"]]
        chunked_prefill_df = prefill_df[prefill_df["kv_cache_size"] > 0].copy()
        chunked_prefill_df["total_prefill_tokens"] = (
            chunked_prefill_df["kv_cache_size"]
            + chunked_prefill_df["prefill_chunk_size"]
        )

        predictions["attn_prefill"] = self._get_model_prediction(
            "attn_prefill",
            ModelType.COMPUTE,
            models["attn_prefill"],
            prefill_df[["kv_cache_size", "prefill_chunk_size"]],
        )

        predictions["attn_decode"] = self._get_model_prediction(
            "attn_decode",
            ModelType.COMPUTE,
            models["attn_decode"],
            decode_df[["batch_size", "kv_cache_size"]],
        )

        return predictions

    def _predict_from_models(self, models: Dict[str, Any]) -> Dict[str, Any]:
        predictions = self._predict_for_general_models(models)
        predictions.update(self._predict_for_attention_layer_models(models))

        return predictions

    def _get_batch_decode_attention_params(self, batch: Batch) -> Tuple[int, int]:
        if hasattr(batch, "_decode_params"):
            return batch._decode_params

        decode_kv_cache_sizes = []

        for num_q_tokens, num_kv_tokens in zip(batch.num_q_tokens, batch.num_kv_tokens):
            if num_q_tokens != 1:
                continue
            decode_kv_cache_sizes.append(num_kv_tokens)

        if not decode_kv_cache_sizes:
            batch._decode_params = (0, 0)
            return batch._decode_params

        decode_batch_size = len(decode_kv_cache_sizes)
        decode_avg_kv_cache_size = int(np.mean(decode_kv_cache_sizes))
        decode_avg_kv_cache_size = (
            (
                decode_avg_kv_cache_size
                + self._config.kv_cache_prediction_granularity
                - 1
            )
            // self._config.kv_cache_prediction_granularity
        ) * self._config.kv_cache_prediction_granularity

        batch._decode_params = (decode_batch_size, decode_avg_kv_cache_size)

        return batch._decode_params

    def _get_batch_prefill_attention_params(
        self, batch: Batch
    ) -> List[Tuple[int, int]]:
        if hasattr(batch, "_prefill_params"):
            return batch._prefill_params

        prefill_params = []

        for num_q_tokens, num_kv_tokens in zip(batch.num_q_tokens, batch.num_kv_tokens):
            if num_q_tokens == 1:
                continue

            num_kv_tokens = (
                (num_kv_tokens + self._config.kv_cache_prediction_granularity - 1)
                // self._config.kv_cache_prediction_granularity
            ) * self._config.kv_cache_prediction_granularity

            prefill_params.append((num_kv_tokens, num_q_tokens))

        batch._prefill_params = prefill_params

        return prefill_params

    def _get_attention_layer_pre_proj_execution_time(self, batch: Batch) -> float:
        return self._predictions["attn_pre_proj"][(batch._total_num_q_tokens_rounded,)]

    def _get_attention_layer_post_proj_execution_time(self, batch: Batch) -> float:
        return self._predictions["attn_post_proj"][(batch._total_num_q_tokens_rounded,)]

    def _get_mlp_layer_up_proj_execution_time(self, batch: Batch) -> float:
        return self._predictions["mlp_up_proj"][(batch._total_num_q_tokens_rounded,)]

    def _get_mlp_layer_down_proj_execution_time(self, batch: Batch) -> float:
        return self._predictions["mlp_down_proj"][(batch._total_num_q_tokens_rounded,)]

    def _get_mlp_layer_act_execution_time(self, batch: Batch) -> float:
        return self._predictions["mlp_act"][(batch._total_num_q_tokens_rounded,)]

    def _get_attn_norm_layer_act_execution_time(self, batch: Batch) -> float:
        return self._predictions["input_layernorm"][
            (batch._total_num_q_tokens_rounded,)
        ]

    def _get_mlp_norm_layer_act_execution_time(self, batch: Batch) -> float:
        if not self._model_config.post_attn_norm:
            return 0

        return self._predictions["post_attention_layernorm"][
            (batch._total_num_q_tokens_rounded,)
        ]

    def _get_add_layer_act_execution_time(self, batch: Batch) -> float:
        return self._predictions["add"][(batch._total_num_q_tokens_rounded,)]

    def _get_tensor_parallel_communication_time(self, batch: Batch) -> float:
        return (
            self._predictions["all_reduce"][(batch._total_num_q_tokens_rounded,)]
            + self._config.nccl_cpu_launch_overhead_ms
            + self._config.nccl_cpu_skew_overhead_per_device_ms
            * self._replica_config.tensor_parallel_size**1.25
        )

    def _get_pipeline_parallel_communication_time(self, batch: Batch) -> float:
        try:
            return self._predictions["send_recv"][(batch._total_num_q_tokens_rounded,)]
        except KeyError as e:
            logger.error(f"Failed to get send_recv prediction for batch {batch}")
            raise e

    def _get_attention_rope_execution_time(self, batch: Batch) -> float:
        return self._predictions["attn_rope"][(batch._total_num_q_tokens_rounded,)]

    def _get_attention_kv_cache_save_execution_time(self, batch: Batch) -> float:
        # don't use round up to the nearest multiple of 8 here, because we want to
        # predict the execution time for the exact number of tokens
        return self._predictions["attn_kv_cache_save"][(batch._total_num_q_tokens,)]

    def _get_attention_decode_execution_time(self, batch: Batch) -> float:
        (
            decode_batch_size,
            decode_avg_kv_cache_size,
        ) = self._get_batch_decode_attention_params(batch)
        if decode_batch_size == 0:
            return 0

        return self._predictions["attn_decode"][
            (decode_batch_size, decode_avg_kv_cache_size)
        ] * (
            1
            + self._attention_decode_batching_overhead_fraction
            * int(decode_batch_size > 1)
        )

    def _get_attention_prefill_execution_time(self, batch: Batch) -> float:
        prefill_params = self._get_batch_prefill_attention_params(batch)

        if len(prefill_params) == 0:
            return 0

        total_time = 0

        for kv_cache_size, prefill_chunk_size in prefill_params:
            prefill_chunk_size = ((prefill_chunk_size + 31) // 32) * 32
            total_time += self._predictions["attn_prefill"][
                (kv_cache_size, prefill_chunk_size)
            ]

        return total_time

    @abstractmethod
    def _get_kv_parallel_communication_time(self, batch: Batch) -> float:
        if not self._config.disable_kvp_communication:
            return 0

        total_comm_time = 0

        for num_q_tokens, num_groups in zip(
            batch.num_q_tokens, batch.num_active_kvp_groups
        ):
            if num_q_tokens == 0:
                continue

            # round up to the nearest multiple of 8
            num_q_tokens = (num_q_tokens + 7) // 8 * 8

            total_comm_time += (
                self._predictions["all_reduce_kvp"][(num_q_tokens, num_groups)]
                + self._config.nccl_cpu_launch_overhead_ms
                + self._config.nccl_cpu_skew_overhead_per_device_ms * num_groups**1.25
            )

        return total_comm_time

    def _get_compute_model_config(self) -> Dict[str, Any]:
        return {
            "model_provider": str(self._config.get_type()),
            "profiling_datasource": self._config.model_profiling_dataset,
            "num_tensor_parallel_workers": self._replica_config.tensor_parallel_size,
            "k_fold_cv_splits": self._config.k_fold_cv_splits,
            "block_size": self._block_size,
            "max_tokens": self._max_tokens,
            "prediction_max_prefill_chunk_size": self._config.prediction_max_prefill_chunk_size,
            "max_batch_size": self._config.prediction_max_batch_size,
        }

    def _get_network_model_config(self) -> Dict[str, Any]:
        return {
            "model_provider": str(self._config.get_type()),
            "profiling_datasource": self._config.network_profiling_dataset,
            "tensor_parallel_size": self._replica_config.tensor_parallel_size,
            "is_multi_node": self._is_multi_node,
            "max_tokens": self._max_tokens,
            "disable_kvp_communication": self._config.disable_kvp_communication,
        }

    def to_dict(self) -> dict:
        return {
            "model_provider": str(self._config.get_type()),
            "model_name": self._replica_config.model_name,
            "model_profiling_dataset": self._config.model_profiling_dataset,
            "network_profiling_dataset": self._config.network_profiling_dataset,
            "tensor_parallel_size": self._replica_config.tensor_parallel_size,
            "is_multi_node": self._is_multi_node,
            "k_fold_cv_splits": self._config.k_fold_cv_splits,
            "max_tokens": self._max_tokens,
            "block_size": self._block_size,
            "prediction_max_prefill_chunk_size": self._config.prediction_max_prefill_chunk_size,
            "max_batch_size": self._config.prediction_max_batch_size,
        }

    def get_hash(self) -> str:
        attributes = self.to_dict()
        return hashlib.md5(str(attributes).encode("utf-8")).hexdigest()[0:8]
