# ETL 数据协议完整定义

本文档详细定义了从 evalscope 原始输出到前端静态 JSON 的完整数据转换协议。

---

## 1. evalscope 原始输出结构

基于 evalscope v1.0+ 的实际源码分析，评测完成后会生成以下目录结构：

```
outputs/
  <timestamp>/                    # 例如：20251124_143025
    ├── configs/
    │   └── task_config_<hash>.yaml
    ├── logs/
    │   └── eval_log.log
    ├── predictions/
    │   └── <model_name>/
    │       └── <dataset_name>.jsonl
    ├── reviews/
    │   └── <model_name>/
    │       └── <dataset_name>.jsonl
    └── reports/
        └── <model_name>/
            └── <dataset_name>.json
```

### 1.1 配置文件（configs/task_config_*.yaml）

记录完整的评测任务配置：

```yaml
# 评测配置示例
model:
  model_id: "Qwen/Qwen2.5-7B-Instruct"
  model_revision: "master"
  device_map: "auto"
  generation_config:
    do_sample: false
    max_new_tokens: 512
    temperature: 0.0

eval:
  datasets: ["mmlu", "gsm8k", "humaneval"]
  eval_batch_size: 4
  limit: null
  seed: 42

eval_type: "openai_api"
work_dir: "./outputs/20251124_143025"
```

**关键字段**：
- `model.model_id`: 模型标识符
- `model.model_revision`: 模型版本
- `model.generation_config`: 生成配置
- `eval.datasets`: 评测数据集列表
- `eval.seed`: 随机种子
- `work_dir`: 输出目录

### 1.2 日志文件（logs/eval_log.log）

评测过程的完整日志，包含：
- 时间戳
- 日志级别（INFO, WARNING, ERROR）
- 评测进度信息
- 错误和异常信息

```
2025-11-24 14:30:25,123 - INFO - Start evaluating benchmark: mmlu
2025-11-24 14:30:26,456 - INFO - Processing 1000 samples
2025-11-24 14:35:12,789 - INFO - Benchmark mmlu evaluation finished.
```

### 1.3 预测结果（predictions/<model_name>/<dataset_name>.jsonl）

每行是一个样本的预测结果（JSON Lines 格式）：

```jsonl
{"id": 0, "input": "What is the capital of France?", "target": "Paris", "prediction": "Paris", "choices": ["London", "Berlin", "Paris", "Madrid"], "metadata": {"category": "geography", "difficulty": "easy"}}
{"id": 1, "input": "What is 2+2?", "target": "4", "prediction": "4", "choices": null, "metadata": {"category": "math", "difficulty": "easy"}}
```

**关键字段**：
- `id`: 样本唯一标识
- `input`: 输入（可以是字符串或消息列表）
- `target`: 目标答案（单个或多个）
- `prediction`: 模型预测结果
- `choices`: 选项列表（多选题）
- `metadata`: 样本元数据（类别、难度等）

### 1.4 评审结果（reviews/<model_name>/<dataset_name>.jsonl）

每行是一个样本的评分结果：

```jsonl
{"id": 0, "sample_scores": {"accuracy": 1.0, "exact_match": 1.0}, "metadata": {"judge_type": "exact_match"}}
{"id": 1, "sample_scores": {"accuracy": 1.0, "exact_match": 1.0}, "metadata": {"judge_type": "exact_match"}}
```

**关键字段**：
- `id`: 样本 ID（对应 predictions 中的 id）
- `sample_scores`: 样本级别的评分字典
- `metadata`: 评分元数据

### 1.5 评估报告（reports/<model_name>/<dataset_name>.json）

聚合后的评估报告，结构化的评测结果：

