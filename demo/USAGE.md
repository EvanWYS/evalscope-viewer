# Demo 使用指南

## 快速开始

最简单的方式是使用quick_start脚本：

```bash
./demo/quick_start.sh
```

这个脚本会自动完成：
1. 创建Python虚拟环境（如果不存在）
2. 安装依赖包（PyYAML）
3. 运行demo转换
4. 验证生成的数据
5. 显示示例输出

## 手动运行

如果你想一步步运行，可以使用以下命令：

### 1. 设置环境

```bash
# 创建虚拟环境
python3 -m venv demo/venv

# 激活虚拟环境（可选）
source demo/venv/bin/activate

# 安装依赖
pip install -r tools/etl/requirements.txt
```

### 2. 运行demo

```bash
demo/venv/bin/python3 demo/run_demo.py
```

预期输出：
```
================================================================================
EvalScope Adapter Demo
================================================================================

Step 1: Initializing EvalScope Adapter...
✅ Adapter initialized

Step 2: Extracting run metadata...
  Run ID: run_20251124_143025_085b35e8
  Model: Qwen/Qwen2-7B-Instruct
  Datasets: mmlu, gsm8k
  Status: completed
  Duration: 186.33s
✅ Metadata extracted

...
```

### 3. 验证数据

```bash
demo/venv/bin/python3 demo/validate_output.py
```

预期输出：
```
================================================================================
Data Validation Script
================================================================================

Validating index.json
✓ Has 'runs' field
✓ Has 'total' field
...

✓ All validations passed!
```

## 查看生成的数据

### 文件结构

```bash
tree demo/output_data/
```

```
demo/output_data/
├── index.json
└── runs/
    └── run_20251124_143025_085b35e8/
        ├── meta.json
        ├── eval_summary.json
        └── samples/
            ├── mmlu_head.jsonl
            └── gsm8k_head.jsonl
```

### 查看JSON文件

```bash
# 查看index.json
cat demo/output_data/index.json | python3 -m json.tool

# 查看meta.json
cat demo/output_data/runs/run_*/meta.json | python3 -m json.tool

# 查看eval_summary.json
cat demo/output_data/runs/run_*/eval_summary.json | python3 -m json.tool

# 查看样本数据（前3行，格式化）
head -n 3 demo/output_data/runs/run_*/samples/mmlu_head.jsonl | while read line; do echo "$line" | python3 -m json.tool; done
```

## 数据说明

### Mock数据概览

本demo使用模拟的evalscope评测数据：

- **模型**: Qwen/Qwen2-7B-Instruct
- **数据集**: MMLU (150样本), GSM8K (100样本)
- **整体得分**: 68.5%

### MMLU结果

| 类别 | 子集 | 得分 | 样本数 |
|------|------|------|--------|
| STEM | Physics | 70% | 20 |
| STEM | Chemistry | 65% | 20 |
| STEM | Mathematics | 70% | 20 |
| Humanities | History | 78% | 15 |
| Humanities | Philosophy | 73% | 15 |
| Humanities | Literature | 73% | 15 |
| Social Sciences | Psychology | 75% | 15 |
| Social Sciences | Economics | 70% | 15 |
| Social Sciences | Sociology | 73% | 15 |

**整体准确率**: 72%

### GSM8K结果

| 难度 | 子集 | 得分 | 样本数 |
|------|------|------|--------|
| Easy | Single-step | 90% | 15 |
| Easy | Two-step | 80% | 15 |
| Medium | Multi-step | 70% | 20 |
| Medium | Word problems | 65% | 20 |
| Hard | Complex reasoning | 40% | 15 |
| Hard | Multiple concepts | 47% | 15 |

**整体准确率**: 65%

## 集成到前端

### 1. 复制数据文件

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

打开浏览器访问 http://localhost:3000

你应该能看到：
- Dashboard显示1个实验
- 点击实验查看详细结果
- 查看MMLU和GSM8K的评测结果
- 浏览样本数据和错误分析

