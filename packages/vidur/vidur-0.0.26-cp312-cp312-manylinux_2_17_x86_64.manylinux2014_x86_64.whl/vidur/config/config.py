import json
import os
import sys
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from math import ceil
from typing import List, Optional

from vidur.config.base_poly_config import BasePolyConfig
from vidur.config.device_sku_config import BaseDeviceSKUConfig
from vidur.config.flat_dataclass import create_flat_dataclass
from vidur.config.model_config import BaseModelConfig
from vidur.config.node_sku_config import BaseNodeSKUConfig
from vidur.config.utils import dataclass_to_dict
from vidur.logger import init_logger
from vidur.types import (
    ExecutionTimePredictorType,
    GlobalSchedulerType,
    ReplicaSchedulerType,
    RequestGeneratorType,
    RequestIntervalGeneratorType,
    RequestLengthGeneratorType,
)

logger = init_logger(__name__)

ROOT_DIR = os.path.abspath(os.path.join(__file__, "../../../"))


@dataclass
class BaseRequestIntervalGeneratorConfig(BasePolyConfig):
    seed: int = field(
        default=42,
        metadata={"help": "Seed for the random number generator."},
    )


@dataclass
class BaseRequestLengthGeneratorConfig(BasePolyConfig):
    seed: int = field(
        default=42,
        metadata={"help": "Seed for the random number generator."},
    )
    max_tokens: int = field(
        default=4096,
        metadata={"help": "Maximum tokens."},
    )


@dataclass
class TraceRequestIntervalGeneratorConfig(BaseRequestIntervalGeneratorConfig):
    trace_file: str = field(
        default="data/processed_traces/AzureFunctionsInvocationTraceForTwoWeeksJan2021Processed.csv",
        metadata={"help": "Path to the trace request interval generator file."},
    )
    start_time: str = field(
        default="1970-01-04 12:00:00",
        metadata={"help": "Start time of the trace request interval generator."},
    )
    end_time: str = field(
        default="1970-01-04 15:00:00",
        metadata={"help": "End time of the trace request interval generator."},
    )
    time_scale_factor: float = field(
        default=1,
        metadata={
            "help": "Time scale factor for the trace request interval generator."
        },
    )

    @staticmethod
    def get_type():
        return RequestIntervalGeneratorType.TRACE


@dataclass
class PoissonRequestIntervalGeneratorConfig(BaseRequestIntervalGeneratorConfig):
    qps: float = field(
        default=10,
        metadata={"help": "Queries per second for Poisson Request Interval Generator."},
    )

    @staticmethod
    def get_type():
        return RequestIntervalGeneratorType.POISSON


@dataclass
class GammaRequestIntervalGeneratorConfig(BaseRequestIntervalGeneratorConfig):
    qps: float = field(
        default=0.2,
        metadata={"help": "Queries per second for Gamma Request Interval Generator."},
    )
    cv: float = field(
        default=0.5,
        metadata={
            "help": "Coefficient of variation for Gamma Request Interval Generator."
        },
    )

    @staticmethod
    def get_type():
        return RequestIntervalGeneratorType.GAMMA


@dataclass
class StaticRequestIntervalGeneratorConfig(BaseRequestIntervalGeneratorConfig):
    @staticmethod
    def get_type():
        return RequestIntervalGeneratorType.STATIC


@dataclass
class TraceRequestLengthGeneratorConfig(BaseRequestLengthGeneratorConfig):
    trace_file: str = field(
        default="data/processed_traces/sharegpt_8k_filtered_stats_llama2_tokenizer.csv",
        metadata={"help": "Path to the trace request length generator file."},
    )
    prefill_scale_factor: float = field(
        default=1,
        metadata={
            "help": "Prefill scale factor for the trace request length generator."
        },
    )
    decode_scale_factor: float = field(
        default=1,
        metadata={
            "help": "Decode scale factor for the trace request length generator."
        },
    )
    max_tokens: int = field(
        default=1024 * 1024,
        metadata={"help": "Maximum tokens for the trace request length generator."},
    )

    @staticmethod
    def get_type():
        return RequestLengthGeneratorType.TRACE


