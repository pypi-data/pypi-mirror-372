#include <cassert>
#include <vidur/config/config.h>

int main()
{
    // Create ReplicaConfig
    vidur::config::ReplicaConfig replica_config(1, 2, 4);

    assert(replica_config.num_pipeline_stages == 1);
    assert(replica_config.tensor_parallel_size == 2);
    assert(replica_config.kv_parallel_size == 4);

    return 0;
}