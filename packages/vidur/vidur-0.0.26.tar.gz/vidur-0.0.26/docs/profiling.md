# How to add a new model to the simulator?

## Structure of Profiling data

The profiling data is available on our Project Vajra's [HuggingFace hub project](https://huggingface.co/project-vajra). The compute and network profiling data is stores in separate repositories. The dataset identifier contains the model and SKU names for easy identification.

## Adding a new model

We need actual GPUs to get profiling data for a new model. Once the profiling is done, simulations can be run on CPUs only.

> :warning: This profiling path is now broken with the Vajra native backend, we need to repair this flow.

1. Clone the [`sarathi-serve`](https://github.com/microsoft/sarathi-serve) GitHub repo.
    1. Checkout branch [`vidur`](https://github.com/microsoft/sarathi-serve/tree/vidur)
    2. Follow its README to install it.
    3. Let us assume that the Python virtual environment was created in `sarathi-serve/env`.
1. Now clone this repo [`vidur`](https://github.com/project-vajra/vidur) but keep the `sarathi-serve/env` virtual environment activated.
1. Add a YAML model config for the new model in `data/model_configs`.
    - Use the model's HuggingFace model id for the file name eg. `data/model_configs/meta-llama/Llama-2-70b-hf.yml`.
    - Refer HuggingFace `config.json` for the model eg. <https://huggingface.co/meta-llama/Llama-2-70b-hf/blob/main/config.json>.
    - Ensure that correct parameters are set in the YAML file so that the reference transformer model [GPTModel](vidur/profiling/mlp/mlp_impl.py) closely resembles the new model.
    - We use this reference model to profile only the MLP operations of all the models so the attention operations are no-op'ed here.
1. Run the following command to install the simulator in the virtual environment: `python -m pip install -e .` from the `vidur/` directory.
1. For compute profiling (mlp and attention), 1 GPU is enough even for tensor parallel degrees greater than 1. So `num_gpus` set to 1 is sufficient albeit slower for profiling.
1. Now we need to do the MLP profiling:

    ```bash
        python vidur/profiling/mlp/main.py \
        --models codellama/CodeLlama-34b-Instruct-hf \
        --num_gpus 4
    ```

    - Run `python vidur/profiling/mlp/main.py --help` for more options.
    - Copy the CSV file from `profiling_outputs/mlp/<timestamp>/codellama/CodeLlama-34b-Instruct-hf/mlp.csv.xz` to a temporary directory.
1. Now we need to do the attention profiling:

    ```bash
        python vidur/profiling/attention/main.py \
        --models codellama/CodeLlama-34b-Instruct-hf \
        --num_gpus 4
    ```

    - Run `python vidur/profiling/attention/main.py --help` for more options.
    - Copy the CSV file from `profiling_outputs/attention/<timestamp>/codellama/CodeLlama-34b-Instruct-hf/attention.csv.xz` to the same temporary directory created for mlp data.
    - Upload the profiled data using `vidur-data publish compute` command.

## Network (Collectives) profiling

Network profiling is not dependent on the model 🎉. So, we can use the same network profiling data for all models. However, we need to ensure that the network profiling data is available for the node configuration we are using. If not, then we need to profile the network for the device. 1.

For network profiling, the node setup i.e. type of connectivity between the gpus matter. This is why we have the concept of `network_device`. The network_device is an informal name for the network configuration of the node. Eg: `a100_pair_nvlink`, `a100_dgx`, `h100_dgx` etc.
    1. For tensor parallelism, 4 GPUs are needed for TP4 and 8 GPUs are needed for TP8 etc.
    2. For pipeline parallelism across nodes, 2 nodes are needed to profile the link between the nodes.

Currently available data includes:

- `a100_pair_nvlink`: Azure Standard_NC96ads_A100_v4 with 4 80GB A100 PCIe GPUs with pair-wise NVLINK connectivity.
- `h100_pair_nvlink`: Azure internal VM with 4 80GB H100 NVL GPUs with pair-wise NVLINK connectivity.
- `a100_dgx`: A100 DGX with 8 80GB A100s.
- `h100_dgx`: H100 DGX with 8 H100s.

### Steps to profile:

1. Clone this (`vidur`) repo and create a Python virtual environment as in [Setup](README.md).
1. Setup a ray cluster:
    1. Tensor parallelism is typically done on a single node so we don't need a multi-node cluster.
    1. However, pipeline parallelism is typically done across multiple nodes so we need at least 2 nodes there.
    1. Run `ray start --head` from the root node.
    1. Run `ray start --address <head-node-ip>:<head-node-port>` from the other nodes. The other nodes also need to have the same git commit checked out.
1. Run the following command to profile for the `all_reduce` operation, (sufficient for TP):
 
    ```bash
        python vidur/profiling/collectives/main.py \
        --num_workers_per_node_combinations 1,2,4,8 \
        --collective all_reduce
    ```

    - One may need to adjust `--num_workers_per_node_combinations` depending on the number of GPUs in the node eg. `--num_workers_per_node_combinations 1,2,4` for Azure Standard_NC96ads_A100_v4 node.
    - Copy the CSV file from `profiling_outputs/collectives/<timestamp>/all_reduce.csv` to a temporary directory.
    - Run `python vidur/profiling/collectives/main.py --help` for more options.
1. Run the following command to profile for the `send_recv` operation, (required only for PP):

    ```bash
        python vidur/profiling/collectives/main.py \
        --num_workers_per_node_combinations 1,2,4,8 \
        --collective send_recv
    ```

    - Typically, PP is done across nodes so `num_workers_per_node_combinations` should be the same as the number of GPUs available in one node. Profiling `num_workers_per_node_combinations` less than the number of GPUs in the node to have PP inside a node. This can be useful when each gpu is not connected to every other gpu using the same high speed link.
    - Copy the CSV file from `profiling_outputs/collectives/<timestamp>/send_recv.csv` to same directory created for all_reduce data.
    - Upload the profiled data using `vidur-data network compute` command.