@dataclass
class ZipfRequestLengthGeneratorConfig(BaseRequestLengthGeneratorConfig):
    theta: float = field(
        default=0.6,
        metadata={"help": "Theta for Zipf Request Length Generator."},
    )
    scramble: bool = field(
        default=False,
        metadata={"help": "Scramble for Zipf Request Length Generator."},
    )
    min_tokens: int = field(
        default=1024,
        metadata={"help": "Minimum tokens for Zipf Request Length Generator."},
    )
    max_tokens: int = field(
        default=4096,
        metadata={"help": "Maximum tokens for Zipf Request Length Generator."},
    )
    prefill_to_decode_ratio: float = field(
        default=20.0,
        metadata={"help": "Prefill to decode ratio for Zipf Request Length Generator."},
    )

    @staticmethod
    def get_type():
        return RequestLengthGeneratorType.ZIPF


@dataclass
class UniformRequestLengthGeneratorConfig(BaseRequestLengthGeneratorConfig):
    min_tokens: int = field(
        default=1024,
        metadata={"help": "Minimum tokens for Uniform Request Length Generator."},
    )
    max_tokens: int = field(
        default=4096,
        metadata={"help": "Maximum tokens for Uniform Request Length Generator."},
    )
    prefill_to_decode_ratio: float = field(
        default=20.0,
        metadata={
            "help": "Prefill to decode ratio for Uniform Request Length Generator."
        },
    )

    @staticmethod
    def get_type():
        return RequestLengthGeneratorType.UNIFORM


@dataclass
class FixedRequestLengthGeneratorConfig(BaseRequestLengthGeneratorConfig):
    prefill_tokens: int = field(
        default=4 * 1024,
        metadata={"help": "Prefill tokens for Fixed Request Length Generator."},
    )
    decode_tokens: int = field(
        default=512,
        metadata={"help": "Decode tokens for Fixed Request Length Generator."},
    )

    @staticmethod
    def get_type():
        return RequestLengthGeneratorType.FIXED


@dataclass
class BaseRequestGeneratorConfig(BasePolyConfig):
    seed: int = field(
        default=42,
        metadata={"help": "Seed for the random number generator."},
    )
    max_tokens: int = field(
        default=4096,
        metadata={"help": "Maximum tokens."},
    )


@dataclass
class SyntheticRequestGeneratorConfig(BaseRequestGeneratorConfig):
    length_generator_config: BaseRequestLengthGeneratorConfig = field(
        default_factory=FixedRequestLengthGeneratorConfig,
        metadata={"help": "Length generator config for Synthetic Request Generator."},
    )
    interval_generator_config: BaseRequestIntervalGeneratorConfig = field(
        default_factory=StaticRequestIntervalGeneratorConfig,
        metadata={"help": "Interval generator config for Synthetic Request Generator."},
    )
    num_requests: Optional[int] = field(
        default=512,
        metadata={"help": "Number of requests for Synthetic Request Generator."},
    )
    duration: Optional[float] = field(
        default=None,
        metadata={"help": "Duration of the synthetic request generator."},
    )

    def __post_init__(self):
        self.max_tokens = self.length_generator_config.max_tokens

    @staticmethod
    def get_type():
        return RequestGeneratorType.SYNTHETIC


@dataclass
class TraceRequestGeneratorConfig(BaseRequestGeneratorConfig):
    trace_file: str = field(
        default="data/processed_traces/splitwise_conv.csv",
        metadata={"help": "Path to the trace request generator file."},
    )
    date: str = field(
        default="2023-08-21",
        metadata={"help": "Date for the trace request generator."},
    )
    prefill_scale_factor: float = field(
        default=0.3,
        metadata={"help": "Prefill scale factor for the trace request generator."},
    )
    decode_scale_factor: float = field(
        default=1,
        metadata={"help": "Decode scale factor for the trace request generator."},
    )
    time_scale_factor: float = field(
        default=0.04,
        metadata={"help": "Time scale factor for the trace request generator."},
    )
    max_tokens: int = field(
        default=4096,
        metadata={"help": "Maximum tokens for the trace request generator."},
    )

    @staticmethod
    def get_type():
        return RequestGeneratorType.TRACE_REPLAY


@dataclass
class BaseReplicaSchedulerConfig(BasePolyConfig):
    batch_size_cap: int = field(
        default=128,
        metadata={"help": "Maximum batch size cap."},
    )


@dataclass
class VllmSchedulerConfig(BaseReplicaSchedulerConfig):
    max_batched_tokens: int = field(
        default=None,
        metadata={"help": "Maximum batched tokens for vLLM."},
    )
    max_tokens_in_batch: int = field(
        default=4096,
        metadata={"help": "Maximum tokens in batch for vLLM."},
    )

    @staticmethod
    def get_type():
        return ReplicaSchedulerType.VLLM


