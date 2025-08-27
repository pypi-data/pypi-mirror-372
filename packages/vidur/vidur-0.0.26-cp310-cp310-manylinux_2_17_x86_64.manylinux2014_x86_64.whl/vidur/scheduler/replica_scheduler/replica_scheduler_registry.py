from vidur.scheduler.replica_scheduler.mnemosyne_edf_replica_scheduler import (
    MnemosyneEDFReplicaScheduler,
)
from vidur.scheduler.replica_scheduler.mnemosyne_fcfs_fixed_chunk_replica_scheduler import (
    MnemosyneFCFSFixedChunkReplicaScheduler,
)
from vidur.scheduler.replica_scheduler.mnemosyne_fcfs_replica_scheduler import (
    MnemosyneFCFSReplicaScheduler,
)
from vidur.scheduler.replica_scheduler.mnemosyne_lrs_replica_scheduler import (
    MnemosyneLRSReplicaScheduler,
)
from vidur.scheduler.replica_scheduler.mnemosyne_st_replica_scheduler import (
    MnemosyneSTReplicaScheduler,
)
from vidur.scheduler.replica_scheduler.orca_replica_scheduler import (
    OrcaReplicaScheduler,
)
from vidur.scheduler.replica_scheduler.sarathi_replica_scheduler import (
    SarathiReplicaScheduler,
)
from vidur.scheduler.replica_scheduler.vllm_replica_scheduler import (
    VLLMReplicaScheduler,
)
from vidur.types import ReplicaSchedulerType
from vidur.utils.base_registry import BaseRegistry


class ReplicaSchedulerRegistry(BaseRegistry):
    pass


ReplicaSchedulerRegistry.register(ReplicaSchedulerType.ORCA, OrcaReplicaScheduler)
ReplicaSchedulerRegistry.register(ReplicaSchedulerType.SARATHI, SarathiReplicaScheduler)
ReplicaSchedulerRegistry.register(ReplicaSchedulerType.VLLM, VLLMReplicaScheduler)
ReplicaSchedulerRegistry.register(
    ReplicaSchedulerType.MNEMOSYNE_FCFS_FIXED_CHUNK,
    MnemosyneFCFSFixedChunkReplicaScheduler,
)
ReplicaSchedulerRegistry.register(
    ReplicaSchedulerType.MNEMOSYNE_FCFS, MnemosyneFCFSReplicaScheduler
)
ReplicaSchedulerRegistry.register(
    ReplicaSchedulerType.MNEMOSYNE_EDF, MnemosyneEDFReplicaScheduler
)
ReplicaSchedulerRegistry.register(
    ReplicaSchedulerType.MNEMOSYNE_LRS, MnemosyneLRSReplicaScheduler
)
ReplicaSchedulerRegistry.register(
    ReplicaSchedulerType.MNEMOSYNE_ST, MnemosyneSTReplicaScheduler
)