```json
{
  "name": "mmlu_report_20251124_143025",
  "dataset_name": "mmlu",
  "dataset_pretty_name": "MMLU (Massive Multitask Language Understanding)",
  "dataset_description": "A comprehensive benchmark covering 57 subjects",
  "model_name": "Qwen/Qwen2.5-7B-Instruct",
  "score": 0.7234,
  "metrics": [
    {
      "name": "accuracy",
      "num": 14042,
      "score": 0.7234,
      "macro_score": 0.7189,
      "categories": [
        {
          "name": ["STEM"],
          "num": 4321,
          "score": 0.6891,
          "macro_score": 0.6845,
          "subsets": [
            {
              "name": "abstract_algebra",
              "score": 0.3200,
              "num": 100
            },
            {
              "name": "astronomy",
              "score": 0.6711,
              "num": 152
            }
          ]
        },
        {
          "name": ["Humanities"],
          "num": 3789,
          "score": 0.7123,
          "macro_score": 0.7089,
          "subsets": [
            {
              "name": "formal_logic",
              "score": 0.4127,
              "num": 126
            },
            {
              "name": "high_school_european_history",
              "score": 0.7576,
              "num": 165
            }
          ]
        }
      ]
    }
  ],
  "analysis": "根据评测结果，该模型在 MMLU 基准测试中整体表现良好..."
}
```

**数据结构层次**：
- **Report**: 顶层报告
  - `name`: 报告名称
  - `dataset_name`: 数据集名称
  - `dataset_pretty_name`: 数据集显示名称
  - `model_name`: 模型名称
  - `score`: 总体得分（使用第一个 metric 的 score）
  - `metrics[]`: 指标列表

- **Metric**: 评测指标
  - `name`: 指标名称（accuracy, f1, bleu 等）
  - `num`: 样本总数
  - `score`: 微平均得分（weighted by sample count）
  - `macro_score`: 宏平均得分（simple average）
  - `categories[]`: 类别列表

- **Category**: 类别分组
  - `name`: 类别名称（tuple 格式，支持多层级）
  - `num`: 该类别样本数
  - `score`: 微平均得分
  - `macro_score`: 宏平均得分
  - `subsets[]`: 子集列表

- **Subset**: 最细粒度的评测子集
  - `name`: 子集名称
  - `score`: 该子集得分
  - `num`: 样本数量

---

## 2. ETL 转换映射规则

从 evalscope 原始输出到前端静态 JSON 的转换逻辑。

### 2.1 run_id 生成规则

```python
# run_id 格式：run_<timestamp>_<model_hash>
# 例如：run_20251124_143025_qwen7b

def generate_run_id(timestamp: str, model_id: str) -> str:
    """
    生成唯一的 run_id

    Args:
        timestamp: evalscope 输出目录的时间戳（YYYYMMDD_HHMMSS）
        model_id: 模型标识符

    Returns:
        run_id: 格式化的运行 ID
    """
    model_hash = hashlib.md5(model_id.encode()).hexdigest()[:8]
    return f"run_{timestamp}_{model_hash}"
```

### 2.2 元数据提取（meta.json）

**数据来源**：`configs/task_config_*.yaml`

**转换逻辑**：

```python
def extract_meta(config_yaml_path: str, timestamp: str) -> dict:
    """
    从配置文件提取元数据

    输入：configs/task_config_*.yaml
    输出：meta.json
    """
    config = yaml.safe_load(open(config_yaml_path))

    return {
        "run_id": generate_run_id(timestamp, config["model"]["model_id"]),
        "timestamp": timestamp,
        "model": {
            "name": config["model"]["model_id"],
            "revision": config["model"].get("model_revision", "master"),
            "type": config.get("eval_type", "unknown")
        },
        "datasets": config["eval"]["datasets"],
        "config": {
            "eval_batch_size": config["eval"].get("eval_batch_size", 1),
            "seed": config["eval"].get("seed", None),
            "limit": config["eval"].get("limit", None),
            "generation_config": config["model"].get("generation_config", {})
        },
        "start_time": parse_timestamp_from_log_start(logs_dir),
        "end_time": parse_timestamp_from_log_end(logs_dir),
        "status": "completed"
    }
```

### 2.3 评估摘要提取（eval_summary.json）

**数据来源**：`reports/<model_name>/<dataset_name>.json`

**转换逻辑**：