@dataclass
class OrcaSchedulerConfig(BaseReplicaSchedulerConfig):

    @staticmethod
    def get_type():
        return ReplicaSchedulerType.ORCA


@dataclass
class SarathiSchedulerConfig(BaseReplicaSchedulerConfig):
    chunk_size: int = field(
        default=512,
        metadata={"help": "Chunk size for Sarathi."},
    )

    @staticmethod
    def get_type():
        return ReplicaSchedulerType.SARATHI


@dataclass
class MnemosyneFCFSFixedChunkSchedulerConfig(BaseReplicaSchedulerConfig):
    chunk_size: int = field(
        default=512,
        metadata={"help": "Chunk size for Sarathi."},
    )

    @staticmethod
    def get_type():
        return ReplicaSchedulerType.MNEMOSYNE_FCFS_FIXED_CHUNK


@dataclass
class MnemosyneFCFSSchedulerConfig(BaseReplicaSchedulerConfig):
    target_batch_time: float = field(
        default=0.05,
        metadata={"help": "Target batch time for Mnemosyne FCFS."},
    )

    @staticmethod
    def get_type():
        return ReplicaSchedulerType.MNEMOSYNE_FCFS


@dataclass
class MnemosyneEDFSchedulerConfig(BaseReplicaSchedulerConfig):
    target_batch_time: float = field(
        default=0.05,
        metadata={"help": "Target batch time for Mnemosyne EDF."},
    )
    deadline_multiplier: float = field(
        default=1.5,
        metadata={"help": "Deadline multiplier for Mnemosyne EDF."},
    )
    min_deadline: float = field(
        default=0.5,
        metadata={"help": "Minimum deadline for Mnemosyne EDF."},
    )

    @staticmethod
    def get_type():
        return ReplicaSchedulerType.MNEMOSYNE_EDF


@dataclass
class MnemosyneLRSSchedulerConfig(BaseReplicaSchedulerConfig):
    target_batch_time: float = field(
        default=0.05,
        metadata={"help": "Target batch time for Mnemosyne LRS."},
    )
    deadline_multiplier: float = field(
        default=1.5,
        metadata={"help": "Deadline multiplier for Mnemosyne LRS."},
    )
    min_deadline: float = field(
        default=0.5,
        metadata={"help": "Minimum deadline for Mnemosyne LRS."},
    )

    @staticmethod
    def get_type():
        return ReplicaSchedulerType.MNEMOSYNE_LRS


@dataclass
class MnemosyneSTSchedulerConfig(BaseReplicaSchedulerConfig):
    target_batch_time: float = field(
        default=0.05,
        metadata={"help": "Target batch time for Mnemosyne ST."},
    )
    deadline_multiplier: float = field(
        default=1.5,
        metadata={"help": "Deadline multiplier for Mnemosyne ST."},
    )
    min_deadline: float = field(
        default=0.5,
        metadata={"help": "Minimum deadline for Mnemosyne ST."},
    )
    long_request_kv_cache_len_threshold: float = field(
        default=256 * 1024,
        metadata={
            "help": "Minimum KV cache length to be categorized as a long request."
        },
    )

    @staticmethod
    def get_type():
        return ReplicaSchedulerType.MNEMOSYNE_ST


@dataclass
class MetricsConfig:
    """Metric configuration."""

    write_metrics: bool = field(
        default=True,
        metadata={"help": "Whether to write metrics."},
    )
    write_json_trace: bool = field(
        default=False,
        metadata={"help": "Whether to write json trace."},
    )
    wandb_project: Optional[str] = field(
        default=None,
        metadata={"help": "Weights & Biases project name."},
    )
    wandb_group: Optional[str] = field(
        default=None,
        metadata={"help": "Weights & Biases group name."},
    )
    wandb_run_name: Optional[str] = field(
        default=None,
        metadata={"help": "Weights & Biases run name."},
    )
    wandb_sweep_id: Optional[str] = field(
        default=None,
        metadata={"help": "Weights & Biases sweep id."},
    )
    wandb_run_id: Optional[str] = field(
        default=None,
        metadata={"help": "Weights & Biases run id."},
    )
    enable_chrome_trace: bool = field(
        default=True,
        metadata={"help": "Enable Chrome tracing."},
    )
    save_table_to_wandb: bool = field(
        default=False,
        metadata={"help": "Whether to save table to wandb."},
    )
    store_plots: bool = field(
        default=True,
        metadata={"help": "Whether to store plots."},
    )
    store_operation_metrics: bool = field(
        default=False,
        metadata={"help": "Whether to store operation metrics."},
    )
    store_token_completion_metrics: bool = field(
        default=False,
        metadata={"help": "Whether to store token completion metrics."},
    )
    store_request_metrics: bool = field(
        default=True,
        metadata={"help": "Whether to store request metrics."},
    )
    store_batch_metrics: bool = field(
        default=True,
        metadata={"help": "Whether to store batch metrics."},
    )
    store_utilization_metrics: bool = field(
        default=True,
        metadata={"help": "Whether to store utilization metrics."},
    )
    keep_individual_batch_metrics: bool = field(
        default=False,
        metadata={"help": "Whether to keep individual batch metrics."},
    )
    subsamples: Optional[int] = field(
        default=None,
        metadata={"help": "Subsamples."},
    )
    min_batch_index: Optional[int] = field(
        default=None,
        metadata={"help": "Minimum batch index."},
    )
    max_batch_index: Optional[int] = field(
        default=None,
        metadata={"help": "Maximum batch index."},
    )
    output_dir: str = field(
        default="simulator_output",
        metadata={"help": "Output directory."},
    )

    def __post_init__(self):
        self.output_dir = (
            f"{self.output_dir}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')}"
        )
        os.makedirs(self.output_dir, exist_ok=True)


