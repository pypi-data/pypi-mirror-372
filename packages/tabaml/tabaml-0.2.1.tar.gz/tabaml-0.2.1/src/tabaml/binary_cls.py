import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from metrics import accuracy_score, f1_score


class TabularDataset(Dataset):
    """PyTorch数据集类"""

    def __init__(self, X, y):
        self.X = torch.FloatTensor(
            X.values if isinstance(X, pd.DataFrame) else X)
        self.y = torch.LongTensor(y.values if isinstance(y, pd.Series) else y)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class BinaryClassifierNet(nn.Module):
    """二分类神经网络模型"""

    def __init__(self, input_size, hidden_size=128, num_layers=3, dropout_prob=0.1):
        super(BinaryClassifierNet, self).__init__()

        layers = []
        layers.append(nn.Linear(input_size, hidden_size))
        layers.append(nn.ReLU())
        layers.append(nn.Dropout(dropout_prob))

        for _ in range(num_layers - 2):
            layers.append(nn.Linear(hidden_size, hidden_size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_prob))

        layers.append(nn.Linear(hidden_size, 2))  # 二分类输出2个类别

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


class BinaryClsModel:
    def __init__(self, hyperparameters=None):
        self.hyperparameters = hyperparameters or {}
        self.model = None
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        self.input_size = None

        # 默认超参数
        self.num_epochs = self.hyperparameters.get('num_epochs', 200)
        self.learning_rate = self.hyperparameters.get('learning_rate', 0.01)
        self.batch_size = self.hyperparameters.get('batch_size', 32)
        self.num_layers = self.hyperparameters.get('num_layers', 3)
        self.hidden_size = self.hyperparameters.get('hidden_size', 128)
        self.dropout_prob = self.hyperparameters.get('dropout_prob', 0.1)
        self.patience = self.hyperparameters.get('patience', 3)  # 早停耐心参数
        self.use_early_stopping = self.hyperparameters.get(
            'use_early_stopping', True)

    def fit(self, X, y, X_val=None, y_val=None):
        """训练模型"""

        # 获取输入特征维度
        self.input_size = X.shape[1]

        # 创建模型
        self.model = BinaryClassifierNet(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            dropout_prob=self.dropout_prob
        ).to(self.device)

        # 创建数据集和数据加载器
        train_dataset = TabularDataset(X, y)
        train_loader = DataLoader(
            train_dataset, batch_size=self.batch_size, shuffle=True)

        # 验证相关变量
        val_loader = None
        X_val_df = None
        y_val_series = None
        best_val_f1 = 0
        best_model_state = None
        patience_counter = 0

        if X_val is not None and y_val is not None:
            val_dataset = TabularDataset(X_val, y_val)
            val_loader = DataLoader(
                val_dataset, batch_size=self.batch_size, shuffle=False)
            # 保存原始格式用于F1计算
            X_val_df = X_val
            y_val_series = y_val

        # 损失函数和优化器
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)

        # 训练循环
        for epoch in range(self.num_epochs):
            # 训练阶段
            self.model.train()
            total_loss = 0
            for batch_X, batch_y in train_loader:
                batch_X, batch_y = batch_X.to(
                    self.device), batch_y.to(self.device)

                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / len(train_loader)

            # 验证阶段
            if val_loader is not None and X_val_df is not None:
                val_acc = self._evaluate_accuracy(val_loader)
                val_f1 = self._evaluate_f1(X_val_df, y_val_series)

                print(
                    f"Epoch [{epoch+1}/{self.num_epochs}], Loss: {avg_loss:.4f}, Val Acc: {val_acc:.4f}, Val F1: {val_f1:.4f}")

                # 检查是否为最佳F1分数
                if val_f1 > best_val_f1:
                    best_val_f1 = val_f1
                    best_model_state = self.model.state_dict().copy()
                    patience_counter = 0
                    print(f"*** 新的最佳验证F1: {best_val_f1:.4f} ***")
                else:
                    patience_counter += 1

                # 早停检查
                if self.use_early_stopping and patience_counter >= self.patience:
                    print(f"验证F1连续{self.patience}个epoch未提升，提前停止训练")
                    break
            else:
                print(
                    f"Epoch [{epoch+1}/{self.num_epochs}], Loss: {avg_loss:.4f}")

        # 加载最佳模型
        if best_model_state is not None:
            self.model.load_state_dict(best_model_state)
            print(f"已加载最佳验证F1模型 (F1: {best_val_f1:.4f})")

    def _evaluate_accuracy(self, data_loader):
        """在数据加载器上评估模型准确率"""
        self.model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for batch_X, batch_y in data_loader:
                batch_X, batch_y = batch_X.to(
                    self.device), batch_y.to(self.device)
                outputs = self.model(batch_X)
                _, predicted = torch.max(outputs.data, 1)
                total += batch_y.size(0)
                correct += (predicted == batch_y).sum().item()
        return correct / total

    def _evaluate_f1(self, X_val, y_val):
        """计算验证集F1分数"""
        predictions = self.predict(X_val)
        return f1_score(y_val, predictions)

    def predict(self, X):
        """预测"""
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用fit方法")

        self.model.eval()
        X_tensor = torch.FloatTensor(X.values if isinstance(
            X, pd.DataFrame) else X).to(self.device)

        with torch.no_grad():
            outputs = self.model(X_tensor)
            _, predicted = torch.max(outputs, 1)

        return predicted.cpu().numpy()

    def predict_proba(self, X):
        """预测概率"""
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用fit方法")

        self.model.eval()
        X_tensor = torch.FloatTensor(X.values if isinstance(
            X, pd.DataFrame) else X).to(self.device)

        with torch.no_grad():
            outputs = self.model(X_tensor)
            probabilities = torch.softmax(outputs, dim=1)

        return probabilities.cpu().numpy()

    def score(self, X, y, metric):
        """计算评估指标"""
        if metric == 'accuracy':
            predictions = self.predict(X)
            return accuracy_score(y, predictions)
        elif metric == 'f1':
            predictions = self.predict(X)
            return f1_score(y, predictions)
        else:
            raise ValueError(f"不支持的评估指标: {metric}")


