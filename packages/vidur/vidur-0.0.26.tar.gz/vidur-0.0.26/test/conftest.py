import os
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import pytest
from pytest import Config, Item, TestReport


@dataclass
class TestRunStats:
    """Tracks statistics for test execution."""

    start_time: float = 0.0
    total_duration: float = 0.0
    tests_executed: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    tests_deselected: int = 0
    slowest_tests: List[Tuple[str, float]] = field(default_factory=list)

    def __post_init__(self):
        self.slowest_tests = []
        self.start_time = time.time()

    def update_duration(self):
        self.total_duration = time.time() - self.start_time

    def record_test_duration(self, test_name: str, duration: float):
        self.slowest_tests.append((test_name, duration))
        self.slowest_tests.sort(key=lambda x: x[1], reverse=True)
        if len(self.slowest_tests) > 10:  # Keep only the 10 slowest tests
            self.slowest_tests = self.slowest_tests[:10]


# Global test run statistics
test_stats = TestRunStats()


def pytest_configure(config: Config):
    """Called after command line options have been parsed."""
    test_stats.__post_init__()


def pytest_collection_modifyitems(config: Config, items: List[Item]):
    """Called after collection has been performed."""
    test_stats.tests_executed = len(items)


def pytest_runtest_setup(item: Item):
    """Called to perform the setup phase for a test item."""
    pass


def pytest_runtest_teardown(item: Item, nextitem: Optional[Item]):
    """Called to perform the teardown phase for a test item."""
    pass


def pytest_runtest_logreport(report: TestReport):
    """Called for each test result."""
    if report.when == "call":  # Only count the main test execution
        if report.outcome == "passed":
            test_stats.tests_passed += 1
        elif report.outcome == "failed":
            test_stats.tests_failed += 1
        elif report.outcome == "skipped":
            test_stats.tests_skipped += 1

        # Record test duration for slowest test tracking
        test_name = report.nodeid
        duration = getattr(report, "duration", 0.0)
        test_stats.record_test_duration(test_name, duration)


def pytest_deselected(items: List[Item]):
    """Called for deselected test items."""
    test_stats.tests_deselected = len(items)


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    test_stats.update_duration()

    # Print summary statistics
    print("\n" + "=" * 80)
    print(f"Test Run Summary")
    print("=" * 80)
    print(f"Duration: {test_stats.total_duration:.2f}s")
    print(f"Tests executed: {test_stats.tests_executed}")
    print(f"Passed: {test_stats.tests_passed}")
    print(f"Failed: {test_stats.tests_failed}")
    print(f"Skipped: {test_stats.tests_skipped}")
    if test_stats.tests_deselected > 0:
        print(f"Deselected: {test_stats.tests_deselected}")

    if test_stats.slowest_tests:
        print(f"\nSlowest Tests:")
        for i, (test_name, duration) in enumerate(test_stats.slowest_tests[:5], 1):
            print(f"  {i}. {test_name} ({duration:.2f}s)")

    print("=" * 80)


# Test fixtures
@pytest.fixture(scope="session")
def test_data_dir():
    """Return the path to test data directory."""
    return os.path.join(os.path.dirname(__file__), "..", "data")


@pytest.fixture(scope="session")
def temp_output_dir(tmp_path_factory):
    """Create a temporary directory for test outputs."""
    return tmp_path_factory.mktemp("test_output")


@pytest.fixture(autouse=True)
def reset_base_entity():
    """Reset BaseEntity, BaseEvent and all subclass _id variables before each test."""
    from vidur.entities.base_entity import BaseEntity
    from vidur.entities.batch import Batch
    from vidur.entities.batch_stage import BatchStage
    from vidur.entities.cluster import Cluster
    from vidur.entities.execution_time import ExecutionTime
    from vidur.entities.kv_parallel_batch import KVParallelBatch
    from vidur.entities.kv_parallel_batch_stage import KVParallelBatchStage
    from vidur.entities.replica import Replica
    from vidur.entities.request import Request
    
    from vidur.events.base_event import BaseEvent
    from vidur.events.batch_end_event import BatchEndEvent
    from vidur.events.batch_stage_arrival_event import BatchStageArrivalEvent
    from vidur.events.batch_stage_end_event import BatchStageEndEvent
    from vidur.events.global_schedule_event import GlobalScheduleEvent
    from vidur.events.replica_schedule_event import ReplicaScheduleEvent
    from vidur.events.replica_stage_schedule_event import ReplicaStageScheduleEvent
    from vidur.events.request_arrival_event import RequestArrivalEvent
    
    # Store original states
    original_states = {}
    all_classes = [
        # Entity classes
        BaseEntity, Batch, BatchStage, Cluster, ExecutionTime, 
        KVParallelBatch, KVParallelBatchStage, Replica, Request,
        # Event classes
        BaseEvent, BatchEndEvent, BatchStageArrivalEvent, BatchStageEndEvent,
        GlobalScheduleEvent, ReplicaScheduleEvent, ReplicaStageScheduleEvent, RequestArrivalEvent
    ]
    
    for cls in all_classes:
        if hasattr(cls, '_id'):
            original_states[cls] = cls._id
            # Reset to initial state (BaseEvent starts at 0, BaseEntity at -1)
            if issubclass(cls, BaseEvent):
                cls._id = 0
            else:
                cls._id = -1
    
    yield