```python
def extract_eval_summary(reports_dir: str, run_id: str) -> dict:
    """
    从报告目录提取所有数据集的评估摘要

    输入：reports/<model_name>/*.json
    输出：eval_summary.json
    """
    summaries = []

    # 遍历所有报告文件
    for report_file in glob(f"{reports_dir}/**/*.json"):
        report = json.load(open(report_file))

        # 提取主要指标
        primary_metric = report["metrics"][0]

        summary = {
            "dataset": report["dataset_name"],
            "dataset_pretty_name": report.get("dataset_pretty_name", ""),
            "metrics": {
                metric["name"]: {
                    "score": metric["score"],
                    "macro_score": metric["macro_score"],
                    "num_samples": metric["num"]
                }
                for metric in report["metrics"]
            },
            "overall_score": report["score"],
            "categories": []
        }

        # 提取类别级别的详细信息
        for category in primary_metric["categories"]:
            cat_info = {
                "name": category["name"],
                "score": category["score"],
                "macro_score": category["macro_score"],
                "num_samples": category["num"],
                "subsets": [
                    {
                        "name": subset["name"],
                        "score": subset["score"],
                        "num": subset["num"]
                    }
                    for subset in category["subsets"]
                ]
            }
            summary["categories"].append(cat_info)

        summaries.append(summary)

    return {
        "run_id": run_id,
        "datasets": summaries,
        "overall": {
            "avg_score": sum(s["overall_score"] for s in summaries) / len(summaries),
            "total_samples": sum(
                s["metrics"][list(s["metrics"].keys())[0]]["num_samples"]
                for s in summaries
            )
        }
    }
```

### 2.4 样本抽样（samples_head.jsonl）

**数据来源**：`predictions/<model_name>/<dataset_name>.jsonl` + `reviews/<model_name>/<dataset_name>.jsonl`

**转换逻辑**：

```python
def extract_samples(predictions_dir: str, reviews_dir: str,
                   dataset_name: str, head_limit: int = 100) -> list:
    """
    从预测和评审结果中提取样本

    输入：
    - predictions/<model>/<dataset>.jsonl
    - reviews/<model>/<dataset>.jsonl

    输出：samples_head.jsonl（前 N 条）
    """
    # 读取预测和评审结果
    predictions = read_jsonl(f"{predictions_dir}/**/{dataset_name}.jsonl")
    reviews = read_jsonl(f"{reviews_dir}/**/{dataset_name}.jsonl")

    # 合并数据（按 id）
    reviews_dict = {r["id"]: r for r in reviews}

    samples = []
    for pred in predictions[:head_limit]:
        sample_id = pred["id"]
        review = reviews_dict.get(sample_id, {})

        sample = {
            "id": sample_id,
            "input": pred["input"],
            "target": pred["target"],
            "prediction": pred["prediction"],
            "scores": review.get("sample_scores", {}),
            "metadata": {
                **pred.get("metadata", {}),
                **review.get("metadata", {})
            }
        }

        # 如果是多选题，添加 choices
        if pred.get("choices"):
            sample["choices"] = pred["choices"]

        samples.append(sample)

    return samples
```

### 2.5 训练曲线数据（metrics.json）

**注意**：evalscope 主要用于评估，不直接产出训练曲线。如果需要训练曲线，数据应该来自训练日志。

**数据来源**：训练框架的日志文件（如 tensorboard events, wandb logs）

**转换逻辑**：

```python
def extract_training_metrics(training_log_path: str) -> dict:
    """
    从训练日志提取训练曲线数据

    注意：这部分需要根据实际训练框架调整
    可能的数据源：
    - TensorBoard events
    - WandB logs
    - 自定义训练日志
    """
    series = []

    # 示例：从 tensorboard events 提取
    # from tensorboard.backend.event_processing import event_accumulator
    # ea = event_accumulator.EventAccumulator(training_log_path)
    # ea.Reload()

    # for tag in ea.Tags()['scalars']:
    #     events = ea.Scalars(tag)
    #     points = [
    #         {"step": e.step, "value": e.value, "timestamp": e.wall_time}
    #         for e in events
    #     ]
    #     series.append({"name": tag, "points": points})

    return {
        "series": series,
        "source": "tensorboard"  # or "wandb", "custom"
    }
```