class MultiLabelBinaryClsNet(nn.Module):
    """多标签二分类神经网络模型"""

    def __init__(self, input_size, num_labels, hidden_size=128, num_layers=3, dropout_prob=0.1, dependent_mode=False):
        super(MultiLabelBinaryClsNet, self).__init__()

        self.num_labels = num_labels
        self.dependent_mode = dependent_mode

        if dependent_mode:
            # 相关模式：每个标签的预测依赖于前面的标签
            self.label_networks = nn.ModuleList()

            for i in range(num_labels):
                # 当前标签的输入维度 = 原始特征维度 + 前面所有标签的数量
                current_input_size = input_size + i

                layers = []
                layers.append(nn.Linear(current_input_size, hidden_size))
                layers.append(nn.ReLU())
                layers.append(nn.Dropout(dropout_prob))

                for _ in range(num_layers - 2):
                    layers.append(nn.Linear(hidden_size, hidden_size))
                    layers.append(nn.ReLU())
                    layers.append(nn.Dropout(dropout_prob))

                layers.append(nn.Linear(hidden_size, 1))  # 每个标签输出1个值

                self.label_networks.append(nn.Sequential(*layers))
        else:
            # 独立模式：所有标签共享相同的网络结构
            layers = []
            layers.append(nn.Linear(input_size, hidden_size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_prob))

            for _ in range(num_layers - 2):
                layers.append(nn.Linear(hidden_size, hidden_size))
                layers.append(nn.ReLU())
                layers.append(nn.Dropout(dropout_prob))

            layers.append(nn.Linear(hidden_size, num_labels))  # 输出所有标签

            self.network = nn.Sequential(*layers)

    def forward(self, x):
        if self.dependent_mode:
            # 相关模式：顺序预测每个标签
            outputs = []
            current_input = x

            for i, network in enumerate(self.label_networks):
                output = network(current_input)
                outputs.append(output)

                # 将当前标签的预测结果作为下一个标签的输入特征
                # 使用sigmoid激活来获得0-1之间的值
                current_prediction = torch.sigmoid(output)
                current_input = torch.cat(
                    [current_input, current_prediction], dim=1)

            return torch.cat(outputs, dim=1)
        else:
            # 独立模式：同时预测所有标签
            return self.network(x)


