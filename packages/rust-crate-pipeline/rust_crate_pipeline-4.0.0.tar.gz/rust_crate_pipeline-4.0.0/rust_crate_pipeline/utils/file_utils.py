# rust_crate_pipeline/utils/file_utils.py
import json
import os
import shutil
from datetime import datetime
from typing import Any, Union


def create_output_dir(base_name: str = "crate_data") -> str:
    """
    Create timestamped output directory

    Args:
        base_name: Base name for output directory

    Returns:
        Path to created directory
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = f"{base_name}_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def save_checkpoint(data: list[dict], prefix: str, output_dir: str) -> str:
    """
    Save processing checkpoint with status metadata

    Args:
        data: List of crate dictionaries
        prefix: File name prefix
        output_dir: Target directory

    Returns:
        Path to saved checkpoint file
    """
    timestamp = datetime.now().isoformat()
    filename = os.path.join(output_dir, f"{prefix}_{timestamp}.jsonl")

    with open(filename, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

    # Save status metadata
    status = {
        "timestamp": timestamp,
        "total_items": len(data),
        "checkpoint_file": filename,
    }

    status_file = os.path.join(output_dir, f"{prefix}_status_{timestamp}.json")
    atomic_write_json(status_file, status)

    return filename


def safe_file_cleanup(path: str) -> None:
    """Safely remove files or directories"""
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    except Exception as e:
        print(f"Failed to cleanup {path}: {str(e)}")


def disk_space_check(min_free_gb: float = 1.0) -> bool:
    """Check if sufficient disk space is available"""
    try:
        free_bytes = shutil.disk_usage(".").free
        free_gb = free_bytes / (1024**3)
        return free_gb >= min_free_gb
    except Exception:
        return True  # Assume OK if check fails


def load_rule_zero_typing_quick_lookup(
    path: Union[str, None] = None,
) -> dict[str, Any]:
    """
    Load the Rule Zero Python Typing & PEP8 Quick Lookup Table as a dict.

    Args:
        path: Optional path to the quick lookup JSON file.

    Returns:
        Dictionary with quick lookup entries.
    """
    if not path:
        path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../rule_zero_typing_quick_lookup.json",
            )
        )
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load Rule Zero typing quick lookup: {e}")
        return {}


def atomic_write_json(path, obj):
    """Write JSON data atomically to avoid corruption on process interruption."""
    import json
    import os
    from tempfile import NamedTemporaryFile

    def json_serializer(o):
        """Custom JSON serializer to handle non-serializable objects."""
        if hasattr(o, "__dict__"):
            return o.__dict__
        elif hasattr(o, "_asdict"):  # namedtuple
            return o._asdict()
        elif hasattr(o, "__str__"):  # Url objects, etc.
            return str(o)
        else:
            return repr(o)

    d = os.path.dirname(path)
    with NamedTemporaryFile("w", delete=False, dir=d, encoding="utf-8") as tmp:
        json.dump(obj, tmp, indent=2, ensure_ascii=False, default=json_serializer)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_name = tmp.name
    os.replace(tmp_name, path)
