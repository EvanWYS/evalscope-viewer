"""
Standard JSON Schema Definition

Defines the framework-agnostic data protocol that all adapters must output.
This ensures consistency across different evaluation frameworks.
"""

SCHEMA_VERSION = "1.0"

# Schema for index.json
INDEX_SCHEMA = {
    "type": "object",
    "properties": {
        "runs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "run_id": {"type": "string"},
                    "timestamp": {"type": "string"},
                    "framework": {"type": "string"},
                    "model": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                        },
                    },
                    "datasets": {"type": "array", "items": {"type": "string"}},
                    "overall_score": {"type": "number"},
                    "num_samples": {"type": "integer"},
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                    "duration_seconds": {"type": "number"},
                    "status": {"type": "string", "enum": ["completed", "failed", "running"]},
                },
                "required": ["run_id", "timestamp", "framework", "model", "datasets", "status"],
            },
        },
        "total": {"type": "integer"},
        "last_updated": {"type": "string"},
    },
    "required": ["runs", "total", "last_updated"],
}

# Schema for meta.json
META_SCHEMA = {
    "type": "object",
    "properties": {
        "schema_version": {"type": "string"},
        "run_id": {"type": "string"},
        "timestamp": {"type": "string"},
        "framework": {"type": "string"},
        "framework_version": {"type": "string"},
        "model": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "revision": {"type": "string"},
                "type": {"type": "string"},
            },
        },
        "datasets": {"type": "array", "items": {"type": "string"}},
        "config": {"type": "object"},
        "start_time": {"type": "string"},
        "end_time": {"type": "string"},
        "duration_seconds": {"type": "number"},
        "status": {"type": "string"},
    },
    "required": ["schema_version", "run_id", "timestamp", "framework", "model", "datasets", "status"],
}

# Schema for eval_summary.json
EVAL_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "schema_version": {"type": "string"},
        "run_id": {"type": "string"},
        "datasets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "dataset": {"type": "string"},
                    "dataset_pretty_name": {"type": "string"},
                    "metrics": {"type": "object"},
                    "overall_score": {"type": "number"},
                    "categories": {"type": "array"},
                },
                "required": ["dataset", "metrics", "overall_score"],
            },
        },
        "overall": {
            "type": "object",
            "properties": {
                "avg_score": {"type": "number"},
                "total_samples": {"type": "integer"},
            },
        },
    },
    "required": ["schema_version", "run_id", "datasets", "overall"],
}