class MultiLabelBinaryClsModel:
    """
    多个标签的二分类模型。
    分两种情况: 1.每个标签是独立的;2.每个标签是相关的(通过前面的标签加入训练预测后面的标签)。
    """

    def __init__(self, hyperparameters=None, dependent_mode=False):
        self.hyperparameters = hyperparameters or {}
        self.dependent_mode = dependent_mode
        self.model = None
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        self.input_size = None
        self.num_labels = None
        self.label_names = None

        # 默认超参数
        self.num_epochs = self.hyperparameters.get('num_epochs', 200)
        self.learning_rate = self.hyperparameters.get('learning_rate', 0.01)
        self.batch_size = self.hyperparameters.get('batch_size', 32)
        self.num_layers = self.hyperparameters.get('num_layers', 3)
        self.hidden_size = self.hyperparameters.get('hidden_size', 128)
        self.dropout_prob = self.hyperparameters.get('dropout_prob', 0.1)
        self.patience = self.hyperparameters.get('patience', 3)
        self.use_early_stopping = self.hyperparameters.get(
            'use_early_stopping', True)
        self.threshold = self.hyperparameters.get('threshold', 0.5)  # 二分类阈值

    def fit(self, X, y, X_val=None, y_val=None):
        """训练模型"""

        # 获取输入特征维度和标签数量
        self.input_size = X.shape[1]

        # 处理标签数据
        if isinstance(y, pd.DataFrame):
            self.num_labels = y.shape[1]
            self.label_names = y.columns.tolist()
            y_tensor = torch.FloatTensor(y.values)
        elif isinstance(y, pd.Series):
            # 如果是Series，假设包含多个标签（可能需要预处理）
            raise ValueError("多标签模型需要DataFrame格式的标签数据")
        else:
            # numpy数组
            self.num_labels = y.shape[1] if len(y.shape) > 1 else 1
            self.label_names = [f'label_{i}' for i in range(self.num_labels)]
            y_tensor = torch.FloatTensor(y)

        # 创建模型
        self.model = MultiLabelBinaryClsNet(
            input_size=self.input_size,
            num_labels=self.num_labels,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            dropout_prob=self.dropout_prob,
            dependent_mode=self.dependent_mode
        ).to(self.device)

        # 创建数据集
        X_tensor = torch.FloatTensor(
            X.values if isinstance(X, pd.DataFrame) else X)
        train_dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
        train_loader = DataLoader(
            train_dataset, batch_size=self.batch_size, shuffle=True)

        # 验证相关变量
        val_loader = None
        best_val_f1 = 0
        best_model_state = None
        patience_counter = 0

        if X_val is not None and y_val is not None:
            X_val_tensor = torch.FloatTensor(
                X_val.values if isinstance(X_val, pd.DataFrame) else X_val)
            y_val_tensor = torch.FloatTensor(
                y_val.values if isinstance(y_val, pd.DataFrame) else y_val)
            val_dataset = torch.utils.data.TensorDataset(
                X_val_tensor, y_val_tensor)
            val_loader = DataLoader(
                val_dataset, batch_size=self.batch_size, shuffle=False)

        # 损失函数和优化器 - 使用BCEWithLogitsLoss用于多标签分类
        criterion = nn.BCEWithLogitsLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)

        # 训练循环
        for epoch in range(self.num_epochs):
            # 训练阶段
            self.model.train()
            total_loss = 0
            for batch_X, batch_y in train_loader:
                batch_X, batch_y = batch_X.to(
                    self.device), batch_y.to(self.device)

                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / len(train_loader)

            # 验证阶段
            if val_loader is not None:
                val_f1 = self._evaluate_f1(val_loader)

                print(
                    f"Epoch [{epoch+1}/{self.num_epochs}], Loss: {avg_loss:.4f}, Val F1 (macro): {val_f1:.4f}")

                # 检查是否为最佳F1分数
                if val_f1 > best_val_f1:
                    best_val_f1 = val_f1
                    best_model_state = self.model.state_dict().copy()
                    patience_counter = 0
                    print(f"*** 新的最佳验证F1: {best_val_f1:.4f} ***")
                else:
                    patience_counter += 1

                # 早停检查
                if self.use_early_stopping and patience_counter >= self.patience:
                    print(f"验证F1连续{self.patience}个epoch未提升，提前停止训练")
                    break
            else:
                print(
                    f"Epoch [{epoch+1}/{self.num_epochs}], Loss: {avg_loss:.4f}")

        # 加载最佳模型
        if best_model_state is not None:
            self.model.load_state_dict(best_model_state)
            print(f"已加载最佳验证F1模型 (F1: {best_val_f1:.4f})")

    def _evaluate_f1(self, data_loader):
        """在数据加载器上评估模型F1分数（f1_macro）"""
        self.model.eval()
        all_predictions = []
        all_targets = []

        with torch.no_grad():
            for batch_X, batch_y in data_loader:
                batch_X, batch_y = batch_X.to(
                    self.device), batch_y.to(self.device)
                outputs = self.model(batch_X)
                predictions = (torch.sigmoid(outputs) > self.threshold).float()

                all_predictions.append(predictions.cpu().numpy())
                all_targets.append(batch_y.cpu().numpy())

        all_predictions = np.vstack(all_predictions)
        all_targets = np.vstack(all_targets)

        # 计算每个标签的F1分数并取宏平均
        f1_scores = []
        for i in range(self.num_labels):
            f1 = f1_score(all_targets[:, i], all_predictions[:, i])
            f1_scores.append(f1)

        return np.mean(f1_scores)  # 宏平均F1

    def predict(self, X):
        """预测"""
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用fit方法")

        self.model.eval()
        X_tensor = torch.FloatTensor(X.values if isinstance(
            X, pd.DataFrame) else X).to(self.device)

        with torch.no_grad():
            outputs = self.model(X_tensor)
            predictions = (torch.sigmoid(outputs) > self.threshold).float()

        return predictions.cpu().numpy()

    def predict_proba(self, X):
        """预测概率"""
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用fit方法")

        self.model.eval()
        X_tensor = torch.FloatTensor(X.values if isinstance(
            X, pd.DataFrame) else X).to(self.device)

        with torch.no_grad():
            outputs = self.model(X_tensor)
            probabilities = torch.sigmoid(outputs)

        return probabilities.cpu().numpy()

    def score(self, X, y, metric='f1_macro'):
        """计算评估指标"""
        predictions = self.predict(X)

        if metric == 'f1_macro':
            # 宏平均F1
            f1_scores = []
            y_array = y.values if isinstance(y, pd.DataFrame) else y
            for i in range(self.num_labels):
                f1 = f1_score(y_array[:, i], predictions[:, i])
                f1_scores.append(f1)
            return np.mean(f1_scores)
        elif metric == 'f1_micro':
            # 微平均F1（将所有标签的预测结果flatten后计算）
            y_array = y.values if isinstance(y, pd.DataFrame) else y
            return f1_score(y_array.flatten(), predictions.flatten())
        elif metric == 'accuracy':
            # 子集准确率（所有标签都正确才算正确）
            y_array = y.values if isinstance(y, pd.DataFrame) else y
            return accuracy_score(y_array, predictions)
        else:
            raise ValueError(f"不支持的评估指标: {metric}")

    def get_label_scores(self, X, y):
        """获取每个标签的详细评估结果"""
        predictions = self.predict(X)
        y_array = y.values if isinstance(y, pd.DataFrame) else y

        results = {}
        for i, label_name in enumerate(self.label_names):
            acc = accuracy_score(y_array[:, i], predictions[:, i])
            f1 = f1_score(y_array[:, i], predictions[:, i])
            results[label_name] = {'accuracy': acc, 'f1': f1}

        return results


