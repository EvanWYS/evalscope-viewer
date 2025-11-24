# LLM 评测可视化整体方案（evalscope + 静态 JSON + ETL 脚本 + 前端可视化）

本方案面向内部模型训练/评测的可视化展示场景，覆盖从评测执行 → 数据转换 → 静态前端展示的完整链路。  
目标是提供一套无需后端服务即可使用的轻量化可视化平台。

---

# 1. 方案概述

评测可视化平台由四部分构成：

1. **evalscope（评测执行层）**  
   - 负责跑评测、产出原始结果文件（raw）。
   - 可以 fork 社区版本，支持本地开发和未来与社区同步。

2. **静态 JSON 数据协议（存储层）**  
   - 用于描述统一的评测结果格式（meta / metrics / summary / samples）。
   - 供前端直接读取，不需要后端服务。

3. **ETL 脚本（数据转换层）**  
   - 从 raw/ 中提取数据（Extract）  
   - 转换为统一 JSON 协议（Transform）  
   - 写入前端静态目录 public/data（Load）

4. **前端可视化（展示层）**  
   - Next.js/React 前端项目  
   - 直接用 `fetch('/data/...')` 读取 JSON  
   - 渲染训练曲线、Benchmark 指标、样本案例等

整体架构如下：

```
evalscope → raw 结果
      ↓
ETL 脚本（raw → data）
      ↓
静态 JSON（public/data）
      ↓
前端可视化（Next.js）
```

---

# 2. 模块说明与职责

## 2.1 evalscope（评测执行）
- 算法同学通过 evalscope 执行一次评测。
- 产出目录格式约定为：

```
raw/
  runs/
    <run_id>/
      evalscope.jsonl
      metrics.log
      samples.jsonl
      ...
```

- 每次评测独立一个 `<run_id>` 目录。

---

## 2.2 静态 JSON 协议（存储格式）

ETL 脚本会将原始数据转换为统一的 JSON 协议，结构如下：

```
public/
  data/
    index.json                         # 所有 run 的索引
    runs/
      <run_id>/
        meta.json                      # 元信息
        metrics.json                   # 训练/评测时间序列
        eval_summary.json              # Benchmark 汇总
        samples_head.jsonl             # 样本级抽样
```

### 2.2.1 index.json（run 列表页）

```json
[
  {
    "run_id": "run_20251124_001",
    "project": "qwen-7b",
    "experiment": "sft-v3",
    "model_name": "qwen-7b-sft",
    "dataset": "sharegpt_filtered_v3.1",
    "start_time": "2025-11-24T01:23:45Z",
    "end_time": "2025-11-24T03:12:11Z",
    "metrics_summary": {
      "mmlu/overall": 0.72,
      "gsm8k/overall": 0.45
    },
    "tags": ["sft", "lr_3e-5"],
    "schema_version": "v1"
  }
]
```

### 2.2.2 meta.json（单 run 信息）

```json
{
  "run_id": "run_20251124_001",
  "project": "qwen-7b",
  "experiment": "sft-v3",
  "model": { "name": "qwen-7b-sft" },
  "dataset": { "name": "sharegpt_filtered", "version": "v3.1" },
  "hparams": { "lr": 3e-5, "batch_size": 64 },
  "start_time": "2025-11-24T01:23:45Z",
  "end_time": "2025-11-24T03:12:11Z"
}
```

### 2.2.3 metrics.json（训练曲线）

```json
{
  "run_id": "run_20251124_001",
  "series": [
    {
      "name": "train/loss",
      "points": [
        { "step": 100, "value": 2.34 },
        { "step": 500, "value": 1.80 }
      ]
    }
  ]
}
```

### 2.2.4 eval_summary.json（Benchmark 汇总）

```json
{
  "run_id": "run_20251124_001",
  "suites": [
    {
      "suite": "mmlu",
      "overall": { "metric": "accuracy", "value": 0.72 }
    }
  ]
}
```

### 2.2.5 samples_head.jsonl（样本级抽样）

```json
{"input": "...", "target": "...", "prediction": "...", "score": 1}
```

---

# 3. ETL 脚本（raw → JSON）

ETL 脚本路径示例：

```
tools/etl/build_static_data.py
```

脚本功能如下：

## 3.1 Extract（提取）
- 从 `raw/runs/<run_id>/` 中读取：
  - evalscope.jsonl
  - metrics.log
  - samples.jsonl

## 3.2 Transform（转换）
- 解析后生成：
  - meta.json
  - metrics.json（训练损失、准确率等曲线）
  - eval_summary.json（Benchmark 汇总）
  - samples_head.jsonl（抽样样本）

## 3.3 Load（写出）
- 写入 `web/public/data/runs/<run_id>/`
- 扫描所有 run，生成 `index.json`

执行示例：

```bash
python tools/etl/build_static_data.py \
  --raw-dir ./raw/runs \
  --out-dir ./web/public/data
```

---

# 4. 前端可视化（Next.js）

前端目录：

```
web/
  public/data/         # ETL 的输出，前端直接 fetch
  src/
    pages/
      /runs
      /runs/[runId]
      /compare
    components/
      MetricChart.tsx
      SummaryRadar.tsx
      SamplesTable.tsx
```

### 前端核心特性：

- **无需后端服务**
- 直接 `fetch('/data/...')`
- 支持：
  - run 列表页（index.json）
  - run 详情页（meta / metrics / summary）
  - 多 run 对比（combine summary）
  - 样本级案例展示（samples）

---

# 5. 用户操作 SOP（本地开发/使用）

以下是本地模式下，算法同学如何使用整个系统：

---

## ➤ 步骤 1：本地运行 evalscope 评测

```bash
cd evalscope
python -m evalscope.run \
  --config configs/qwen7b_sft_v3.yaml \
  --output ../raw/runs/run_20251124_qwen7b_sft_v3_001
```

输出目录即：

```
raw/runs/run_20251124_qwen7b_sft_v3_001/
```

---

## ➤ 步骤 2：运行 ETL 脚本生成静态 JSON

```bash
cd project-root
python tools/etl/build_static_data.py \
  --raw-dir ./raw/runs \
  --out-dir ./web/public/data
```

执行后会生成：

```
web/public/data/index.json
web/public/data/runs/run_20251124_qwen7b_sft_v3_001/*
```

---

## ➤ 步骤 3：本地启动前端

```bash
cd web
npm install
npm run dev
```

浏览器访问：

```
http://localhost:3000
```

即可查看：

- run 列表  
- 单 run 的训练曲线、指标、样本案例  
- 多 run benchmark 对比  

---

# 6. 方案优势

- **无后端**，部署维护成本极低
- 数据协议统一，扩展性强
- 支持本地使用，也可轻松迁移到线上集中式平台
- 前端与 evalscope 解耦，开发人员职责清晰
- 静态文件可随评测结果快速更新

---

# 7. 演进路线（可选）

1. **集中式平台模式（模式A）**
   - 将 raw 和 ETL 放到服务器
   - 提交 raw 即自动生成前端可见的静态 JSON

2. **用户权限 / 项目管理体系**
   - 加 project.json，按 project/experiment 分组查看

3. **支持更多可视化**
   - Error type 统计
   - Heatmap
   - 多 benchmark 综合评分

4. **自动化流水线**
   - 新评测完成 → 自动触发 build ETL → 自动发布前端

---

# 8. 一句话总结

> 整套方案依赖 evalscope 产出 raw，通过 ETL 转换成静态 JSON，再用纯前端渲染，实现轻量可扩展的 LLM 评测可视化平台。