@dataclass
class CacheConfig:
    block_size: int = field(
        default=16,
        metadata={"help": "Block size."},
    )
    num_blocks: Optional[int] = field(
        default=None,
        metadata={"help": "Number of blocks."},
    )
    watermark_blocks_fraction: float = field(
        default=0.01,
        metadata={"help": "Watermark blocks fraction."},
    )
    memory_margin_fraction: float = field(
        default=0.1,
        metadata={"help": "Memory margin fraction."},
    )
    enable_prefix_caching: bool = field(
        default=False,
        metadata={"help": "Enable prefix caching."},
    )
    prefix_caching_hash_algo: str = field(
        default="builtin",
        metadata={"help": "Prefix caching hash algorithm."},
    )
    num_preallocate_tokens: int = field(
        default=64,
        metadata={"help": "Number of preallocate tokens."},
    )
    enable_disk_caching: bool = field(
        default=False, metadata={"help": "Enable caching to disk."}
    )
    disk_num_blocks: int = field(
        default=sys.maxsize, metadata={"help": "Number of blocks in disk cache."}
    )


@dataclass
class ReplicaConfig:
    model_name: str = field(
        default="meta-llama/Llama-3-8B",
        metadata={"help": "Model name."},
    )
    gpu_memory_utilization: float = field(
        default=0.8,
        metadata={"help": "GPU memory utilization."},
    )
    num_pipeline_stages: int = field(
        default=2,
        metadata={"help": "Number of pipeline stages."},
    )
    tensor_parallel_size: int = field(
        default=8,
        metadata={"help": "Tensor parallel size."},
    )
    enable_sequence_pipeline_parallel: bool = field(
        default=False, metadata={"help": "Enable sequence pipeline parallelism."}
    )
    kv_parallel_size: int = field(
        default=1,
        metadata={"help": "KV parallel size."},
    )
    max_num_tokens_per_kvp_group: int = field(
        default=512 * 1024,
        metadata={"help": "Maximum number of tokens per KV group."},
    )
    device: str = field(
        default="h100",
        metadata={"help": "Device."},
    )
    network_device: str = field(
        default="h100_dgx",
        metadata={"help": "Network device."},
    )

    def __post_init__(self):
        if self.enable_sequence_pipeline_parallel and self.num_pipeline_stages == 1:
            logger.warning(
                "Sequence pipeline parallelism is enabled but number of pipeline stages is 1."
                "Disabling sequence pipeline parallelism."
            )
            self.enable_sequence_pipeline_parallel = False

        self.world_size = self.num_pipeline_stages * self.tensor_parallel_size
        self.model_config: BaseModelConfig = BaseModelConfig.create_from_name(
            self.model_name
        )
        self.device_config: BaseDeviceSKUConfig = (
            BaseDeviceSKUConfig.create_from_type_string(self.device)
        )
        self.node_config: BaseNodeSKUConfig = BaseNodeSKUConfig.create_from_type_string(
            self.network_device
        )

        assert self.model_config.num_q_heads % self.tensor_parallel_size == 0
        assert self.model_config.num_layers % self.num_pipeline_stages == 0
        assert self.model_config.embedding_dim % self.tensor_parallel_size == 0
        assert self.model_config.embedding_dim % self.model_config.num_q_heads == 0

        self._num_layers_per_pipeline_stage = (
            self.model_config.num_layers // self.num_pipeline_stages
        )
        self._attention_head_dim = (
            self.model_config.embedding_dim // self.model_config.num_q_heads
        )
        self._q_heads_per_tensor_parallel_worker = (
            self.model_config.num_q_heads // self.tensor_parallel_size
        )
        self._kv_heads_per_tensor_parallel_worker = ceil(
            self.model_config.num_kv_heads / self.tensor_parallel_size
        )

    @property
    def num_layers_per_pipeline_stage(self):
        return self._num_layers_per_pipeline_stage

    @property
    def attention_head_dim(self):
        return self._attention_head_dim

    @property
    def q_heads_per_tensor_parallel_worker(self):
        return self._q_heads_per_tensor_parallel_worker

    @property
    def kv_heads_per_tensor_parallel_worker(self):
        return self._kv_heads_per_tensor_parallel_worker