def create_hyperparameters(config: dict):
    return {
        'learning_rate': config.get('learning_rate', 0.001),
        'batch_size': config.get('batch_size', 32),
        'num_layers': config.get('num_layers', 4),
        'hidden_size': config.get('hidden_size', 64),
        'dropout_prob': config.get('dropout_prob', 0.2),
        'patience': config.get('patience', 20),
        'use_early_stopping': config.get('use_early_stopping', True),
        'threshold': config.get('threshold', 0.5),
        'num_epochs': config.get('num_epochs', 200)
    }


def train_single_label_binary_cls(df_train, df_val, label_column, hyperparameters=None):
    X_train = df_train.drop(columns=[label_column])
    y_train = df_train[label_column]
    X_val = df_val.drop(columns=[label_column])
    y_val = df_val[label_column]

    # 创建模型实例
    model = BinaryClsModel(
        hyperparameters=create_hyperparameters(hyperparameters)
    )

    model.fit(
        X=X_train,
        y=y_train,
        X_val=X_val,
        y_val=y_val
    )
    print("模型训练完成！")
    train_score = model.score(X_train, y_train, metric='accuracy')
    print(f"训练集accuracy得分：{train_score:.4f}")
    train_score = model.score(X_train, y_train, metric='f1')
    print(f"训练集f1得分：{train_score:.4f}")

    val_score = model.score(X_val, y_val, metric='accuracy')
    print(f"验证集accuracy得分：{val_score:.4f}")
    val_score = model.score(X_val, y_val, metric='f1')
    print(f"验证集f1得分：{val_score:.4f}")
    return model


