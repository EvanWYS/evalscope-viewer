# EvalScope Adapter Demo - 总结

## 概述

这个demo完整演示了从evalscope框架的原始评测数据到标准数据协议的ETL转换流程。

## Demo内容

### 1. Mock数据 (mock_evalscope_output/)

模拟了一次完整的evalscope评测运行，包含：

**评测配置**
- 模型: Qwen/Qwen2-7B-Instruct
- 数据集: MMLU, GSM8K
- 生成配置: temperature=0.7, top_p=0.9, max_tokens=512

**评测结果**
- MMLU: 72% accuracy (150 samples)
  - STEM: 68% (Physics, Chemistry, Mathematics)
  - Humanities: 75% (History, Philosophy, Literature)
  - Social Sciences: 73% (Psychology, Economics, Sociology)

- GSM8K: 65% accuracy (100 samples)
  - Easy: 85% (Single-step, Two-step)
  - Medium: 68% (Multi-step, Word problems)
  - Hard: 43% (Complex reasoning, Multiple concepts)

**文件结构**
```
20251124_143025/
├── configs/task_config_*.yaml      # 评测配置
├── logs/eval_log.log                # 运行日志
├── predictions/                     # 模型预测
│   └── Qwen_Qwen2-7B-Instruct/
│       ├── mmlu.jsonl
│       └── gsm8k.jsonl
├── reviews/                         # 评分结果
│   └── Qwen_Qwen2-7B-Instruct/
│       ├── mmlu.jsonl
│       └── gsm8k.jsonl
└── reports/                         # 评估报告
    └── Qwen_Qwen2-7B-Instruct/
        ├── mmlu.json
        └── gsm8k.json
```

### 2. 适配器实现 (tools/etl/)

**EvalScopeAdapter** 实现了完整的数据转换逻辑：

1. **extract_meta()**: 从配置文件和日志提取运行元信息
2. **extract_results()**: 从reports目录提取评估结果
3. **extract_samples()**: 合并predictions和reviews获取样本数据

**关键特性**:
- 自动解析YAML配置
- 从日志提取时间戳和运行时长
- 支持分层类别统计
- 支持多指标评分
- 合并预测和评分数据

### 3. 标准协议数据 (output_data/)

生成符合v1.0协议的标准JSON文件：

**index.json** - 运行列表索引
```json
{
  "runs": [...],
  "total": 1,
  "last_updated": "2025-11-24T..."
}
```

**meta.json** - 运行元信息
- run_id: 唯一标识符
- model: 模型配置
- datasets: 数据集列表
- config: 评测配置
- 时间和状态信息

**eval_summary.json** - 评估摘要
- 每个数据集的详细结果
- 多指标支持
- 分层类别统计
- 全局统计信息

**samples/*.jsonl** - 样本数据
- 输入、目标、预测
- 样本级别评分
- 丰富的元数据

## 数据流程

```
┌──────────────────────────────────────┐
│   EvalScope 原始输出                  │
│   (mock_evalscope_output/)           │
│                                      │
│   • configs/*.yaml                   │
│   • logs/*.log                       │
│   • predictions/*.jsonl              │
│   • reviews/*.jsonl                  │
│   • reports/*.json                   │
└──────────────────┬───────────────────┘
                   │
                   │ EvalScopeAdapter
                   │ • extract_meta()
                   │ • extract_results()
                   │ • extract_samples()
                   ▼
┌──────────────────────────────────────┐
│   标准数据模型                        │
│   (Python dataclasses)               │
│                                      │
│   • StandardRunMeta                  │
│   • StandardBenchmarkResult          │
│   • StandardSample                   │
└──────────────────┬───────────────────┘
                   │
                   │ DataBuilder
                   │ • build_meta()
                   │ • build_eval_summary()
                   │ • build_samples()
                   │ • build_index()
                   ▼
┌──────────────────────────────────────┐
│   标准协议 JSON 文件                  │
│   (output_data/)                     │
│                                      │
│   • index.json                       │
│   • runs/{run_id}/meta.json         │
│   • runs/{run_id}/eval_summary.json │
│   • runs/{run_id}/samples/*.jsonl   │
└──────────────────────────────────────┘
```

## 运行Demo

### 方法1: 使用快速启动脚本 (推荐)

```bash
./demo/quick_start.sh
```

### 方法2: 手动运行

```bash
# 创建虚拟环境
python3 -m venv demo/venv

# 安装依赖
demo/venv/bin/pip3 install -r tools/etl/requirements.txt

# 运行demo
demo/venv/bin/python3 demo/run_demo.py
```

## 验证结果

### 1. 检查生成的文件

```bash
# 查看文件结构
tree demo/output_data/

# 查看index.json
cat demo/output_data/index.json | python3 -m json.tool

# 查看meta.json
cat demo/output_data/runs/run_*/meta.json | python3 -m json.tool

