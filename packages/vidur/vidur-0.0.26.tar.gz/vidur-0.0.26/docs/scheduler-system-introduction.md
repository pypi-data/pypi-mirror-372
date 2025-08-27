# Mnemosyne Scheduler System

## Overview

The Mnemosyne scheduler family provides a hierarchy of scheduling algorithms for LLM inference, ranging from simple FCFS to sophisticated space-time sharing. All schedulers inherit from `MnemosyneBaseReplicaScheduler`.

## Base Architecture

### Core Features

1. **KV-parallel batch formation**: Distributes memory across parallel groups
2. **Memory management**: Watermark-based protection with preemption support
3. **Request lifecycle**: Handles prefill/decode phases with partial prefill support
4. **Dual queue system**: Separate queues for new requests and partial prefill requests
5. **Abstract interfaces**: Priority and chunk sizing methods

### Key Methods

- `_get_request_priority()`: Determines request priority (abstract)
- `_get_request_next_num_q_tokens()`: Determines chunk size (abstract)
- `_sort_request_queue()`: Sorts requests by priority
- `_get_next_batch()`: Main scheduling logic
- `add_partial_prefill_request()`: Adds partially processed requests to priority queue
- `num_partial_prefill_requests`: Property returning count of partial prefill requests

## Scheduler Implementations

### 1. FCFS Fixed Chunk

**Algorithm**: First-Come-First-Served with fixed chunk sizes

**Priority**:
```python
def _get_request_priority(self, request):
    return (request.arrived_at, request.id)
```

**Chunk Sizing**:
```python
next_num_tokens = min(
    request.num_prefill_tokens - num_processed_tokens,
    chunk_size - max_num_q_tokens_across_groups
)
```

**Characteristics**:
- Simple and predictable
- Fixed chunk size from configuration
- Minimal computational overhead

### 2. FCFS Dynamic

**Algorithm**: FCFS with adaptive chunk sizing using execution time prediction

**Priority**: Same as FCFS Fixed

**Chunk Sizing**:
- Binary search to find optimal chunk size
- Targets execution time within slack bounds
- Uses `BatchFormationTrackerWithRuntimePrediction`
- Caches last chunk size per request

**Characteristics**:
- Adaptive batching for better hardware utilization
- 10% slack tolerance on target batch time
- Higher computational overhead than fixed chunk

### 3. EDF (Earliest Deadline First)

**Algorithm**: Prioritizes requests by deadline

**Priority**:
```python
def _get_request_priority(self, request):
    return (request.deadline, request.id)
```

**Deadline Calculation**:
```python
prefill_time = self._prefill_time_calculator.get_prefill_time(request.num_prefill_tokens)
deadline_time = prefill_time * self._config.deadline_multiplier
deadline_time = max(prefill_time, self._config.min_deadline)
request.deadline = request.arrived_at + deadline_time
```

**Characteristics**:
- Deadline-aware scheduling
- Inherits dynamic chunk sizing from FCFS
- Better SLA compliance

### 4. LRS (Least Remaining Slack)

**Algorithm**: Dynamic priority based on remaining slack

**Priority**: Uses custom sorting instead of static priority
```python
def _sort_request_queue(self, time):
    self._request_queue.sort(
        key=lambda x: self._get_remaining_slack_fraction(time, x[1])
    )
```

**Slack Calculation**:
```python
def _get_remaining_slack_fraction(self, time, request):
    remaining_prefill_time = self._prefill_time_calculator.get_prefill_time(
        request.num_prefill_tokens,
        self._get_num_processed_tokens(request)
    )
    slack = request.deadline - time - remaining_prefill_time
    return slack / request.deadline_time
```

**Characteristics**:
- Time-aware dynamic prioritization
- Continuously reorders queue
- Better fairness under load

### 5. ST (Space-Time)

**Algorithm**: Space-time sharing with special handling for long requests

**Priority**: Inherits LRS priority mechanism

**Chunk Sizing**:
```python
def _get_request_next_num_q_tokens(self, time, request, batch_formation_tracker):
    if num_processed_tokens < long_request_threshold:
        target_time = self._config.target_batch_time
    else:
        # Long request handling
        if any(long_request_in_batch):
            return 0  # Avoid multiple long requests
        
        slack_fraction = self._get_remaining_slack_fraction(time, request)
        slack_fraction = max(0.0, min(MAX_SPACE_SHARE_FRAC, slack_fraction))
        target_time = self._config.target_batch_time * (1 - slack_fraction)
```

