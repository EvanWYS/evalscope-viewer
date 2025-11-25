# 评测可视化系统解耦架构方案

## 目录

- [1. 背景与目标](#1-背景与目标)
  - [1.1 背景](#11-背景)
  - [1.2 设计目标](#12-设计目标)
- [2. 核心架构设计](#2-核心架构设计)
  - [2.1 三层架构](#21-三层架构)
  - [2.2 层级职责](#22-层级职责)
- [3. 数据协议设计（核心）](#3-数据协议设计核心)
  - [3.1 设计原则](#31-设计原则)
  - [3.2 核心数据模型](#32-核心数据模型)
  - [3.3 数据文件组织结构](#33-数据文件组织结构)
  - [3.4 数据协议版本控制](#34-数据协议版本控制)
  - [3.5 扩展性设计](#35-扩展性设计)
- [4. 适配层设计](#4-适配层设计)
  - [4.1 Adapter 接口规范](#41-adapter-接口规范)
  - [4.2 EvalScope Adapter 实现](#42-evalscope-adapter-实现)
  - [4.3 适配器自动发现](#43-适配器自动发现)
  - [4.4 用户自定义数据适配](#44-用户自定义数据适配)
- [5. 算法研究员核心需求分析](#5-算法研究员核心需求分析)
  - [5.1 横向对比分析](#51-横向对比分析)
  - [5.2 细粒度错误分析](#52-细粒度错误分析)
  - [5.3 指标深度分析](#53-指标深度分析)
  - [5.4 实验管理和追溯](#54-实验管理和追溯)
  - [5.5 报告生成和分享](#55-报告生成和分享)
- [6. 前端可视化能力规划](#6-前端可视化能力规划)
  - [6.1 Dashboard 总览](#61-dashboard-总览)
  - [6.2 单实验详情页](#62-单实验详情页)
  - [6.3 多模型对比视图](#63-多模型对比视图)
  - [6.4 样本探索器](#64-样本探索器)
  - [6.5 训练曲线（可选）](#65-训练曲线可选)
- [7. 技术实现方案](#7-技术实现方案)
  - [7.1 前端技术栈](#71-前端技术栈)
  - [7.2 数据加载策略](#72-数据加载策略)
  - [7.3 TypeScript 类型定义](#73-typescript-类型定义)
  - [7.4 ETL 工具实现](#74-etl-工具实现)
- [8. 扩展性与开源路径](#8-扩展性与开源路径)
  - [8.1 独立开源的价值](#81-独立开源的价值)
  - [8.2 Co-GenAI 平台集成](#82-co-genai-平台集成)
  - [8.3 社区贡献指南](#83-社区贡献指南)
- [9. 实施路线图](#9-实施路线图)
- [10. 总结](#10-总结)

---

## 1. 背景与目标

### 1.1 背景

当前业界大语言模型评测框架众多，各有特点：

- **EvalScope**: 阿里开源的评测框架，支持多种评测模式
- **OpenCompass**: 上海人工智能实验室的评测平台
- **LM Evaluation Harness**: EleutherAI 维护的评测工具
- **VLMEvalKit**: 多模态评测框架
- **自定义评测**: 企业内部自研评测工具

这些框架的数据格式、输出结构各不相同，导致：
- 可视化系统与特定框架深度耦合
- 切换框架需要大量改造工作
- 无法支持用户自定义评测数据
- 难以独立开源和推广

### 1.2 设计目标

1. **框架解耦**: 可视化系统与评测框架完全解耦，通过标准数据协议交互
2. **扩展性强**: 支持任意评测框架通过适配器接入
3. **易于开源**: 前端可视化能力可独立开源，降低使用门槛
4. **平台集成**: 支持 Co-GenAI 平台用户上传自定义评测数据
5. **用户友好**: 从算法研究员需求出发，提供真正有价值的分析能力

---

## 2. 核心架构设计

### 2.1 三层架构

```
┌──────────────────────────────────────────────────────────────┐
│                  可视化前端层 (Frontend)                       │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Dashboard  │  │ 对比分析视图   │  │   样本详情    │         │
│  └─────────────┘  └──────────────┘  └──────────────┘         │
│                                                              │
│             统一数据接口 (JSON/API)                            │
└──────────────────────────────────────────────────────────────┘
                             ▲
                             │
                     标准数据协议
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                  数据适配层 (Adapter Layer)                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  EvalScope   │  │ OpenCompass  │  │  自定义数据    │       │
│  │   Adapter    │  │   Adapter    │  │   Adapter    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                             ▲
                             │
                     原始数据格式
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                评测框架层 (Evaluation Frameworks)              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  EvalScope   │  │ OpenCompass  │  │   LM-Eval    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 层级职责

**评测框架层**：
- 执行模型评测任务
- 生成原始评测结果
- 各框架格式各异

**数据适配层**：
- 读取原始评测输出
- 转换为标准数据协议
- 数据验证和规范化

**可视化前端层**：
- 只依赖标准数据协议
- 与评测框架完全解耦
- 提供交互式分析能力

---

## 3. 数据协议设计（核心）

### 3.1 设计原则

1. **完备性**: 覆盖评测全流程的所有关键信息
2. **扩展性**: 支持自定义字段，兼容未来需求
3. **类型安全**: 明确的数据类型定义
4. **版本控制**: 协议版本化，支持向后兼容
5. **简洁性**: 避免冗余，保持结构清晰

### 3.2 核心数据模型

#### 3.2.1 实验运行（Experiment Run）

**用途**: 描述单次评测实验的基本信息

**Schema 定义** (TypeScript):

```typescript
interface ExperimentRun {
  // === 核心标识 ===
  run_id: string;                    // 唯一运行标识，格式: run_<timestamp>_<hash>
  schema_version: string;            // 数据协议版本，格式: "major.minor"

  // === 时间信息 ===
  timestamp: string;                 // 创建时间戳，格式: YYYYMMDD_HHMMSS
  start_time: string;                // 开始时间，ISO 8601 格式
  end_time: string | null;           // 结束时间，ISO 8601 格式，running 时为 null
  duration_seconds: number | null;   // 运行时长（秒），running 时为 null

  // === 模型信息 ===
  model: ModelInfo;

  // === 评测配置 ===
  datasets: string[];                // 评测数据集列表
  config: EvalConfig;                // 评测配置

  // === 状态和元数据 ===
  status: "running" | "completed" | "failed" | "cancelled";
  tags: string[];                    // 用户自定义标签，用于筛选和分组
  description?: string;              // 可选的运行描述

  // === 环境信息 ===
  environment?: EnvironmentInfo;

  // === 扩展字段 ===
  metadata?: Record<string, any>;    // 自定义元数据，支持任意扩展
}

interface ModelInfo {
  name: string;                      // 模型名称或路径
  revision?: string;                 // 模型版本/commit hash
  type: "openai_api" | "local" | "custom" | string;  // 模型类型，可扩展
  parameters?: {
    size?: string;                   // 参数量，如 "7B", "13B"
    precision?: string;              // 精度，如 "fp16", "int8"
    [key: string]: any;              // 其他自定义参数
  };
}

interface EvalConfig {
  eval_batch_size?: number;          // 评测批次大小
  seed?: number | null;              // 随机种子
  limit?: number | null;             // 样本数量限制，null 表示全量
  generation_config?: {
    do_sample?: boolean;
    max_new_tokens?: number;
    temperature?: number;
    top_p?: number;
    top_k?: number;
    [key: string]: any;              // 其他生成参数
  };
  [key: string]: any;                // 其他评测配置
}

interface EnvironmentInfo {
  framework?: string;                // 评测框架名称和版本，如 "evalscope==1.0.0"
  python_version?: string;           // Python 版本
  cuda_version?: string;             // CUDA 版本
  gpu?: string;                      // GPU 型号
  [key: string]: any;                // 其他环境信息
}
```

**字段详解**：

- `run_id`: 全局唯一标识符，建议格式为 `run_<timestamp>_<hash>`，其中 hash 可以是模型名的 MD5 前缀
- `schema_version`: 协议版本号，当前为 "1.0"，前端需要检查版本兼容性
- `status`: 运行状态，支持四种状态便于实时监控
- `tags`: 灵活的标签系统，支持用户自定义分类，如 ["baseline", "experiment-1", "优化后"]
- `metadata`: 预留的扩展字段，支持适配器添加框架特定的信息

#### 3.2.2 评估摘要（Evaluation Summary）

**用途**: 聚合的评测结果，支持多数据集、多指标、分层统计

**Schema 定义**:

```typescript
interface EvaluationSummary {
  // === 关联信息 ===
  run_id: string;                    // 关联的 run_id
  schema_version: string;            // 数据协议版本

  // === 数据集评测结果 ===
  datasets: DatasetEvaluation[];     // 每个数据集的评测结果

  // === 全局统计 ===
  overall: OverallStatistics;
}

interface DatasetEvaluation {
  // === 数据集标识 ===
  dataset: string;                   // 数据集名称（内部标识）
  dataset_pretty_name?: string;      // 显示名称
  dataset_description?: string;      // 数据集描述

  // === 评测指标 ===
  metrics: Record<string, MetricValue>;  // 指标字典，key 为指标名

  // === 总体得分 ===
  overall_score: number;             // 该数据集的总体得分（通常是主指标的 score）

  // === 分层统计 ===
  categories?: CategoryBreakdown[];  // 类别分解（可选，支持多层级）

  // === 扩展字段 ===
  metadata?: Record<string, any>;    // 自定义元数据
}

interface MetricValue {
  score: number;                     // 微平均得分（weighted by sample count）
  macro_score?: number;              // 宏平均得分（simple average）
  num_samples: number;               // 样本总数
  std?: number;                      // 标准差（可选）
  confidence_interval?: [number, number];  // 置信区间（可选）
}

interface CategoryBreakdown {
  // === 类别标识 ===
  name: string | string[];           // 类别名称，支持层级结构
                                     // 例如: "STEM" 或 ["STEM", "Physics"]

  // === 类别统计 ===
  score: number;                     // 微平均得分
  macro_score?: number;              // 宏平均得分
  num_samples: number;               // 该类别样本数

  // === 子集详情 ===
  subsets?: SubsetDetail[];          // 最细粒度的子集

  // === 子类别 ===
  subcategories?: CategoryBreakdown[];  // 支持递归嵌套
}

interface SubsetDetail {
  name: string;                      // 子集名称
  score: number;                     // 该子集得分
  num: number;                       // 样本数量
  metrics?: Record<string, number>;  // 可选的多指标详情
}

interface OverallStatistics {
  avg_score: number;                 // 所有数据集的平均分
  weighted_avg_score?: number;       // 加权平均分（按样本数加权）
  total_samples: number;             // 总样本数
  total_datasets: number;            // 数据集数量
  best_dataset?: string;             // 得分最高的数据集
  worst_dataset?: string;            // 得分最低的数据集
}
```

**设计亮点**：

1. **多指标支持**: `metrics` 使用字典结构，支持任意数量和类型的指标
   - 常见指标：accuracy, f1, precision, recall, bleu, rouge, pass@k
   - 自定义指标：任意字符串作为 key

2. **分层统计**: `categories` 和 `subcategories` 支持递归嵌套
   - MMLU: STEM → Physics → quantum_mechanics
   - 自定义分类：难度 → 困难 → 特定错误类型

3. **兼容性**: 所有高级字段都是可选的，最简情况只需 `dataset` + `overall_score`

#### 3.2.3 样本数据（Sample Data）

**用途**: 样本级别的详细信息，支持错误分析和 badcase 探查

**Schema 定义**:

```typescript
interface Sample {
  // === 核心标识 ===
  id: string | number;               // 样本唯一标识

  // === 输入输出 ===
  input: string | Message[];         // 输入内容（支持字符串或消息列表）
  target: string | string[];         // 目标答案（单个或多个）
  prediction: string;                // 模型预测结果

  // === 多选题支持 ===
  choices?: string[];                // 选项列表（仅多选题）

  // === 评分信息 ===
  scores: Record<string, number>;    // 样本级别的评分，key 为指标名
  is_correct?: boolean;              // 是否正确（便于快速筛选）

  // === 元数据 ===
  metadata?: SampleMetadata;

  // === 扩展字段 ===
  extra?: Record<string, any>;       // 任意扩展数据
}

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

interface SampleMetadata {
  // === 分类信息 ===
  category?: string | string[];      // 类别标签（单个或多个）
  subset?: string;                   // 所属子集

  // === 难度和属性 ===
  difficulty?: "easy" | "medium" | "hard" | string;
  tags?: string[];                   // 自定义标签

  // === 评分元数据 ===
  judge_type?: string;               // 评分方式，如 "exact_match", "llm_judge", "regex"
  judge_model?: string;              // 评分模型（如使用 LLM 评分）

  // === 其他信息 ===
  language?: string;                 // 语言
  domain?: string;                   // 领域
  source?: string;                   // 数据来源

  [key: string]: any;                // 其他自定义元数据
}
```

**设计亮点**：

1. **灵活的输入格式**:
   - 简单文本: `input: "What is 2+2?"`
   - 多轮对话: `input: [{role: "user", content: "..."}, ...]`

2. **多答案支持**: `target` 可以是字符串数组，支持多个正确答案

3. **丰富的元数据**: `metadata` 支持任意扩展，适配不同数据集的特殊字段

#### 3.2.4 训练曲线（Training Metrics，可选）

**用途**: 训练过程中的指标变化，支持训练监控和对比

**Schema 定义**:

```typescript
interface TrainingMetrics {
  // === 关联信息 ===
  run_id: string;
  schema_version: string;

  // === 数据来源 ===
  source: "tensorboard" | "wandb" | "custom" | string;

  // === 时间序列 ===
  series: MetricSeries[];
}

interface MetricSeries {
  name: string;                      // 指标名称，建议使用 "/" 分隔，如 "train/loss"
  type: "scalar" | "histogram" | "image" | string;
  unit?: string;                     // 单位，如 "seconds", "MB"
  points: DataPoint[];               // 数据点列表
}

interface DataPoint {
  step: number;                      // 训练步数或 epoch
  value: number | number[];          // 指标值（scalar 为数字，histogram 为数组）
  timestamp?: string;                // 时间戳（ISO 8601 格式，可选）
  wall_time?: number;                // Unix 时间戳（秒，可选）
}
```

**常见指标命名规范**:
- 训练指标: `train/loss`, `train/learning_rate`, `train/grad_norm`
- 验证指标: `eval/accuracy`, `eval/perplexity`
- 系统指标: `system/gpu_memory`, `system/throughput`

### 3.3 数据文件组织结构

```
data/
  ├── index.json                     # 运行列表索引
  └── runs/
      └── <run_id>/
          ├── meta.json              # 实验运行元信息 (ExperimentRun)
          ├── eval_summary.json      # 评估摘要 (EvaluationSummary)
          ├── metrics.json           # 训练曲线（可选）(TrainingMetrics)
          └── samples/
              ├── <dataset_1>_head.jsonl   # 样本数据（JSONL 格式）
              ├── <dataset_2>_head.jsonl
              └── ...
```

**index.json 格式**:

```typescript
interface Index {
  runs: RunIndexEntry[];             // 运行列表
  total: number;                     // 总数
  last_updated: string;              // 最后更新时间（ISO 8601）
}

interface RunIndexEntry {
  // 从 ExperimentRun 提取的关键信息
  run_id: string;
  timestamp: string;
  model: {
    name: string;
    type: string;
  };
  datasets: string[];
  overall_score: number;
  num_samples: number;
  start_time: string;
  end_time: string | null;
  duration_seconds: number | null;
  status: string;
  tags: string[];
}
```

### 3.4 数据协议版本控制

#### 3.4.1 版本号规范

格式: `"<major>.<minor>"`

- **Major 版本**: 不兼容的破坏性变更
  - 删除必需字段
  - 修改字段类型
  - 修改字段语义

- **Minor 版本**: 向后兼容的新增功能
  - 新增可选字段
  - 新增枚举值
  - 扩展元数据

**当前版本**: `"1.0"`

#### 3.4.2 版本兼容性策略

前端需要实现版本检查和降级处理:

```typescript
function parseExperimentRun(data: any): ExperimentRun {
  const version = data.schema_version || "1.0";
  const [major, minor] = version.split('.').map(Number);

  // 检查主版本兼容性
  if (major > SUPPORTED_MAJOR_VERSION) {
    throw new Error(`Unsupported schema version: ${version}`);
  }

  // 根据版本进行解析
  if (major === 1) {
    return parseV1Run(data, minor);
  }

  throw new Error(`Unknown schema version: ${version}`);
}

function parseV1Run(data: any, minor: number): ExperimentRun {
  // 基础字段（1.0+）
  const run: ExperimentRun = {
    run_id: data.run_id,
    schema_version: data.schema_version,
    timestamp: data.timestamp,
    // ...
  };

  // 新增字段（1.1+）
  if (minor >= 1) {
    run.description = data.description;
  }

  return run;
}
```

### 3.5 扩展性设计

#### 3.5.1 自定义字段规范

所有核心数据模型都包含 `metadata` 或 `extra` 字段，用于存放框架特定或用户自定义的数据。

**示例 1: 添加评测框架特定信息**

```json
{
  "run_id": "run_20251124_143025",
  "model": {...},
  "metadata": {
    "evalscope": {
      "task_config_hash": "a1b2c3d4",
      "work_dir": "./outputs/20251124_143025"
    }
  }
}
```

**示例 2: 添加用户自定义标注**

```json
{
  "id": 42,
  "input": "What is the capital of France?",
  "prediction": "London",
  "scores": {"accuracy": 0.0},
  "metadata": {
    "category": "geography",
    "user_annotation": {
      "error_type": "factual_error",
      "severity": "high",
      "notes": "模型混淆了英国和法国的首都"
    }
  }
}
```

#### 3.5.2 指标扩展

`metrics` 字段使用字典结构，支持任意自定义指标:

```json
{
  "metrics": {
    "accuracy": {
      "score": 0.85,
      "num_samples": 1000
    },
    "f1_macro": {
      "score": 0.82,
      "num_samples": 1000
    },
    "custom_metric": {
      "score": 0.91,
      "num_samples": 1000,
      "description": "自定义的领域特定指标"
    }
  }
}
```

#### 3.5.3 类别层级扩展

`categories` 支持任意深度的嵌套:

```json
{
  "categories": [
    {
      "name": ["难度", "困难"],
      "score": 0.65,
      "num_samples": 200,
      "subcategories": [
        {
          "name": ["难度", "困难", "推理错误"],
          "score": 0.58,
          "num_samples": 80,
          "subsets": [
            {"name": "多步推理", "score": 0.55, "num": 40},
            {"name": "逻辑链断裂", "score": 0.61, "num": 40}
          ]
        }
      ]
    }
  ]
}
```

---

## 4. 适配层设计

### 4.1 Adapter 接口规范

所有适配器需要实现统一的接口:

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

class EvaluationAdapter(ABC):
    """评测框架适配器基类"""

    @abstractmethod
    def extract_run_meta(self, run_dir: Path) -> Dict:
        """
        提取运行元信息

        Returns:
            ExperimentRun 字典
        """
        pass

    @abstractmethod
    def extract_eval_summary(self, run_dir: Path) -> Dict:
        """
        提取评估摘要

        Returns:
            EvaluationSummary 字典
        """
        pass

    @abstractmethod
    def extract_samples(
        self,
        run_dir: Path,
        dataset: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        提取样本数据

        Args:
            run_dir: 运行目录
            dataset: 数据集名称
            limit: 抽样数量

        Returns:
            Sample 字典列表
        """
        pass

    @abstractmethod
    def validate(self, run_dir: Path) -> bool:
        """
        验证运行目录是否符合该框架格式

        Returns:
            True 如果是该框架的输出
        """
        pass
```

### 4.2 EvalScope Adapter 实现

```python
class EvalScopeAdapter(EvaluationAdapter):
    """EvalScope 框架适配器"""

    def validate(self, run_dir: Path) -> bool:
        """检查是否为 evalscope 输出"""
        required_dirs = ['configs', 'reports', 'predictions']
        return all((run_dir / d).exists() for d in required_dirs)

    def extract_run_meta(self, run_dir: Path) -> Dict:
        """从 configs/task_config_*.yaml 提取元信息"""
        config_file = next(run_dir.glob('configs/task_config_*.yaml'))
        config = yaml.safe_load(config_file.read_text())

        timestamp = run_dir.name  # 目录名即时间戳
        run_id = f"run_{timestamp}_{self._hash_model(config['model']['model_id'])}"

        return {
            "run_id": run_id,
            "schema_version": "1.0",
            "timestamp": timestamp,
            "model": {
                "name": config["model"]["model_id"],
                "revision": config["model"].get("model_revision", "master"),
                "type": config.get("eval_type", "unknown")
            },
            "datasets": config["eval"]["datasets"],
            "config": {
                "eval_batch_size": config["eval"].get("eval_batch_size", 1),
                "seed": config["eval"].get("seed"),
                "generation_config": config["model"].get("generation_config", {})
            },
            "start_time": self._parse_log_start_time(run_dir / "logs"),
            "end_time": self._parse_log_end_time(run_dir / "logs"),
            "status": "completed",
            "tags": [],
            "environment": {
                "framework": "evalscope",
                # 可以从日志中提取更多环境信息
            },
            "metadata": {
                "evalscope": {
                    "work_dir": str(run_dir),
                    "config_file": config_file.name
                }
            }
        }

    def extract_eval_summary(self, run_dir: Path) -> Dict:
        """从 reports/*/*.json 提取评估摘要"""
        reports_dir = run_dir / "reports"
        datasets = []

        for report_file in reports_dir.rglob("*.json"):
            report = json.loads(report_file.read_text())

            # 提取指标
            metrics = {}
            for metric in report["metrics"]:
                metrics[metric["name"]] = {
                    "score": metric["score"],
                    "macro_score": metric.get("macro_score"),
                    "num_samples": metric["num"]
                }

            # 提取类别
            categories = []
            if report["metrics"]:
                primary_metric = report["metrics"][0]
                for cat in primary_metric.get("categories", []):
                    categories.append({
                        "name": cat["name"],
                        "score": cat["score"],
                        "macro_score": cat.get("macro_score"),
                        "num_samples": cat["num"],
                        "subsets": cat.get("subsets", [])
                    })

            datasets.append({
                "dataset": report["dataset_name"],
                "dataset_pretty_name": report.get("dataset_pretty_name"),
                "metrics": metrics,
                "overall_score": report["score"],
                "categories": categories
            })

        # 计算全局统计
        total_samples = sum(
            ds["metrics"][list(ds["metrics"].keys())[0]]["num_samples"]
            for ds in datasets
        )
        avg_score = sum(ds["overall_score"] for ds in datasets) / len(datasets)

        return {
            "run_id": self._extract_run_id(run_dir),
            "schema_version": "1.0",
            "datasets": datasets,
            "overall": {
                "avg_score": avg_score,
                "total_samples": total_samples,
                "total_datasets": len(datasets)
            }
        }

    def extract_samples(
        self,
        run_dir: Path,
        dataset: str,
        limit: int = 100
    ) -> List[Dict]:
        """从 predictions 和 reviews 合并样本数据"""
        pred_file = next(run_dir.glob(f"predictions/*/{dataset}.jsonl"))
        review_file = next(run_dir.glob(f"reviews/*/{dataset}.jsonl"))

        predictions = [json.loads(line) for line in pred_file.read_text().splitlines()]
        reviews = [json.loads(line) for line in review_file.read_text().splitlines()]

        # 建立 id 到 review 的映射
        reviews_dict = {r["id"]: r for r in reviews}

        samples = []
        for pred in predictions[:limit]:
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

            if pred.get("choices"):
                sample["choices"] = pred["choices"]

            # 判断是否正确
            if "accuracy" in sample["scores"]:
                sample["is_correct"] = sample["scores"]["accuracy"] == 1.0

            samples.append(sample)

        return samples
```

### 4.3 适配器自动发现

```python
class AdapterRegistry:
    """适配器注册表"""

    def __init__(self):
        self.adapters: List[EvaluationAdapter] = []

    def register(self, adapter: EvaluationAdapter):
        """注册适配器"""
        self.adapters.append(adapter)

    def detect(self, run_dir: Path) -> EvaluationAdapter:
        """自动检测并返回合适的适配器"""
        for adapter in self.adapters:
            if adapter.validate(run_dir):
                return adapter
        raise ValueError(f"No adapter found for: {run_dir}")

# 使用示例
registry = AdapterRegistry()
registry.register(EvalScopeAdapter())
registry.register(OpenCompassAdapter())
registry.register(CustomAdapter())

adapter = registry.detect(Path("./outputs/20251124_143025"))
meta = adapter.extract_run_meta(Path("./outputs/20251124_143025"))
```

### 4.4 用户自定义数据适配

对于用户上传的自定义评测数据，提供简化的适配器：

```python
class CustomJSONAdapter(EvaluationAdapter):
    """
    用户自定义 JSON 适配器

    要求用户提供符合标准协议的 JSON 文件：
    - meta.json
    - eval_summary.json
    - samples/*.jsonl
    """

    def validate(self, run_dir: Path) -> bool:
        return (run_dir / "meta.json").exists()

    def extract_run_meta(self, run_dir: Path) -> Dict:
        return json.loads((run_dir / "meta.json").read_text())

    def extract_eval_summary(self, run_dir: Path) -> Dict:
        return json.loads((run_dir / "eval_summary.json").read_text())

    def extract_samples(self, run_dir: Path, dataset: str, limit: int = 100) -> List[Dict]:
        sample_file = run_dir / "samples" / f"{dataset}_head.jsonl"
        lines = sample_file.read_text().splitlines()[:limit]
        return [json.loads(line) for line in lines]
```

---

## 5. 算法研究员核心需求分析

基于调研和访谈，算法研究员在模型评测后最关心以下内容：

### 5.1 横向对比分析

**需求**: 对比多个模型或同一模型不同版本在相同数据集上的表现

**支持能力**:
- 多模型同数据集对比（柱状图、雷达图）
- 细粒度子集对比（热力图）
- 统计显著性检验

**数据支持**: 多个 `run_id` 的 `eval_summary.json`

### 5.2 细粒度错误分析

**需求**: 快速定位模型在哪些类型的问题上表现不佳

**支持能力**:
- 按类别/难度/标签筛选样本
- 错误样本聚类和标注
- Badcase 模式挖掘

**数据支持**: `samples/*.jsonl` + 丰富的 `metadata`

### 5.3 指标深度分析

**需求**: 不满足于单一 accuracy，需要多维度指标

**支持能力**:
- 多指标联合展示
- 指标相关性分析
- 自定义指标公式

**数据支持**: `metrics` 字典的灵活结构

### 5.4 实验管理和追溯

**需求**: 管理大量实验，快速找到特定配置的结果

**支持能力**:
- 标签和筛选系统
- 配置对比
- 实验笔记和标注

**数据支持**: `tags`, `description`, `config`

### 5.5 报告生成和分享

**需求**: 将分析结果制作成报告分享给团队

**支持能力**:
- Markdown/PDF 报告导出
- 图表导出
- 结果链接分享

---

## 6. 前端可视化能力规划

### 6.1 Dashboard 总览

**功能**:
- 实验列表（表格视图）
- 按时间/模型/数据集筛选
- 快速对比（选中多个实验）

**数据来源**: `index.json`

### 6.2 单实验详情页

**功能**:
- 元信息展示（模型、配置、环境）
- 数据集结果卡片
- 类别分解树状图

**数据来源**: `meta.json` + `eval_summary.json`

### 6.3 多模型对比视图

**功能**:
- 雷达图对比
- 热力图（数据集 × 模型）
- 子集级别对比表格

**数据来源**: 多个 `run_id` 的数据

### 6.4 样本探索器

**功能**:
- 分页浏览样本
- 多维筛选（正确/错误、类别、难度）
- 样本标注（错误类型标注）
- 搜索和高亮

**数据来源**: `samples/*.jsonl`

### 6.5 训练曲线（可选）

**功能**:
- 多曲线对比
- 放大和平滑
- 事件标注

**数据来源**: `metrics.json`

---

## 7. 技术实现方案

### 7.1 前端技术栈

**推荐方案**: Next.js + TypeScript + Tailwind CSS + shadcn/ui

- **Next.js 14+**: 静态生成 (SSG) 或客户端渲染
- **TypeScript**: 类型安全，基于数据协议生成类型定义
- **Tailwind CSS**: 快速样式开发
- **shadcn/ui**: 高质量组件库
- **Recharts / D3.js**: 图表库
- **Zustand / Jotai**: 轻量级状态管理

### 7.2 数据加载策略

**静态部署模式**:
```typescript
// 直接 fetch 静态 JSON 文件
async function loadRunMeta(runId: string) {
  const res = await fetch(`/data/runs/${runId}/meta.json`);
  return res.json();
}
```

**API 模式**（可选，用于动态数据）:
```typescript
// 通过后端 API 查询
async function loadRunMeta(runId: string) {
  const res = await fetch(`/api/runs/${runId}/meta`);
  return res.json();
}
```

### 7.3 TypeScript 类型定义

基于数据协议自动生成类型：

```bash
# 使用 json-schema-to-typescript
npx json-schema-to-typescript \
  schemas/experiment-run.schema.json \
  -o src/types/protocol.ts
```

### 7.4 ETL 工具实现

**语言选择**: Python（与评测框架生态一致）

**目录结构**:
```
tools/etl/
  ├── cli.py                    # 命令行入口
  ├── adapters/
  │   ├── base.py              # 基类
  │   ├── evalscope.py         # EvalScope 适配器
  │   ├── opencompass.py       # OpenCompass 适配器
  │   └── custom.py            # 自定义适配器
  ├── validators/
  │   └── schema_validator.py  # 数据验证
  └── utils/
      └── json_utils.py
```

**命令行使用**:
```bash
# 转换 evalscope 输出
python -m tools.etl.cli \
  --input ./outputs \
  --output ./web/public/data \
  --adapter evalscope

# 验证数据协议
python -m tools.etl.cli validate ./web/public/data/runs/run_xxx
```

---

## 8. 扩展性与开源路径

### 8.1 独立开源的价值

**对用户**:
- 无需使用特定评测框架
- 只需提供符合协议的 JSON 即可使用可视化
- 降低学习成本

**对社区**:
- 吸引更多贡献者
- 成为评测可视化的事实标准
- 与各评测框架建立生态合作

### 8.2 Co-GenAI 平台集成

**集成方式**:
1. 用户在平台上传评测数据（JSON 或原始输出）
2. 平台调用适配器转换为标准协议
3. 前端可视化组件嵌入平台页面
4. 支持在线标注和团队协作

**架构**:
```
Co-GenAI 平台
  ├── 评测任务管理
  ├── 数据适配服务 (ETL as a Service)
  ├── 可视化组件 (iframe 嵌入)
  └── 协作和分享
```

### 8.3 社区贡献指南

**如何贡献新的适配器**:
1. 继承 `EvaluationAdapter` 基类
2. 实现必需方法
3. 添加测试用例
4. 提交 PR 并附上示例数据

**如何扩展数据协议**:
1. 提出 RFC（Request for Comments）
2. 讨论兼容性影响
3. 更新 JSON Schema
4. 实现向后兼容的解析逻辑

---

## 9. 实施路线图

### Phase 1: 基础协议和 EvalScope 适配（4 周）

- [x] 完成数据协议设计文档
- [ ] 实现 TypeScript 类型定义
- [ ] 实现 EvalScope Adapter
- [ ] 实现 ETL 工具 CLI
- [ ] 数据验证器

**交付物**: 可以将 EvalScope 输出转换为标准 JSON

### Phase 2: 核心可视化功能（6 周）

- [ ] 项目脚手架（Next.js + TypeScript）
- [ ] Dashboard 页面（实验列表）
- [ ] 单实验详情页
- [ ] 基础图表组件（柱状图、雷达图）
- [ ] 样本探索器（分页、筛选）

**交付物**: 可用的 MVP 版本

### Phase 3: 高级分析和多框架支持（4 周）

- [ ] 多模型对比视图
- [ ] 热力图和高级图表
- [ ] 样本标注功能
- [ ] OpenCompass Adapter
- [ ] 自定义数据 Adapter

**交付物**: 功能完整的可视化系统

### Phase 4: 开源准备和平台集成（3 周）

- [ ] 文档完善（用户指南、开发指南）
- [ ] 示例数据和教程
- [ ] 性能优化和测试
- [ ] Co-GenAI 平台集成
- [ ] 开源发布

**交付物**: 开源项目 + 平台集成

---

## 10. 总结

本方案通过**数据协议层**实现了评测框架与可视化系统的完全解耦，具有以下优势：

1. **框架无关**: 支持任意评测框架，只需实现适配器
2. **易于扩展**: 丰富的元数据和扩展字段设计
3. **类型安全**: 基于 TypeScript 的类型系统
4. **独立开源**: 可视化能力可独立使用和开源
5. **平台友好**: 易于集成到 Co-GenAI 等平台

通过标准化的数据协议，我们为评测可视化领域建立了一个通用的标准，有望成为业界的参考实现。
