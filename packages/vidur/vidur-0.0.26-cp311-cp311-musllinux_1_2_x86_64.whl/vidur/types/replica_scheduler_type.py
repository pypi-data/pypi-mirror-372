from vidur.types.base_int_enum import BaseIntEnum


class ReplicaSchedulerType(BaseIntEnum):
    ORCA = 1
    SARATHI = 2
    VLLM = 3
    MNEMOSYNE_FCFS_FIXED_CHUNK = 4
    MNEMOSYNE_FCFS = 5
    MNEMOSYNE_EDF = 6
    MNEMOSYNE_LRS = 7
    MNEMOSYNE_ST = 10
