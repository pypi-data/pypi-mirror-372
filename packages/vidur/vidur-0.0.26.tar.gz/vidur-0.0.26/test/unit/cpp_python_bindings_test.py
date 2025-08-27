# Test the creation of cpp entities, configs and execution time predictor

import pytest
from vidur._native.entities import Batch as BatchC, KVParallelBatch as KVParallelBatchC, ExecutionTime as ExecutionTimeC
from vidur._native.execution_time_predictor import ExecutionTimePredictor as ExecutionTimePredictorC
from vidur._native.config import ExecutionTimePredictorConfig as ExecutionTimePredictorConfigC, ReplicaConfig as ReplicaConfigC, ModelConfig as ModelConfigC

def test_batch_creation():
    # Test basic batch creation
    batch = BatchC(
        replica_id=0,
        num_requests=2,
        num_q_tokens=[10, 15],
        num_kv_tokens=[20, 25],
        num_active_kvp_groups=[1, 2],
        kvp_group_id=0
    )
    
    # Test properties
    assert batch.replica_id == 0
    assert batch.num_requests == 2
    assert list(batch.num_q_tokens) == [10, 15]
    assert list(batch.num_kv_tokens) == [20, 25]
    assert list(batch.num_active_kvp_groups) == [1, 2]
    assert batch.kvp_group_id == 0
    assert batch.total_num_q_tokens == 25  # 10 + 15
    assert batch.total_num_kv_tokens == 45  # 20 + 25

def test_kv_parallel_batch():
    # Create some batches
    batch1 = BatchC(0, 2, [10, 15], [20, 25], [1, 2], 0)
    batch2 = BatchC(0, 2, [12, 18], [22, 28], [1, 2], 1)
    
    # Create KVParallelBatch
    kvp_batch = KVParallelBatchC(
        replica_id=0,
        kvp_group_ids=[0, 1],
        batches=[batch1, batch2]
    )
    
    # Test properties
    assert kvp_batch.replica_id == 0
    batch_map = kvp_batch.batch_mapping
    assert len(batch_map) == 2
    assert 0 in batch_map
    assert 1 in batch_map

def test_execution_time():
    # Test execution time creation
    exec_time = ExecutionTimeC(
        num_layers_per_pipeline_stage=4,
        attention_rope_execution_time=1.0,
        attention_kv_cache_save_execution_time=1.0,
        attention_decode_execution_time=2.0,
        attention_prefill_execution_time=2.0,
        attention_layer_pre_proj_execution_time=1.0,
        attention_layer_post_proj_execution_time=1.0,
        mlp_layer_up_proj_execution_time=1.0,
        mlp_layer_down_proj_execution_time=1.0,
        mlp_layer_act_execution_time=1.0,
        attn_norm_time=1.0,
        mlp_norm_time=1.0,
        add_time=1.0,
        tensor_parallel_communication_time=0.5,
        pipeline_parallel_communication_time=0.5,
    )
    
    # Test methods
    assert exec_time.model_time > 0
    assert exec_time.total_time > 0

def test_replica_config():
    # Test config creation
    config = ReplicaConfigC(
        num_pipeline_stages=2,
        tensor_parallel_size=1,
        kv_parallel_size=1
    )
    
    # Test properties
    assert config.num_pipeline_stages == 2
    assert config.tensor_parallel_size == 1
    assert config.kv_parallel_size == 1

def test_model_config():
    config = ModelConfigC(
        num_layers=8,
        num_q_heads=16,
        num_kv_heads=16,
        embedding_dim=1024,
        mlp_hidden_dim=4096,
        max_model_len=4096,
        use_gated_mlp=True,
        use_bias=True,
        use_qkv_bias=True,
        post_attn_norm=True,
        vocab_size=10000
    )
    
    # Test properties
    assert config.num_layers == 8
    assert config.num_q_heads == 16
    assert config.num_kv_heads == 16
    assert config.embedding_dim == 1024
    assert config.mlp_hidden_dim == 4096
    assert config.max_model_len == 4096
    assert config.use_gated_mlp == True
    assert config.use_bias == True
    assert config.use_qkv_bias == True
    assert config.post_attn_norm == True
    assert config.vocab_size == 10000

def test_execution_time_predictor_config():
    # Test config creation
    config = ExecutionTimePredictorConfigC(
        kv_cache_prediction_granularity=256,
        prediction_max_prefill_chunk_size=4096,
        prediction_max_batch_size=128,
        prediction_max_tokens_per_request=2 * 1024 * 1024,
        attention_decode_batching_overhead_fraction=0.1,
        nccl_cpu_launch_overhead_ms=0.02,
        nccl_cpu_skew_overhead_per_device_ms=0.0,
        use_native_execution_time_predictor=True,
        disable_kvp_communication=True
    )
    
    # Test properties
    assert config.kv_cache_prediction_granularity == 256
    assert config.prediction_max_prefill_chunk_size == 4096
    assert config.prediction_max_batch_size == 128
    assert config.prediction_max_tokens_per_request == 2 * 1024 * 1024
    assert config.attention_decode_batching_overhead_fraction == 0.1
    assert config.nccl_cpu_launch_overhead_ms == 0.02
    assert config.nccl_cpu_skew_overhead_per_device_ms == 0.0
    assert config.use_native_execution_time_predictor
    assert config.disable_kvp_communication

def test_execution_time_predictor():
    # Create configs using native implementations
    model_config = ModelConfigC(
        num_layers=8,
        num_q_heads=16,
        num_kv_heads=16,
        embedding_dim=1024,
        mlp_hidden_dim=4096,
        max_model_len=4096,
        use_gated_mlp=True,
        use_bias=True,
        use_qkv_bias=True,
        post_attn_norm=True,
        vocab_size=10000
    )
    
    replica_config = ReplicaConfigC(
        num_pipeline_stages=2,
        tensor_parallel_size=1,
        kv_parallel_size=1
    )
    
    predictor_config = ExecutionTimePredictorConfigC(
        kv_cache_prediction_granularity=256,
        prediction_max_prefill_chunk_size=4096,
        prediction_max_batch_size=128,
        prediction_max_tokens_per_request=2 * 1024 * 1024,
        attention_decode_batching_overhead_fraction=0.1,
        nccl_cpu_launch_overhead_ms=0.02,
        nccl_cpu_skew_overhead_per_device_ms=0.0,
        use_native_execution_time_predictor=True,
        disable_kvp_communication=True
    )
    
    # Create some sample prediction data
    prediction_ops = ["attention", "mlp"]
    prediction_keys = [[(1, 1), (2, 2)], [(3, 3), (4, 4)]]
    prediction_values = [[0.1, 0.2], [0.3, 0.4]]
    
    # Create predictor
    predictor = ExecutionTimePredictorC(
        predictor_config,
        replica_config,
        model_config,
        prediction_ops,
        prediction_keys,
        prediction_values
    )
    
    # Test prediction with a batch
    batch = BatchC(0, 2, [10, 15], [20, 25], [1, 2], 0)
    exec_time = predictor.get_execution_time_batch(batch, pipeline_stage=0)
    assert isinstance(exec_time, ExecutionTimeC)
    
    # Test prediction with KVParallelBatch
    batch1 = BatchC(0, 2, [10, 15], [20, 25], [1, 2], 0)
    batch2 = BatchC(0, 2, [12, 18], [22, 28], [1, 2], 1)
    kvp_batch = KVParallelBatchC(0, [0, 1], [batch1, batch2])
    exec_time = predictor.get_execution_time_kv_parallel_batch(kvp_batch, pipeline_stage=0)
    assert isinstance(exec_time, ExecutionTimeC)