## 扩展Demo

### 添加更多评测运行

1. 复制mock数据并修改：

```bash
# 复制目录
cp -r demo/mock_evalscope_output/20251124_143025 \
      demo/mock_evalscope_output/20251124_160000

# 修改配置和结果（使用编辑器）
# - 修改模型名称
# - 修改得分
# - 修改样本数据
```

2. 更新运行脚本以处理多个目录：

```python
# 在run_demo.py中添加循环处理多个目录
for run_dir in Path("demo/mock_evalscope_output").glob("*/"):
    adapter = EvalScopeAdapter(str(run_dir))
    # ... 处理每个运行
```

### 创建自定义适配器

参考 `tools/etl/adapters/evalscope/adapter.py` 创建新的适配器：

```python
from tools.etl.adapters.base import BaseAdapter
from tools.etl.core.models import StandardRunMeta, StandardBenchmarkResult, StandardSample

class MyCustomAdapter(BaseAdapter):
    def get_framework_name(self) -> str:
        return "my_framework"

    def get_framework_version(self) -> str:
        return "1.0.0"

    def extract_meta(self) -> StandardRunMeta:
        # 从你的框架输出中提取元信息
        ...

    def extract_results(self) -> List[StandardBenchmarkResult]:
        # 从你的框架输出中提取结果
        ...

    def extract_samples(self, dataset: str, limit: int = 100) -> List[StandardSample]:
        # 从你的框架输出中提取样本
        ...
```

## 故障排除

### 1. 找不到模块错误

```
ImportError: No module named 'yaml'
```

**解决方案**：确保安装了依赖
```bash
demo/venv/bin/pip3 install -r tools/etl/requirements.txt
```

### 2. 找不到文件错误

```
FileNotFoundError: Raw directory not found
```

**解决方案**：确保从项目根目录运行
```bash
# 正确
python3 demo/run_demo.py

# 错误
cd demo && python3 run_demo.py
```

### 3. 权限错误

```
Permission denied: ./demo/quick_start.sh
```

**解决方案**：添加执行权限
```bash
chmod +x demo/quick_start.sh
```

### 4. Python版本错误

```
python: command not found
```

**解决方案**：使用python3
```bash
python3 demo/run_demo.py
```

## 常见问题

### Q: 生成的数据可以用于生产环境吗？

A: 本demo使用的是mock数据，仅用于演示目的。实际使用时，应该从真实的evalscope评测输出中转换数据。

### Q: 如何处理大规模数据集？

A: `extract_samples()` 方法有 `limit` 参数，可以限制样本数量。对于大规模数据集，建议：
- 只保存前N个样本（如100或1000）
- 使用抽样策略（如stratified sampling）
- 分别保存正确和错误的样本

### Q: 可以添加自定义字段吗？

A: 可以！标准协议支持 `metadata` 字段用于扩展：

```python
sample = StandardSample(
    id=1,
    input="...",
    target="...",
    prediction="...",
    scores={"accuracy": 1.0},
    metadata={
        "custom_field": "custom_value",
        "another_field": 123
    }
)
```

### Q: 如何验证数据协议版本？

A: 每个JSON文件都包含 `schema_version` 字段，当前版本是 "1.0"。前端应该检查这个字段并相应处理不同版本的数据。

## 相关文档

- [Demo README](README.md) - 详细的demo说明
- [Demo总结](DEMO_SUMMARY.md) - demo完成情况总结
- [系统架构文档](../docs/Visualization%20System%20Architecture.md) - 完整的系统设计
- [ETL数据协议](../docs/ETL%20Data%20Protocol.md) - 数据协议详细说明

## 获取帮助

如果遇到问题：
1. 查看本文档的故障排除部分
2. 检查 demo/README.md 获取更多信息
3. 查看生成的日志输出
4. 运行验证脚本检查数据完整性