def train_multi_label_binary_cls(df_train, df_val, label_columns, dependent_mode=False, hyperparameters=None):
    """训练多标签分类模型"""
    print(f"\n{'='*50}")
    print(f"训练多标签分类模型 ({'相关模式' if dependent_mode else '独立模式'})")
    print(f"{'='*50}")
    # 读取多标签数据

    # 分离特征和标签
    feature_columns = [
        col for col in df_train.columns if col not in label_columns]

    X_train = df_train[feature_columns]
    y_train = df_train[label_columns]
    X_val = df_val[feature_columns]
    y_val = df_val[label_columns]

    print(f"训练数据形状: X_train {X_train.shape}, y_train {y_train.shape}")
    print(f"验证数据形状: X_val {X_val.shape}, y_val {y_val.shape}")

    # 创建多标签模型实例
    model = MultiLabelBinaryClsModel(
        hyperparameters=create_hyperparameters(hyperparameters),
        dependent_mode=dependent_mode
    )

    # 训练模型
    model.fit(
        X=X_train,
        y=y_train,
        X_val=X_val,
        y_val=y_val
    )

    print(f"\n{'='*30} 模型评估结果 {'='*30}")

    # 训练集评估
    print("\n训练集评估:")
    train_f1_macro = model.score(X_train, y_train, metric='f1_macro')
    train_f1_micro = model.score(X_train, y_train, metric='f1_micro')
    train_accuracy = model.score(X_train, y_train, metric='accuracy')

    print(f"  F1 macro: {train_f1_macro:.4f}")
    print(f"  F1 micro: {train_f1_micro:.4f}")
    print(f"  Accuracy: {train_accuracy:.4f}")

    # 验证集评估
    print("\n验证集评估:")
    val_f1_macro = model.score(X_val, y_val, metric='f1_macro')
    val_f1_micro = model.score(X_val, y_val, metric='f1_micro')
    val_accuracy = model.score(X_val, y_val, metric='accuracy')

    print(f"  F1 macro: {val_f1_macro:.4f}")
    print(f"  F1 micro: {val_f1_micro:.4f}")
    print(f"  Accuracy: {val_accuracy:.4f}")

    # 每个标签的详细评估
    print("\n各标签详细评估 (验证集):")
    label_scores = model.get_label_scores(X_val, y_val)
    for label_name, scores in label_scores.items():
        print(
            f"  {label_name}: 准确率={scores['accuracy']:.4f}, F1={scores['f1']:.4f}")

    # 预测示例
    print(f"\n{'='*20} 预测示例 {'='*20}")
    sample_predictions = model.predict(X_val.iloc[:5])
    sample_probabilities = model.predict_proba(X_val.iloc[:5])

    print("前5个样本的预测结果:")
    for i in range(5):
        print(f"\n样本 {i+1}:")
        print(f"  真实标签: {y_val.iloc[i].values}")
        print(f"  预测标签: {sample_predictions[i]}")
        print(f"  预测概率: {sample_probabilities[i].round(3)}")
        for j, label in enumerate(label_columns):
            print(
                f"    {label}: 真实={int(y_val.iloc[i, j])}, 预测={int(sample_predictions[i, j])}, 概率={sample_probabilities[i, j]:.3f}")

    return model