---

## 3. 前端静态 JSON 协议

前端直接读取的标准化 JSON 格式。

### 3.1 目录结构

```
web/public/data/
  ├── index.json                    # 所有 run 的索引
  └── runs/
      └── <run_id>/
          ├── meta.json              # 运行元信息
          ├── eval_summary.json      # 评估摘要
          ├── metrics.json           # 训练曲线（可选）
          └── samples/
              ├── <dataset_1>_head.jsonl
              ├── <dataset_2>_head.jsonl
              └── ...
```

### 3.2 index.json（运行列表索引）

```json
{
  "runs": [
    {
      "run_id": "run_20251124_143025_a1b2c3d4",
      "timestamp": "20251124_143025",
      "model": {
        "name": "Qwen/Qwen2.5-7B-Instruct",
        "type": "openai_api"
      },
      "datasets": ["mmlu", "gsm8k", "humaneval"],
      "overall_score": 0.6823,
      "num_samples": 15234,
      "start_time": "2025-11-24T14:30:25Z",
      "end_time": "2025-11-24T16:45:12Z",
      "duration_seconds": 8087,
      "status": "completed",
      "tags": []
    }
  ],
  "total": 1,
  "last_updated": "2025-11-24T16:45:15Z"
}
```

**字段说明**：
- `runs[]`: 运行列表
  - `run_id`: 唯一运行标识符
  - `timestamp`: 运行时间戳
  - `model.name`: 模型名称
  - `model.type`: 模型类型（openai_api, llm_ckpt 等）
  - `datasets[]`: 评测数据集列表
  - `overall_score`: 总体平均分
  - `num_samples`: 总样本数
  - `start_time`: 开始时间（ISO 8601）
  - `end_time`: 结束时间（ISO 8601）
  - `duration_seconds`: 运行时长（秒）
  - `status`: 运行状态（completed, failed, running）
  - `tags[]`: 标签列表（用于筛选和分组）

### 3.3 meta.json（运行元信息）

```json
{
  "run_id": "run_20251124_143025_a1b2c3d4",
  "timestamp": "20251124_143025",
  "model": {
    "name": "Qwen/Qwen2.5-7B-Instruct",
    "revision": "master",
    "type": "openai_api"
  },
  "datasets": ["mmlu", "gsm8k", "humaneval"],
  "config": {
    "eval_batch_size": 4,
    "seed": 42,
    "limit": null,
    "generation_config": {
      "do_sample": false,
      "max_new_tokens": 512,
      "temperature": 0.0,
      "top_p": 1.0
    }
  },
  "start_time": "2025-11-24T14:30:25Z",
  "end_time": "2025-11-24T16:45:12Z",
  "duration_seconds": 8087,
  "status": "completed",
  "tags": [],
  "environment": {
    "evalscope_version": "1.0.0",
    "python_version": "3.10.12",
    "cuda_version": "12.1"
  }
}
```

### 3.4 eval_summary.json（评估摘要）