# 查看eval_summary.json
cat demo/output_data/runs/run_*/eval_summary.json | python3 -m json.tool

# 查看样本数据
head -n 3 demo/output_data/runs/run_*/samples/mmlu_head.jsonl | python3 -m json.tool
```

### 2. 验证数据协议

生成的数据符合标准协议v1.0规范：

✅ **ExperimentRun** (meta.json)
- run_id: ✓ 格式正确 `run_<timestamp>_<hash>`
- schema_version: ✓ "1.0"
- model: ✓ 包含name, revision, type, metadata
- datasets: ✓ 数据集列表
- config: ✓ 评测配置
- 时间信息: ✓ start_time, end_time, duration_seconds
- status: ✓ "completed"

✅ **EvaluationSummary** (eval_summary.json)
- datasets: ✓ 2个数据集
- metrics: ✓ accuracy指标，包含score和num_samples
- categories: ✓ 多层级分类统计
- overall: ✓ 全局统计信息

✅ **Sample** (samples/*.jsonl)
- id: ✓ 样本标识
- input/target/prediction: ✓ 完整的输入输出
- scores: ✓ 样本级别评分
- metadata: ✓ 包含category, subset, difficulty等
- choices: ✓ 多选题选项

## 下一步：集成到可视化前端

### 1. 复制数据到前端

```bash
# 创建目标目录
mkdir -p web/public/data

# 复制生成的数据
cp -r demo/output_data/* web/public/data/
```

### 2. 启动前端开发服务器

```bash
cd web
npm install
npm run dev
```

### 3. 访问可视化界面

打开浏览器访问: http://localhost:3000

你应该能看到：
- Dashboard页面显示实验列表
- 点击实验可查看详细结果
- 查看MMLU和GSM8K的评测结果
- 浏览样本数据

## 扩展示例

### 添加更多评测运行

1. 复制mock数据目录：
```bash
cp -r demo/mock_evalscope_output/20251124_143025 \
      demo/mock_evalscope_output/20251124_150000
```

2. 修改配置和结果

3. 再次运行demo:
```bash
demo/venv/bin/python3 demo/run_demo.py
```

### 适配其他评测框架

参考 `tools/etl/adapters/evalscope/adapter.py`，实现新的adapter：

```python
from tools.etl.adapters.base import BaseAdapter

class MyCustomAdapter(BaseAdapter):
    def extract_meta(self):
        # 实现你的逻辑
        pass

    def extract_results(self):
        # 实现你的逻辑
        pass

    def extract_samples(self, dataset, limit):
        # 实现你的逻辑
        pass
```

## 关键技术点

1. **解耦设计**: 适配层完全解耦原始数据格式和标准协议
2. **类型安全**: 使用Python dataclasses保证数据结构正确性
3. **扩展性**: 支持自定义metadata和多指标
4. **版本控制**: schema_version字段支持协议演进
5. **灵活采样**: 支持限制样本数量，避免文件过大

## 文件清单

```
demo/
├── README.md                    # Demo使用文档
├── DEMO_SUMMARY.md             # 本文件 - Demo总结
├── quick_start.sh              # 快速启动脚本
├── run_demo.py                 # Demo运行脚本
├── venv/                       # Python虚拟环境
├── mock_evalscope_output/      # Mock的evalscope数据
│   └── 20251124_143025/
└── output_data/                # 生成的标准协议数据
    ├── index.json
    └── runs/
        └── run_20251124_143025_085b35e8/
```

## 参考文档

- [可视化系统架构设计](../docs/Visualization%20System%20Architecture.md)
- [数据协议设计](../docs/Visualization%20System%20Architecture.md#3-数据协议设计核心)
- [适配层设计](../docs/Visualization%20System%20Architecture.md#4-适配层设计)
- [ETL Data Protocol](../docs/ETL%20Data%20Protocol.md)

## 总结

这个demo展示了：

✅ 完整的ETL转换流程
✅ Mock数据的真实性和完整性
✅ 适配器的正确实现
✅ 标准协议的正确生成
✅ 易于使用的脚本和文档

通过这个demo，你可以：
- 理解数据协议的设计理念
- 学习如何实现自定义适配器
- 快速验证可视化系统的功能
- 为其他评测框架提供参考实现
