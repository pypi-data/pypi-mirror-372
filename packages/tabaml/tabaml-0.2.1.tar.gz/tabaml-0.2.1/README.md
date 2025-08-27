# TabAML - 表格数据机器学习框架

TabAML (Tabular Machine Learning) 是一个基于PyTorch的表格数据分类框架，支持二分类和多分类任务。

## 特性

- 🔥 **二分类模型**: 支持二分类任务，包含完整的训练和评估流程
- 🌟 **多分类模型**: 支持多分类任务，自动检测类别数量
- 📊 **丰富的评估指标**: 支持准确率、F1分数（macro/micro/weighted）等多种评估指标
- ⚡ **早停机制**: 防止过拟合，基于验证集性能自动停止训练
- 🛠️ **可配置性**: 通过超参数字典灵活配置模型结构和训练参数
- 📈 **自动化训练**: 包含数据预处理、模型训练、验证和评估的完整流程

## 安装

确保已安装以下依赖：

```bash
pip install torch pandas numpy
```

## 快速开始

### 交互式运行

```bash
python main.py
```

然后选择要运行的模型类型：
- 1: 二分类模型
- 2: 多分类模型

### 二分类模型

```python
from binary_cls import BinaryClsModel
import pandas as pd

# 加载数据
df_train = pd.read_csv("sample/binary_cls_train.csv")
df_val = pd.read_csv("sample/binary_cls_val.csv")
X_train = df_train.drop(columns=['label'])
y_train = df_train['label']
X_val = df_val.drop(columns=['label'])
y_val = df_val['label']

# 创建模型
model = BinaryClsModel(
    hyperparameters={
        'learning_rate': 0.01,
        'batch_size': 32,
        'num_layers': 3,
        'hidden_size': 64,
        'dropout_prob': 0.2,
        'patience': 10,
        'use_early_stopping': True
    }
)

# 训练模型
model.fit(X=X_train, y=y_train, X_val=X_val, y_val=y_val)

# 评估模型
accuracy = model.score(X_val, y_val, metric='accuracy')
f1 = model.score(X_val, y_val, metric='f1')
print(f"验证集准确率: {accuracy:.4f}")
print(f"验证集F1分数: {f1:.4f}")
```

### 多分类模型

```python
from multi_cls import MultiClassifierModel
import pandas as pd

# 加载数据
df_train = pd.read_csv("sample/multi_cls_train.csv")
df_val = pd.read_csv("sample/multi_cls_val.csv")
X_train = df_train.drop(columns=['label'])
y_train = df_train['label']
X_val = df_val.drop(columns=['label'])
y_val = df_val['label']

# 创建模型
model = MultiClassifierModel(
    hyperparameters={
        'learning_rate': 0.01,
        'batch_size': 32,
        'num_layers': 3,
        'hidden_size': 64,
        'dropout_prob': 0.2,
        'patience': 10,
        'use_early_stopping': True,
        'f1_average': 'macro'  # F1计算方式: 'macro', 'micro', 'weighted'
    }
)

# 训练模型
model.fit(X=X_train, y=y_train, X_val=X_val, y_val=y_val)

# 评估模型
accuracy = model.score(X_val, y_val, metric='accuracy')
f1_macro = model.score(X_val, y_val, metric='f1_macro')
f1_micro = model.score(X_val, y_val, metric='f1_micro')
f1_weighted = model.score(X_val, y_val, metric='f1_weighted')

print(f"验证集准确率: {accuracy:.4f}")
print(f"验证集F1 (macro): {f1_macro:.4f}")
print(f"验证集F1 (micro): {f1_micro:.4f}")
print(f"验证集F1 (weighted): {f1_weighted:.4f}")
```

## 模型结构

### 神经网络架构

- **输入层**: 自动适应特征维度
- **隐藏层**: 可配置的层数和神经元数量
- **激活函数**: ReLU
- **正则化**: Dropout
- **输出层**: 
  - 二分类: 2个神经元 + CrossEntropyLoss
  - 多分类: 自动检测类别数量 + CrossEntropyLoss

### 可配置超参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `num_epochs` | 200 | 最大训练轮数 |
| `learning_rate` | 0.01 | 学习率 |
| `batch_size` | 32 | 批次大小 |
| `num_layers` | 3 | 神经网络层数 |
| `hidden_size` | 128 | 隐藏层神经元数量 |
| `dropout_prob` | 0.1 | Dropout概率 |
| `patience` | 3 | 早停耐心参数 |
| `use_early_stopping` | True | 是否使用早停 |
| `f1_average` | 'macro' | F1分数计算方式（仅多分类） |

## 评估指标

### 二分类

- **准确率 (Accuracy)**: 正确预测的样本比例
- **F1分数**: 精确率和召回率的调和平均数

### 多分类

- **准确率 (Accuracy)**: 正确预测的样本比例
- **F1分数 (macro)**: 每个类别F1分数的算术平均
- **F1分数 (micro)**: 全局计算的F1分数
- **F1分数 (weighted)**: 按类别支持数加权的F1分数

## 数据格式

### 输入数据要求

- **特征**: 数值型特征，支持pandas DataFrame或numpy数组
- **标签**: 
  - 二分类: 0和1
  - 多分类: 0, 1, 2, ..., n-1 (连续整数)

### 示例数据

项目包含示例数据：

- `sample/binary_cls_train.csv` / `sample/binary_cls_val.csv`: 二分类数据
- `sample/multi_cls_train.csv` / `sample/multi_cls_val.csv`: 四分类数据

## 文件结构

```
tabaml/
├── main.py              # 主入口文件
├── binary_cls.py        # 二分类模型实现
├── multi_cls.py         # 多分类模型实现
├── metrics.py           # 评估指标实现
├── sample/              # 示例数据
│   ├── binary_cls_train.csv
│   ├── binary_cls_val.csv
│   ├── multi_cls_train.csv
│   └── multi_cls_val.csv
└── README.md
```

## 注意事项

1. **GPU支持**: 代码自动检测CUDA可用性，优先使用GPU训练
2. **数据预处理**: 确保数据已经完成标准化、缺失值处理等预处理步骤
3. **内存使用**: 大数据集建议调整batch_size参数
4. **类别平衡**: 不平衡数据集可能需要额外的处理策略

## 许可证

本项目使用 MIT 许可证。