```json
{
  "run_id": "run_20251124_143025_a1b2c3d4",
  "datasets": [
    {
      "dataset": "mmlu",
      "dataset_pretty_name": "MMLU (Massive Multitask Language Understanding)",
      "metrics": {
        "accuracy": {
          "score": 0.7234,
          "macro_score": 0.7189,
          "num_samples": 14042
        }
      },
      "overall_score": 0.7234,
      "categories": [
        {
          "name": ["STEM"],
          "score": 0.6891,
          "macro_score": 0.6845,
          "num_samples": 4321,
          "subsets": [
            {
              "name": "abstract_algebra",
              "score": 0.3200,
              "num": 100
            },
            {
              "name": "astronomy",
              "score": 0.6711,
              "num": 152
            },
            {
              "name": "college_biology",
              "score": 0.7361,
              "num": 144
            }
          ]
        },
        {
          "name": ["Humanities"],
          "score": 0.7123,
          "macro_score": 0.7089,
          "num_samples": 3789,
          "subsets": [
            {
              "name": "formal_logic",
              "score": 0.4127,
              "num": 126
            },
            {
              "name": "high_school_european_history",
              "score": 0.7576,
              "num": 165
            }
          ]
        },
        {
          "name": ["Social Sciences"],
          "score": 0.7456,
          "macro_score": 0.7412,
          "num_samples": 3187,
          "subsets": [
            {
              "name": "econometrics",
              "score": 0.4737,
              "num": 114
            },
            {
              "name": "high_school_geography",
              "score": 0.7879,
              "num": 198
            }
          ]
        },
        {
          "name": ["Other"],
          "score": 0.7301,
          "macro_score": 0.7245,
          "num_samples": 2745,
          "subsets": [
            {
              "name": "business_ethics",
              "score": 0.6200,
              "num": 100
            },
            {
              "name": "clinical_knowledge",
              "score": 0.7019,
              "num": 265
            }
          ]
        }
      ]
    },
    {
      "dataset": "gsm8k",
      "dataset_pretty_name": "GSM8K (Grade School Math 8K)",
      "metrics": {
        "accuracy": {
          "score": 0.5847,
          "macro_score": 0.5847,
          "num_samples": 1319
        }
      },
      "overall_score": 0.5847,
      "categories": [
        {
          "name": ["default"],
          "score": 0.5847,
          "macro_score": 0.5847,
          "num_samples": 1319,
          "subsets": [
            {
              "name": "test",
              "score": 0.5847,
              "num": 1319
            }
          ]
        }
      ]
    },
    {
      "dataset": "humaneval",
      "dataset_pretty_name": "HumanEval (Coding)",
      "metrics": {
        "pass@1": {
          "score": 0.4512,
          "macro_score": 0.4512,
          "num_samples": 164
        }
      },
      "overall_score": 0.4512,
      "categories": [
        {
          "name": ["default"],
          "score": 0.4512,
          "macro_score": 0.4512,
          "num_samples": 164,
          "subsets": [
            {
              "name": "test",
              "score": 0.4512,
              "num": 164
            }
          ]
        }
      ]
    }
  ],
  "overall": {
    "avg_score": 0.5864,
    "total_samples": 15525
  }
}
```

**字段说明**：
- `datasets[]`: 每个数据集的详细评估结果
  - `dataset`: 数据集名称
  - `dataset_pretty_name`: 显示名称
  - `metrics{}`: 指标字典（支持多指标）
  - `overall_score`: 该数据集总体得分
  - `categories[]`: 类别分解
    - `name`: 类别名称（支持多层级）
    - `score`: 微平均得分
    - `macro_score`: 宏平均得分
    - `num_samples`: 样本数
    - `subsets[]`: 子集详情
- `overall`: 全局统计
  - `avg_score`: 所有数据集的平均分
  - `total_samples`: 总样本数

### 3.5 metrics.json（训练曲线，可选）

```json
{
  "run_id": "run_20251124_143025_a1b2c3d4",
  "source": "tensorboard",
  "series": [
    {
      "name": "train/loss",
      "type": "scalar",
      "points": [
        {
          "step": 0,
          "value": 2.8934,
          "timestamp": "2025-11-24T10:15:23Z"
        },
        {
          "step": 100,
          "value": 2.1234,
          "timestamp": "2025-11-24T10:20:45Z"
        },
        {
          "step": 200,
          "value": 1.8765,
          "timestamp": "2025-11-24T10:26:12Z"
        }
      ]
    },
    {
      "name": "train/learning_rate",
      "type": "scalar",
      "points": [
        {
          "step": 0,
          "value": 0.0,
          "timestamp": "2025-11-24T10:15:23Z"
        },
        {
          "step": 100,
          "value": 3e-5,
          "timestamp": "2025-11-24T10:20:45Z"
        }
      ]
    },
    {
      "name": "eval/accuracy",
      "type": "scalar",
      "points": [
        {
          "step": 500,
          "value": 0.6234,
          "timestamp": "2025-11-24T11:30:00Z"
        },
        {
          "step": 1000,
          "value": 0.7123,
          "timestamp": "2025-11-24T12:45:00Z"
        }
      ]
    }
  ]
}
```

