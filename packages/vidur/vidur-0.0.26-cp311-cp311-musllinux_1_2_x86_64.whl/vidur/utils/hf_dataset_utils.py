import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from huggingface_hub import HfApi, upload_folder

from vidur.utils import sanitize_name


def upload_dataset(
    repo_id: str,
    config: dict,
    data_path: str,
    use_private_repo: bool = True,
    commit_message: str = "Published dataset",
):
    api = HfApi()

    # Create repo with Vidur naming conventions
    api.create_repo(
        repo_id=repo_id, repo_type="dataset", exist_ok=True, private=use_private_repo
    )

    # Create temp directory with data + config
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Copy user's data
        shutil.copytree(data_path, tmp_dir, dirs_exist_ok=True)

        # Add config.json
        config_path = Path(tmp_dir) / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        upload_folder(
            folder_path=tmp_dir,
            repo_id=repo_id,
            repo_type="dataset",
            commit_message=commit_message,
        )