@dataclass
class BaseGlobalSchedulerConfig(BasePolyConfig):
    pass


@dataclass
class RandomGlobalSchedulerConfig(BaseGlobalSchedulerConfig):
    @staticmethod
    def get_type():
        return GlobalSchedulerType.RANDOM


@dataclass
class RoundRobinGlobalSchedulerConfig(BaseGlobalSchedulerConfig):
    @staticmethod
    def get_type():
        return GlobalSchedulerType.ROUND_ROBIN


@dataclass
class LORGlobalSchedulerConfig(BaseGlobalSchedulerConfig):
    @staticmethod
    def get_type():
        return GlobalSchedulerType.LOR


@dataclass
class BaseExecutionTimePredictorConfig(BasePolyConfig):
    model_profiling_dataset: str = field(
        default="project-vajra/dev-staging-meta-llama-llama-3-8b-h100",
        metadata={
            "help": "HuggingFace dataset that contains the model (compute) profiling data."
        },
    )
    network_profiling_dataset: str = field(
        default="project-vajra/dev-staging-h100-dgx",
        metadata={
            "help": "HuggingFace dataset that contains the network (communication) profiling data."
        },
    )
    prediction_hf_org: str = field(
        default="project-vajra",
        metadata={"help": "Organization to download predictions."},
    )
    prediction_hf_collection: str = field(
        default="dev-staging",
        metadata={"help": "Collection to download predictions."},
    )
    no_cache: bool = field(
        default=False,
        metadata={"help": "Whether to cache prediction models."},
    )
    kv_cache_prediction_granularity: int = field(
        default=256,
        metadata={"help": "KV cache prediction granularity."},
    )
    prediction_max_prefill_chunk_size: int = field(
        default=4096,
        metadata={"help": "Max prefill chunk size for prediction."},
    )
    prediction_max_batch_size: int = field(
        default=128,
        metadata={"help": "Max batch size for prediction."},
    )
    prediction_max_tokens_per_request: int = field(
        default=2 * 1024 * 1024,
        metadata={"help": "Max tokens per request for prediction."},
    )
    attention_decode_batching_overhead_fraction: float = field(
        default=0.1,
        metadata={"help": "Attention decode batching overhead fraction."},
    )
    nccl_cpu_launch_overhead_ms: float = field(
        default=0.02,
        metadata={"help": "NCCL CPU launch overhead in ms."},
    )
    nccl_cpu_skew_overhead_per_device_ms: float = field(
        default=0.0,
        metadata={"help": "NCCL CPU skew overhead per device in ms."},
    )
    k_fold_cv_splits: int = field(
        default=10,
        metadata={"help": "Number of k fold cross validation splits."},
    )
    num_training_job_threads: int = field(
        default=-1,
        metadata={"help": "Number of training job threads."},
    )
    cache_dir: str = field(
        default=".vidur_cache",
        metadata={"help": "Cache directory."},
    )
    disable_kvp_communication: bool = field(
        default=True,
        metadata={"help": "Whether to disable KVP communication."},
    )
    upload_predictions: bool = field(
        default=False,
        metadata={"help": "Whether to upload predictions."},
    )
    upload_to_private_repo: bool = field(
        default=False,
        metadata={"help": "Whether to upload to private repo."},
    )
    use_native_execution_time_predictor: bool = field(
        default=False,
        metadata={"help": "Whether to use cpp execution time predictor."},
    )