**字段说明**：
- `source`: 数据来源（tensorboard, wandb, custom）
- `series[]`: 时间序列列表
  - `name`: 指标名称（建议使用 / 分隔，如 train/loss）
  - `type`: 数据类型（scalar, histogram 等）
  - `points[]`: 数据点
    - `step`: 训练步数
    - `value`: 指标值
    - `timestamp`: 时间戳（可选）

### 3.6 samples/<dataset>_head.jsonl（样本抽样）

每个数据集一个 JSONL 文件，每行一个样本：

```jsonl
{"id": 0, "input": "What is the capital of France?", "target": "Paris", "prediction": "Paris", "scores": {"accuracy": 1.0, "exact_match": 1.0}, "metadata": {"category": "geography", "difficulty": "easy"}, "choices": ["London", "Berlin", "Paris", "Madrid"]}
{"id": 1, "input": "What is 2+2?", "target": "4", "prediction": "4", "scores": {"accuracy": 1.0}, "metadata": {"category": "math", "difficulty": "easy"}}
{"id": 5, "input": "Explain quantum entanglement.", "target": "Quantum entanglement is a phenomenon...", "prediction": "Quantum entanglement refers to...", "scores": {"accuracy": 0.85, "bleu": 0.72}, "metadata": {"category": "physics", "difficulty": "hard"}}
```

**字段说明**：
- `id`: 样本唯一标识
- `input`: 输入内容
- `target`: 目标答案
- `prediction`: 模型预测
- `scores{}`: 样本级别的评分
- `metadata{}`: 样本元数据
- `choices[]`: 选项（仅多选题）

---

## 4. ETL 脚本实现参考

### 4.1 脚本结构

```
tools/etl/
  ├── build_static_data.py        # 主入口
  ├── extractors/
  │   ├── __init__.py
  │   ├── config_extractor.py     # 配置提取
  │   ├── report_extractor.py     # 报告提取
  │   └── sample_extractor.py     # 样本提取
  ├── transformers/
  │   ├── __init__.py
  │   ├── meta_transformer.py     # 元数据转换
  │   └── summary_transformer.py  # 摘要转换
  └── loaders/
      ├── __init__.py
      └── json_loader.py          # JSON 写入
```

### 4.2 主脚本示例（build_static_data.py）

```python
#!/usr/bin/env python3
"""
ETL 脚本：将 evalscope 原始输出转换为前端静态 JSON
"""
import argparse
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict

def parse_args():
    parser = argparse.ArgumentParser(description="Build static data for evalscope viewer")
    parser.add_argument(
        "--raw-dir",
        type=str,
        required=True,
        help="evalscope 输出目录（包含多个 timestamp 子目录）"
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        required=True,
        help="前端静态数据输出目录"
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=100,
        help="每个数据集抽样的样本数量"
    )
    return parser.parse_args()

def scan_evalscope_runs(raw_dir: str) -> List[str]:
    """扫描所有 evalscope 运行目录"""
    runs = []
    for item in Path(raw_dir).iterdir():
        if item.is_dir() and item.name.match(r'\d{8}_\d{6}'):
            runs.append(str(item))
    return sorted(runs)

def process_run(run_dir: str, out_dir: str, sample_limit: int) -> Dict:
    """处理单个运行"""
    from extractors import extract_config, extract_reports, extract_samples
    from transformers import build_meta, build_eval_summary
    from loaders import write_json, write_jsonl

    # 1. Extract
    config = extract_config(run_dir)
    reports = extract_reports(run_dir)
    samples = extract_samples(run_dir, sample_limit)

    # 2. Transform
    meta = build_meta(config, run_dir)
    eval_summary = build_eval_summary(reports, meta["run_id"])

    # 3. Load
    run_out_dir = Path(out_dir) / "runs" / meta["run_id"]
    run_out_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_out_dir / "meta.json", meta)
    write_json(run_out_dir / "eval_summary.json", eval_summary)

    # 写入样本
    samples_dir = run_out_dir / "samples"
    samples_dir.mkdir(exist_ok=True)
    for dataset_name, dataset_samples in samples.items():
        write_jsonl(samples_dir / f"{dataset_name}_head.jsonl", dataset_samples)

    # 返回 index 条目
    return {
        "run_id": meta["run_id"],
        "timestamp": meta["timestamp"],
        "model": meta["model"],
        "datasets": meta["datasets"],
        "overall_score": eval_summary["overall"]["avg_score"],
        "num_samples": eval_summary["overall"]["total_samples"],
        "start_time": meta["start_time"],
        "end_time": meta["end_time"],
        "status": meta["status"]
    }

def build_index(runs: List[Dict], out_dir: str):
    """构建索引文件"""
    index = {
        "runs": runs,
        "total": len(runs),
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }

    with open(Path(out_dir) / "index.json", "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

def main():
    args = parse_args()

    # 扫描所有运行
    run_dirs = scan_evalscope_runs(args.raw_dir)
    print(f"Found {len(run_dirs)} evalscope runs")

    # 处理每个运行
    index_entries = []
    for run_dir in run_dirs:
        print(f"Processing {run_dir}...")
        entry = process_run(run_dir, args.out_dir, args.sample_limit)
        index_entries.append(entry)

    # 构建索引
    build_index(index_entries, args.out_dir)
    print(f"ETL completed. Output: {args.out_dir}")

if __name__ == "__main__":
    main()
```

