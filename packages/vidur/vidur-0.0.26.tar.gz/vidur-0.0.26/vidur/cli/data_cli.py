import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import click

from vidur.utils import parse_metadata, sanitize_name
from vidur.utils.hf_dataset_utils import upload_dataset


@click.group()
def cli():
    """Vidur Data Management CLI"""
    pass


# ========================
# PUBLISH COMMANDS
# ========================


@cli.group()
def publish():
    """Publish datasets to Hugging Face Hub"""
    pass


@publish.command()
@click.option("--org", required=True, help="Target organization on HF Hub")
@click.option(
    "--collection", required=True, help="Dataset version/collection (e.g. v1.0)"
)
@click.option(
    "--model", required=True, help="Model identifier (e.g. meta-llama/Llama-2-70b-hf)"
)
@click.option("--device", required=True, help="Device SKU (e.g. h100, a100-80gb)")
@click.option(
    "--data-path",
    type=click.Path(exists=True),
    required=True,
    help="Path to model-device data directory",
)
@click.option(
    "--use-private-repo", is_flag=True, help="Make the dataset private", default=False
)
@click.option("--metadata", multiple=True, help="Additional metadata key=value pairs")
def compute(org, collection, model, device, data_path, use_private_repo, metadata):
    """Publish compute profiling data for a model-device pair"""
    # Create standardized repo identifier
    repo_id = f"{sanitize_name(org)}/{sanitize_name(collection)}-{sanitize_name(model)}-{sanitize_name(device)}"
    # Parse additional metadata
    metadata_dict = parse_metadata(metadata)

    # Create config.json
    config = {
        "schema_version": "1.0",
        "model": model,
        "device_sku": device,
        "dataset_type": "compute",
        **metadata_dict,
    }

    upload_dataset(
        repo_id=repo_id,
        config=config,
        data_path=data_path,
        use_private_repo=use_private_repo,
    )

    click.echo(f"✅ Published compute data to: {repo_id}")


@publish.command()
@click.option("--org", required=True, help="Target organization on HF Hub")
@click.option(
    "--collection", required=True, help="Dataset version/collection (e.g. v1.0)"
)
@click.option(
    "--sku", required=True, help="Hardware config (e.g. h100-dgx, a100-nvlink-pair)"
)
@click.option(
    "--data-path",
    type=click.Path(exists=True),
    required=True,
    help="Path to network benchmark data",
)
@click.option(
    "--use-private-repo", is_flag=True, help="Make the dataset private", default=False
)
@click.option("--metadata", multiple=True, help="Additional metadata key=value pairs")
def network(org, collection, sku, data_path, use_private_repo, metadata):
    """Publish network performance data"""
    repo_id = f"{sanitize_name(org)}/{sanitize_name(collection)}-{sanitize_name(sku)}"
    # Parse additional metadata
    metadata_dict = parse_metadata(metadata)
    # Create config.json
    config = {
        "schema_version": "1.0",
        "sku": sku,
        "dataset_type": "network",
        **metadata_dict,
    }

    upload_dataset(
        repo_id=repo_id,
        config=config,
        data_path=data_path,
        use_private_repo=use_private_repo,
    )

    click.echo(f"✅ Published network data to: {repo_id}")


if __name__ == "__main__":
    cli()