**Characteristics**:
- Adaptive resource allocation based on slack
- Prevents long request contention
- Optimal for mixed workloads

## Comparison

### Priority Mechanisms

| Scheduler | Method | Logic |
|-----------|--------|-------|
| FCFS Fixed | `_get_request_priority()` | `(arrived_at, id)` |
| FCFS Dynamic | `_get_request_priority()` | `(arrived_at, id)` |
| EDF | `_get_request_priority()` | `(deadline, id)` |
| LRS | `_sort_request_queue()` | `remaining_slack_fraction` |
| ST | `_sort_request_queue()` | `remaining_slack_fraction` |

### Chunk Sizing Strategies

| Scheduler | Strategy | Key Features |
|-----------|----------|--------------|
| FCFS Fixed | Fixed size | Simple subtraction |
| FCFS Dynamic | Adaptive | Binary search, execution prediction |
| EDF | Adaptive | Inherits from FCFS Dynamic |
| LRS | Adaptive | Inherits from EDF |
| ST | Slack-based | Adjusts target time by slack |

## Selection Guidelines

### FCFS Fixed Chunk
- Maximum predictability required
- Uniform request priorities
- Simplicity over optimization

### FCFS Dynamic
- Better hardware utilization needed
- Similar request priorities
- Can afford prediction overhead

### EDF
- Explicit deadlines present
- SLA compliance critical
- Mixed urgent/background workloads

### LRS
- Variable system load
- Need adaptive prioritization
- Fairness under pressure important

### ST
- Mixed short/long requests
- Resource efficiency paramount
- Most sophisticated scheduling needed

## Performance Characteristics

### Computational Overhead
- **Lowest**: FCFS Fixed
- **Low**: FCFS Dynamic
- **Medium**: EDF
- **High**: LRS
- **Highest**: ST

### Scheduling Effectiveness
- **Basic**: FCFS Fixed
- **Good**: FCFS Dynamic
- **Better**: EDF
- **Advanced**: LRS
- **Optimal**: ST

## Partial Prefill Request Management

### Architecture

The Mnemosyne scheduler implements a **dual queue system** for efficient partial prefill handling:

- **`_request_queue`**: New incoming requests awaiting first scheduling
- **`_partial_prefill_queue`**: Requests that have been partially processed and need continuation

### Request Flow

```
New Request → _request_queue → Batch Processing → Partial Completion
                                      ↓
SPP Mode: on_stage_end() ←— Request routing logic —→ Non-SPP Mode: on_batch_end()
                ↓                                                    ↓
        _partial_prefill_queue ←————————————————————————————————————————
                ↓
        Priority processing in _get_next_batch()
```

### Scheduling Priority

In `_get_next_batch()`, partial prefill requests receive **higher priority**:

1. Process running decode requests (preempted)
2. **Process partial prefill queue first** (priority)
3. Process new request queue

Both queues use identical priority mechanisms (`_get_request_priority()`) implemented by scheduler subclasses.

### Mode-Specific Routing

**Non-SPP Mode** (`on_batch_end()`):
- Routes incomplete prefill requests to `_partial_prefill_queue`
- Complete prefills move to `_preempted_requests`

**SPP Mode** (`on_stage_end()`):
- Routes incomplete stage 0 prefills to `_partial_prefill_queue`
- Complete stage prefills handled separately

### Benefits

- **Fairness**: Prevents request starvation from repeated pre-emption
- **Efficiency**: Prioritizes continuation over new work
- **Consistency**: Maintains scheduler-specific priority logic across both queues

## Summary

The Mnemosyne scheduler family demonstrates progressive sophistication:

1. **FCFS Fixed**: Simple baseline
2. **FCFS Dynamic**: Adds adaptive chunk sizing
3. **EDF**: Adds deadline awareness
4. **LRS**: Adds dynamic slack-based prioritization
5. **ST**: Adds space-time resource sharing

Each scheduler builds on previous capabilities while maintaining the same core architecture and partial prefill management. Selection depends on workload characteristics and performance requirements.