# EvalScope Adapter Demo

这个demo演示了从evalscope框架的原始输出数据转换为标准数据协议的完整流程。

## 快速开始

```bash
# 最简单的方式 - 运行快速启动脚本
./demo/quick_start.sh
```

更多使用方式，请查看 [USAGE.md](USAGE.md)。

## 目录结构

```
demo/
├── README.md                          # 本文件 - Demo概览
├── USAGE.md                           # 详细使用指南
├── DEMO_SUMMARY.md                    # Demo总结报告
├── quick_start.sh                     # 快速启动脚本
├── run_demo.py                        # Demo运行脚本
├── validate_output.py                 # 数据验证脚本
├── venv/                              # Python虚拟环境
├── mock_evalscope_output/             # Mock的evalscope原始数据
│   └── 20251124_143025/               # 单次运行的输出目录
│       ├── configs/                   # 配置文件
│       │   └── task_config_*.yaml
│       ├── logs/                      # 日志文件
│       │   └── eval_log.log
│       ├── predictions/               # 预测结果
│       │   └── <model_name>/
│       │       ├── mmlu.jsonl
│       │       └── gsm8k.jsonl
│       ├── reviews/                   # 评分结果
│       │   └── <model_name>/
│       │       ├── mmlu.jsonl
│       │       └── gsm8k.jsonl
│       └── reports/                   # 评估报告
│           └── <model_name>/
│               ├── mmlu.json
│               └── gsm8k.json
└── output_data/                       # 生成的标准协议数据(运行后生成)
    ├── index.json
    └── runs/
        └── run_<timestamp>_<hash>/
            ├── meta.json
            ├── eval_summary.json
            └── samples/
                ├── mmlu_head.jsonl
                └── gsm8k_head.jsonl
```

## Mock数据说明

### 模型配置
- **模型**: Qwen/Qwen2-7B-Instruct
- **评测数据集**: MMLU, GSM8K
- **评测批次大小**: 4
- **随机种子**: 42

### 数据集详情

#### MMLU (Massive Multitask Language Understanding)
- **总样本数**: 150
- **总体准确率**: 72%
- **类别分布**:
  - STEM (60 samples): 68%
    - Physics: 70%
    - Chemistry: 65%
    - Mathematics: 70%
  - Humanities (45 samples): 75%
    - History: 78%
    - Philosophy: 73%
    - Literature: 73%
  - Social Sciences (45 samples): 73%
    - Psychology: 75%
    - Economics: 70%
    - Sociology: 73%

#### GSM8K (Grade School Math 8K)
- **总样本数**: 100
- **总体准确率**: 65%
- **难度分布**:
  - Easy (30 samples): 85%
    - Single-step: 90%
    - Two-step: 80%
  - Medium (40 samples): 68%
    - Multi-step: 70%
    - Word problems: 65%
  - Hard (30 samples): 43%
    - Complex reasoning: 40%
    - Multiple concepts: 47%

## 运行Demo

### 前置要求

```bash
# 安装依赖
pip install -r tools/etl/requirements.txt
```

### 运行脚本

```bash
# 从项目根目录运行
python demo/run_demo.py
```

### 预期输出

脚本会：
1. 初始化EvalScope适配器
2. 从mock数据中提取运行元信息
3. 提取benchmark评估结果
4. 提取样本数据
5. 生成标准协议的JSON文件

运行成功后，会在 `demo/output_data/` 目录下生成以下文件：

```
output_data/
├── index.json                         # 运行列表索引
└── runs/
    └── run_20251124_143025_<hash>/
        ├── meta.json                  # 运行元信息
        ├── eval_summary.json          # 评估摘要
        └── samples/
            ├── mmlu_head.jsonl        # MMLU样本
            └── gsm8k_head.jsonl       # GSM8K样本
```

## 查看生成的数据

### 查看index.json

```bash
cat demo/output_data/index.json | python -m json.tool
```

### 查看运行元信息

```bash
cat demo/output_data/runs/run_*/meta.json | python -m json.tool
```

### 查看评估摘要

```bash
cat demo/output_data/runs/run_*/eval_summary.json | python -m json.tool
```

### 查看样本数据

```bash
# 查看前3行
head -n 3 demo/output_data/runs/run_*/samples/mmlu_head.jsonl | python -m json.tool
```

## 数据协议验证

生成的数据符合标准数据协议v1.0，包含：

1. **ExperimentRun** (meta.json)
   - run_id: 唯一运行标识
   - model: 模型信息
   - datasets: 数据集列表
   - config: 评测配置
   - 时间和状态信息

2. **EvaluationSummary** (eval_summary.json)
   - datasets: 每个数据集的评测结果
   - metrics: 多指标支持
   - categories: 分层统计
   - overall: 全局统计

3. **Samples** (samples/*.jsonl)
   - id: 样本标识
   - input/target/prediction: 输入输出
   - scores: 样本级别评分
   - metadata: 样本元数据

## 下一步

生成的标准协议数据可以直接用于前端可视化：

```bash
# 复制数据到前端public目录
cp -r demo/output_data/* web/public/data/

# 启动前端开发服务器
cd web
npm install
npm run dev
```

然后访问 http://localhost:3000 查看可视化界面。

## 扩展

如果你想创建更多mock数据：

1. 复制 `mock_evalscope_output/20251124_143025/` 目录
2. 修改时间戳和数据内容
3. 再次运行 `run_demo.py` 处理新数据

## 故障排除

### 找不到模块错误

确保从项目根目录运行脚本：

```bash
# 正确
python demo/run_demo.py

# 错误
cd demo && python run_demo.py
```

### YAML解析错误

检查 `configs/task_config_*.yaml` 文件格式是否正确。

### JSONL格式错误

确保每行都是有效的JSON对象，没有空行。

## 参考文档

- [数据协议设计](../docs/Visualization%20System%20Architecture.md#3-数据协议设计核心)
- [适配层设计](../docs/Visualization%20System%20Architecture.md#4-适配层设计)
- [ETL工具实现](../docs/Visualization%20System%20Architecture.md#74-etl-工具实现)
