# Event System Overview

## Core Concepts

The Vidur simulator uses discrete event simulation to model LLM inference systems. Events represent actions that occur at specific times and trigger follow-up events, creating chains of causality that accurately model system behavior.

### Event Properties

1. **Time**: When the event occurs
2. **Priority**: Execution order for simultaneous events
3. **Action**: Operations performed when the event executes

### Priority System

Events are prioritized by tuple: `(time, event_type, event_id)`

```python
def _get_priority_number(self):
    return (self._time, self._id, self.event_type)
```

## Event Types

### 1. REQUEST_ARRIVAL (Priority 2)

**Purpose**: New request enters the system

**Actions**:
- Add request to global scheduler queue
- Record arrival metrics
- Trigger global scheduling

**Creates**: `GlobalScheduleEvent`

### 2. GLOBAL_SCHEDULE (Priority 5)

**Purpose**: Distribute requests across replicas

**Actions**:
- Run global scheduling algorithm
- Assign requests to replicas
- Balance cluster load

**Creates**: `ReplicaScheduleEvent` for affected replicas

### 3. REPLICA_SCHEDULE (Priority 7)

**Purpose**: Schedule requests within a replica

**Actions**:
- Sort requests by policy (FCFS, EDF, LRS, ST)
- Form batches from queued requests
- Initiate batch execution

**Creates**: `BatchStageArrivalEvent` (stage 0)

### 4. BATCH_STAGE_ARRIVAL (Priority 1)

**Purpose**: Batch arrives at pipeline stage

**Actions**:
- Add batch to stage scheduler
- Validate memory availability
- Trigger stage scheduling

**Creates**: `ReplicaStageScheduleEvent`

### 5. REPLICA_STAGE_SCHEDULE (Priority 6)

**Purpose**: Schedule batches within pipeline stage

**Actions**:
- Run stage-specific scheduling
- Form batch stages for execution
- Calculate execution times

**Creates**: `BatchStageEndEvent`

### 6. BATCH_STAGE_END (Priority 3)

**Purpose**: Stage execution completes

**Actions**:
- Update stage completion status
- Handle pipeline transitions
- Record stage metrics

**Creates**:
- `BatchStageArrivalEvent` (if not last stage)
- `BatchEndEvent` (if last stage)
- `ReplicaStageScheduleEvent` (current stage)
- `ReplicaScheduleEvent` (if stage 0)

### 7. BATCH_END (Priority 4)

**Purpose**: Entire batch processing completes

**Actions**:
- Update batch completion status
- Free memory resources
- Handle request completion/preemption

**Creates**: `ReplicaScheduleEvent`

## Request Flow

Complete lifecycle from arrival to completion:

```
RequestArrivalEvent
    ↓
GlobalScheduleEvent
    ↓
ReplicaScheduleEvent
    ↓
BatchStageArrivalEvent (stage 0)
    ↓
ReplicaStageScheduleEvent (stage 0)
    ↓
BatchStageEndEvent (stage 0)
    ↓
[Repeat for stages 1 to N-1]
    ↓
BatchEndEvent
    ↓
ReplicaScheduleEvent
```

## Key Patterns

### Event Cascades

Events generate multiple follow-up events based on system state:

```python
# BatchStageEndEvent example
next_events = [
    ReplicaStageScheduleEvent(stage_id),
]

if is_last_stage:
    next_events.append(BatchEndEvent(batch))
else:
    next_events.append(BatchStageArrivalEvent(stage_id + 1))

if stage_id == 0:
    next_events.append(ReplicaScheduleEvent(replica_id))
```

### Memory Management

- **Allocation**: `ReplicaScheduleEvent` reserves memory
- **Validation**: `BatchStageArrivalEvent` checks availability
- **Deallocation**: `BatchEndEvent` frees resources

### Pipeline Parallelism

- Each stage operates independently
- Events coordinate batch flow between stages
- Stage boundaries serve as synchronization points

## Implementation Details

### Event Queue

- Uses Python `heapq` for priority queue
- O(log n) insertion/extraction
- Automatic priority-based ordering

### Performance Optimizations

- Lightweight event objects
- Conditional metrics collection
- Batch processing for efficiency

### Error Handling

- Memory availability validation
- Request state verification
- Graceful degradation under pressure

## Observability

### Event Tracing

```python
if self._config.metrics_config.write_json_trace:
    self._event_trace.append(event.to_dict())
```

### Chrome Tracing

```python
def to_chrome_trace_events(self) -> dict:
    return self._batch_stage.to_chrome_trace_events(self.time)
```

## Summary

The event system provides:
1. **Modularity**: Clear event responsibilities
2. **Scalability**: Efficient priority queue implementation
3. **Flexibility**: Support for various scheduling policies
4. **Observability**: Comprehensive tracing capabilities
5. **Correctness**: Proper event ordering and state management