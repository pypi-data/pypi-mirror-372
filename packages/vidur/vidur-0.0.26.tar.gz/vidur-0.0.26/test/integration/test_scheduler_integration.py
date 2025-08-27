"""Integration tests for Vidur scheduler configurations.

This module tests that each scheduler type can run without crashing
with minimal configuration parameters.
"""

import sys
import time

import pytest

from vidur.main import main
from vidur.types.replica_scheduler_type import ReplicaSchedulerType


class TestSchedulerIntegration:
    """Integration tests for different scheduler configurations."""

    SCHEDULER_TYPES = [
        "sarathi",
        "vllm",
        "mnemosyne_fcfs_fixed_chunk",
        "mnemosyne_fcfs",
        "mnemosyne_edf",
        "mnemosyne_lrs",
    ]

    # SPP-compatible schedulers (excluding VLLM)
    SPP_SCHEDULER_TYPES = [
        "sarathi",
        "mnemosyne_fcfs_fixed_chunk", 
        "mnemosyne_fcfs",
        "mnemosyne_edf",
        "mnemosyne_lrs",
    ]

    @pytest.mark.parametrize("scheduler_type", SCHEDULER_TYPES)
    @pytest.mark.parametrize("request_pattern", ["default", "poisson_uniform"])
    def test_scheduler_no_crash(self, scheduler_type: str, request_pattern: str, monkeypatch, temp_output_dir):
        """Test that each scheduler type runs without crashing."""
        
        # Set up minimal command line arguments
        test_args = [
            "vidur.main",  # argv[0] - script name
            "--replica_scheduler_config_type", scheduler_type,
            "--metrics_config_output_dir", str(temp_output_dir),
            "--no-replica_config_enable_sequence_pipeline_parallel",
            "--no-metrics_config_write_metrics",
            "--no-metrics_config_write_json_trace",
            "--no-metrics_config_store_plots",
            "--no-metrics_config_store_request_metrics",
            "--no-metrics_config_store_batch_metrics",
            "--no-metrics_config_store_utilization_metrics",
            "--no-metrics_config_store_operation_metrics",
            "--no-metrics_config_enable_chrome_trace",
        ]
        
        # Add Poisson arrival and uniform request length parameters if requested
        if request_pattern == "poisson_uniform":
            test_args.extend([
                "--interval_generator_config_type", "poisson",
                "--length_generator_config_type", "uniform",
                "--poisson_request_interval_generator_config_qps", "10",
                "--uniform_request_length_generator_config_min_tokens", "1024",
                "--uniform_request_length_generator_config_max_tokens", "4096",
            ])
        
        print(f"\nTesting scheduler: {scheduler_type} with {request_pattern} pattern")
        print(f"Args: {' '.join(test_args)}")
        
        # Mock sys.argv for the test
        monkeypatch.setattr(sys, "argv", test_args)
        
        # Run the main function directly
        start_time = time.time()
        try:
            main()
            duration = time.time() - start_time
            print(f"✓ Scheduler {scheduler_type} completed successfully in {duration:.2f}s")
            
        except Exception as e:
            pytest.fail(f"Scheduler {scheduler_type} failed with exception: {str(e)}")

    @pytest.mark.parametrize("scheduler_type", SPP_SCHEDULER_TYPES)
    @pytest.mark.parametrize("request_pattern", ["default", "poisson_uniform"])
    def test_scheduler_with_spp(self, scheduler_type: str, request_pattern: str, monkeypatch, temp_output_dir):
        """Test that SPP-compatible schedulers run without crashing with SPP enabled."""
        
        # Set up minimal command line arguments with SPP enabled
        test_args = [
            "vidur.main",  # argv[0] - script name
            "--replica_scheduler_config_type", scheduler_type,
            "--metrics_config_output_dir", str(temp_output_dir),
            "--replica_config_enable_sequence_pipeline_parallel",  # Enable SPP
            "--no-metrics_config_write_metrics",
            "--no-metrics_config_write_json_trace",
            "--no-metrics_config_store_plots",
            "--no-metrics_config_store_request_metrics",
            "--no-metrics_config_store_batch_metrics",
            "--no-metrics_config_store_utilization_metrics",
            "--no-metrics_config_store_operation_metrics",
            "--no-metrics_config_enable_chrome_trace",
        ]
        
        # Add Poisson arrival and uniform request length parameters if requested
        if request_pattern == "poisson_uniform":
            test_args.extend([
                "--interval_generator_config_type", "poisson",
                "--length_generator_config_type", "uniform",
                "--poisson_request_interval_generator_config_qps", "10",
                "--uniform_request_length_generator_config_min_tokens", "1024",
                "--uniform_request_length_generator_config_max_tokens", "4096",
            ])
        
        print(f"\nTesting scheduler: {scheduler_type} with SPP enabled and {request_pattern} pattern")
        print(f"Args: {' '.join(test_args)}")
        
        # Mock sys.argv for the test
        monkeypatch.setattr(sys, "argv", test_args)
        
        # Run the main function directly
        start_time = time.time()
        try:
            main()
            duration = time.time() - start_time
            print(f"✓ Scheduler {scheduler_type} with SPP completed successfully in {duration:.2f}s")
            
        except Exception as e:
            pytest.fail(f"Scheduler {scheduler_type} with SPP failed with exception: {str(e)}")

    def test_native_execution_single_request(self, monkeypatch, temp_output_dir):
        """Test that native execution time predictor works with a single request."""
        
        # Use a simple scheduler for this test
        scheduler_type = "mnemosyne_fcfs"
        
        # Set up command line arguments with native execution enabled and single request
        test_args = [
            "vidur.main",  # argv[0] - script name
            "--replica_scheduler_config_type", scheduler_type,
            "--metrics_config_output_dir", str(temp_output_dir),
            "--no-replica_config_enable_sequence_pipeline_parallel",  # Disable SPP for simplicity
            "--random_forrest_execution_time_predictor_config_use_native_execution_time_predictor",  # Enable native execution
            "--synthetic_request_generator_config_num_requests", "1",  # Single request
            "--fixed_request_length_generator_config_prefill_tokens", "512",  # Smaller request
            "--fixed_request_length_generator_config_decode_tokens", "128",   # Smaller response
            "--no-metrics_config_write_metrics",
            "--no-metrics_config_write_json_trace",
            "--no-metrics_config_store_plots",
            "--no-metrics_config_store_request_metrics",
            "--no-metrics_config_store_batch_metrics",
            "--no-metrics_config_store_utilization_metrics",
            "--no-metrics_config_store_operation_metrics",
            "--no-metrics_config_enable_chrome_trace",
        ]
        
        print(f"\nTesting native execution with single request using scheduler: {scheduler_type}")
        print(f"Args: {' '.join(test_args)}")
        
        # Mock sys.argv for the test
        monkeypatch.setattr(sys, "argv", test_args)
        
        # Run the main function directly
        start_time = time.time()
        try:
            main()
            duration = time.time() - start_time
            print(f"✓ Native execution with single request completed successfully in {duration:.2f}s")
            
        except Exception as e:
            pytest.fail(f"Native execution with single request failed with exception: {str(e)}")

    def test_all_scheduler_types_available(self):
        """Test that all expected scheduler types are available in the enum."""
        # Get all values from the ReplicaSchedulerType enum
        available_schedulers = set(scheduler_type.name.lower() for scheduler_type in ReplicaSchedulerType)
        expected_schedulers = set(self.SCHEDULER_TYPES)
        
        # Check that all expected schedulers are available
        missing_schedulers = expected_schedulers - available_schedulers
        if missing_schedulers:
            pytest.fail(f"Missing scheduler types in enum: {missing_schedulers}")
        
        print(f"✓ All {len(expected_schedulers)} scheduler types are available in ReplicaSchedulerType enum")