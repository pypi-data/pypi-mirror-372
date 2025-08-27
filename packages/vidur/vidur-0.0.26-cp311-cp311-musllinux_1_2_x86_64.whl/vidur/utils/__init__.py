import re


def sanitize_name(name: str) -> str:
    """Convert to lowercase and replace special characters with hyphens"""
    return re.sub(r"[^a-zA-Z0-9]", "-", name).lower()


def parse_metadata(metadata: list) -> dict:
    """Parse metadata key-value pairs of the form key=value"""
    metadata_dict = {}
    for item in metadata:
        if "=" not in item:
            raise ValueError(f"Metadata must be in key=value format. Got: {item}")
        key, value = item.split("=", 1)
        metadata_dict[key.strip()] = value.strip()
    return metadata_dict
