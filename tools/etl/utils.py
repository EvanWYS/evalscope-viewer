"""
Utility functions for ETL pipeline
"""

import json
from pathlib import Path
from typing import Any, Dict, List


def load_json(file_path: Path) -> Dict[str, Any]:
    """
    Load JSON file

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path: Path, data: Dict[str, Any], indent: int = 2):
    """
    Save data to JSON file

    Args:
        file_path: Path to output JSON file
        data: Data to save
        indent: JSON indentation (default: 2)
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_jsonl(file_path: Path) -> List[Dict[str, Any]]:
    """
    Load JSONL file

    Args:
        file_path: Path to JSONL file

    Returns:
        List of parsed JSON objects
    """
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def save_jsonl(file_path: Path, data: List[Dict[str, Any]]):
    """
    Save data to JSONL file

    Args:
        file_path: Path to output JSONL file
        data: List of data objects to save
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        for item in data:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")


def scan_directories(base_dir: Path, pattern: str = "*") -> List[Path]:
    """
    Scan directories matching a pattern

    Args:
        base_dir: Base directory to scan
        pattern: Glob pattern (default: "*")

    Returns:
        List of matching directory paths
    """
    if not base_dir.exists():
        return []

    return sorted([p for p in base_dir.glob(pattern) if p.is_dir()])