@dataclass
class LinearRegressionExecutionTimePredictorConfig(BaseExecutionTimePredictorConfig):
    polynomial_degree: List[int] = field(
        default_factory=lambda: list(range(1, 6)),
        metadata={"help": "Polynomial degree for linear regression."},
    )
    polynomial_include_bias: List[bool] = field(
        default_factory=lambda: [True, False],
        metadata={"help": "Polynomial include bias for linear regression."},
    )
    polynomial_interaction_only: List[bool] = field(
        default_factory=lambda: [True, False],
        metadata={"help": "Polynomial interaction only for linear regression."},
    )
    fit_intercept: List[bool] = field(
        default_factory=lambda: [True, False],
        metadata={"help": "Fit intercept for linear regression."},
    )

    @staticmethod
    def get_type():
        return ExecutionTimePredictorType.LINEAR_REGRESSION


@dataclass
class RandomForrestExecutionTimePredictorConfig(BaseExecutionTimePredictorConfig):
    num_estimators: List[int] = field(
        default_factory=lambda: [250, 500, 750],
        metadata={"help": "Number of estimators for random forest."},
    )
    max_depth: List[int] = field(
        default_factory=lambda: [8, 16, 32],
        metadata={"help": "Maximum depth for random forest."},
    )
    min_samples_split: List[int] = field(
        default_factory=lambda: [2, 5, 10],
        metadata={"help": "Minimum samples split for random forest."},
    )

    @staticmethod
    def get_type():
        return ExecutionTimePredictorType.RANDOM_FORREST


@dataclass
class ClusterConfig:
    num_replicas: int = field(
        default=1,
        metadata={"help": "Number of replicas."},
    )
    replica_config: ReplicaConfig = field(default_factory=ReplicaConfig)
    cache_config: CacheConfig = field(
        default_factory=CacheConfig,
        metadata={"help": "Cache config."},
    )
    global_scheduler_config: BaseGlobalSchedulerConfig = field(
        default_factory=RoundRobinGlobalSchedulerConfig,
        metadata={"help": "Global scheduler config."},
    )
    replica_scheduler_config: BaseReplicaSchedulerConfig = field(
        default_factory=MnemosyneFCFSFixedChunkSchedulerConfig,
        metadata={"help": "Replica scheduler config."},
    )

    def __post_init__(self):
        if self.replica_config.enable_sequence_pipeline_parallel:
            assert self.replica_scheduler_config.get_type() in [
                ReplicaSchedulerType.SARATHI,
                ReplicaSchedulerType.MNEMOSYNE_FCFS_FIXED_CHUNK,
                ReplicaSchedulerType.MNEMOSYNE_FCFS,
                ReplicaSchedulerType.MNEMOSYNE_EDF,
                ReplicaSchedulerType.MNEMOSYNE_LRS,
                ReplicaSchedulerType.MNEMOSYNE_ST,
            ]


@dataclass
class SimulationConfig(ABC):
    seed: int = field(
        default=42,
        metadata={"help": "Seed for the random number generator."},
    )
    log_level: str = field(
        default="info",
        metadata={"help": "Logging level."},
    )
    time_limit: int = field(
        default=0,  # in seconds, 0 is no limit
        metadata={"help": "Time limit for simulation in seconds. 0 means no limit."},
    )
    cluster_config: ClusterConfig = field(
        default_factory=ClusterConfig,
        metadata={"help": "Cluster config."},
    )
    request_generator_config: BaseRequestGeneratorConfig = field(
        default_factory=SyntheticRequestGeneratorConfig,
        metadata={"help": "Request generator config."},
    )
    execution_time_predictor_config: BaseExecutionTimePredictorConfig = field(
        default_factory=RandomForrestExecutionTimePredictorConfig,
        metadata={"help": "Execution time predictor config."},
    )
    metrics_config: MetricsConfig = field(
        default_factory=MetricsConfig,
        metadata={"help": "Metrics config."},
    )

    def __post_init__(self):
        self.write_config_to_file()

    @classmethod
    def create_from_cli_args(cls):
        flat_config = create_flat_dataclass(cls).create_from_cli_args()
        instance = flat_config.reconstruct_original_dataclass()
        instance.__flat_config__ = flat_config
        return instance

    def to_dict(self):
        if not hasattr(self, "__flat_config__"):
            logger.warning("Flat config not found. Returning the original config.")
            return self.__dict__

        return self.__flat_config__.__dict__

    def write_config_to_file(self):
        config_dict = dataclass_to_dict(self)
        with open(f"{self.metrics_config.output_dir}/config.json", "w") as f:
            json.dump(config_dict, f, indent=4)