### 4.3 使用示例

```bash
# 基础用法
python tools/etl/build_static_data.py \
  --raw-dir ./outputs \
  --out-dir ./web/public/data

# 指定样本抽样数量
python tools/etl/build_static_data.py \
  --raw-dir ./outputs \
  --out-dir ./web/public/data \
  --sample-limit 200

# 增量更新（只处理新的运行）
python tools/etl/build_static_data.py \
  --raw-dir ./outputs \
  --out-dir ./web/public/data \
  --incremental
```

---

## 5. 前端使用示例

### 5.1 获取运行列表

```typescript
// app/runs/page.tsx
async function getRunsList() {
  const res = await fetch('/data/index.json');
  const data = await res.json();
  return data.runs;
}
```

### 5.2 获取单个运行详情

```typescript
// app/runs/[runId]/page.tsx
async function getRunDetails(runId: string) {
  const [meta, summary] = await Promise.all([
    fetch(`/data/runs/${runId}/meta.json`).then(r => r.json()),
    fetch(`/data/runs/${runId}/eval_summary.json`).then(r => r.json())
  ]);
  return { meta, summary };
}
```

### 5.3 获取样本数据

```typescript
// app/runs/[runId]/samples/page.tsx
async function getDatasetSamples(runId: string, dataset: string) {
  const res = await fetch(`/data/runs/${runId}/samples/${dataset}_head.jsonl`);
  const text = await res.text();
  return text.split('\n')
    .filter(line => line.trim())
    .map(line => JSON.parse(line));
}
```

---

## 6. 数据协议版本管理

### 6.1 版本号规范

所有 JSON 文件应包含 `schema_version` 字段：

```json
{
  "schema_version": "1.0",
  "run_id": "...",
  ...
}
```

版本号格式：`<major>.<minor>`
- major 变更：不兼容的结构变化
- minor 变更：向后兼容的新增字段

### 6.2 版本兼容性

前端应检查版本并提供降级方案：

```typescript
function parseRunMeta(data: any) {
  const version = data.schema_version || "1.0";

  if (version.startsWith("1.")) {
    return parseV1Meta(data);
  } else if (version.startsWith("2.")) {
    return parseV2Meta(data);
  } else {
    throw new Error(`Unsupported schema version: ${version}`);
  }
}
```

---

## 7. 总结

本协议定义了从 evalscope 原始输出到前端静态 JSON 的完整数据流：

1. **evalscope 输出**：configs, logs, predictions, reviews, reports
2. **ETL 转换**：提取、转换、加载
3. **静态 JSON**：index.json, meta.json, eval_summary.json, samples/*.jsonl
4. **前端消费**：直接 fetch 静态文件

优势：
- 无需后端服务
- 数据格式统一
- 易于扩展和维护
- 支持版本管理
