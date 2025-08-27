import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from metrics import accuracy_score, multi_class_f1_score
import numpy as np


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


class MultiClassifierNet(nn.Module):
    """多分类神经网络模型"""

    def __init__(self, input_size, num_classes, hidden_size=128, num_layers=3, dropout_prob=0.1):
        super(MultiClassifierNet, self).__init__()

        layers = []
        layers.append(nn.Linear(input_size, hidden_size))
        layers.append(nn.ReLU())
        layers.append(nn.Dropout(dropout_prob))

        for _ in range(num_layers - 2):
            layers.append(nn.Linear(hidden_size, hidden_size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_prob))

        layers.append(nn.Linear(hidden_size, num_classes))  # 多分类输出

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


class MultiClassifierModel:
    """多分类模型类"""

    def __init__(self, hyperparameters=None):
        self.hyperparameters = hyperparameters or {}
        self.model = None
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        self.input_size = None
        self.num_classes = None

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
        self.f1_average = self.hyperparameters.get(
            'f1_average', 'macro')  # F1计算方式

    def fit(self, X, y, X_val=None, y_val=None):
        """训练模型"""

        # 获取输入特征维度和类别数量
        self.input_size = X.shape[1]

        # 确定类别数量
        if hasattr(y, 'values'):
            unique_classes = np.unique(y.values)
        else:
            unique_classes = np.unique(y)
        self.num_classes = len(unique_classes)

        print(f"检测到 {self.num_classes} 个类别: {unique_classes}")
        print(f"类别占比")
        for i in range(self.num_classes):
            print(f"类别 {i}: {np.sum(y==unique_classes[i])/len(y)}")
        # 创建模型
        self.model = MultiClassifierNet(
            input_size=self.input_size,
            num_classes=self.num_classes,
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
        return multi_class_f1_score(y_val, predictions, average=self.f1_average)

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
            return multi_class_f1_score(y, predictions, average=self.f1_average)
        elif metric == 'f1_macro':
            predictions = self.predict(X)
            return multi_class_f1_score(y, predictions, average='macro')
        elif metric == 'f1_micro':
            predictions = self.predict(X)
            return multi_class_f1_score(y, predictions, average='micro')
        elif metric == 'f1_weighted':
            predictions = self.predict(X)
            return multi_class_f1_score(y, predictions, average='weighted')
        else:
            raise ValueError(f"不支持的评估指标: {metric}")


class MultiLabelMultiClassifierNet(nn.Module):
    """多标签多分类神经网络模型"""

    def __init__(self, input_size, num_labels, num_classes_per_label, hidden_size=128,
                 num_layers=3, dropout_prob=0.1, shared_layers=True):
        super(MultiLabelMultiClassifierNet, self).__init__()

        self.num_labels = num_labels
        self.num_classes_per_label = num_classes_per_label
        self.shared_layers = shared_layers

        if shared_layers:
            # 共享底层特征提取
            shared_layers_list = []
            shared_layers_list.append(nn.Linear(input_size, hidden_size))
            shared_layers_list.append(nn.ReLU())
            shared_layers_list.append(nn.Dropout(dropout_prob))

            for _ in range(num_layers - 2):
                shared_layers_list.append(nn.Linear(hidden_size, hidden_size))
                shared_layers_list.append(nn.ReLU())
                shared_layers_list.append(nn.Dropout(dropout_prob))

            self.shared_network = nn.Sequential(*shared_layers_list)

            # 每个标签的分类头
            self.label_classifiers = nn.ModuleList()
            for i in range(num_labels):
                if isinstance(num_classes_per_label, list):
                    num_classes = num_classes_per_label[i]
                else:
                    num_classes = num_classes_per_label

                classifier = nn.Linear(hidden_size, num_classes)
                self.label_classifiers.append(classifier)
        else:
            # 每个标签独立的网络
            self.label_networks = nn.ModuleList()

            for i in range(num_labels):
                if isinstance(num_classes_per_label, list):
                    num_classes = num_classes_per_label[i]
                else:
                    num_classes = num_classes_per_label

                layers = []
                layers.append(nn.Linear(input_size, hidden_size))
                layers.append(nn.ReLU())
                layers.append(nn.Dropout(dropout_prob))

                for _ in range(num_layers - 2):
                    layers.append(nn.Linear(hidden_size, hidden_size))
                    layers.append(nn.ReLU())
                    layers.append(nn.Dropout(dropout_prob))

                layers.append(nn.Linear(hidden_size, num_classes))

                self.label_networks.append(nn.Sequential(*layers))

    def forward(self, x):
        outputs = []

        if self.shared_layers:
            # 共享特征提取
            shared_features = self.shared_network(x)

            # 每个标签的分类
            for classifier in self.label_classifiers:
                output = classifier(shared_features)
                outputs.append(output)
        else:
            # 独立网络
            for network in self.label_networks:
                output = network(x)
                outputs.append(output)

        return outputs


class MultiLabelMultiClassifierModel:
    """
    多标签多分类模型。
    每个样本可以同时属于多个标签，每个标签都是一个多分类问题。
    """

    def __init__(self, hyperparameters=None, shared_layers=True):
        self.hyperparameters = hyperparameters or {}
        self.shared_layers = shared_layers
        self.model = None
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        self.input_size = None
        self.num_labels = None
        self.num_classes_per_label = None
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

    def fit(self, X, y, X_val=None, y_val=None):
        """训练模型"""

        # 获取输入特征维度和标签信息
        self.input_size = X.shape[1]

        # 处理标签数据
        if isinstance(y, pd.DataFrame):
            self.num_labels = y.shape[1]
            self.label_names = y.columns.tolist()
            y_array = y.values
        else:
            # numpy数组
            self.num_labels = y.shape[1] if len(y.shape) > 1 else 1
            self.label_names = [f'label_{i}' for i in range(self.num_labels)]
            y_array = y

        # 确定每个标签的类别数量
        self.num_classes_per_label = []
        for i in range(self.num_labels):
            unique_classes = np.unique(y_array[:, i])
            self.num_classes_per_label.append(len(unique_classes))
            print(
                f"标签 '{self.label_names[i]}' 有 {len(unique_classes)} 个类别: {unique_classes}")

        # 创建模型
        self.model = MultiLabelMultiClassifierNet(
            input_size=self.input_size,
            num_labels=self.num_labels,
            num_classes_per_label=self.num_classes_per_label,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            dropout_prob=self.dropout_prob,
            shared_layers=self.shared_layers
        ).to(self.device)

        # 创建数据集
        X_tensor = torch.FloatTensor(
            X.values if isinstance(X, pd.DataFrame) else X)
        y_tensors = []
        for i in range(self.num_labels):
            y_tensors.append(torch.LongTensor(y_array[:, i]))

        train_dataset = torch.utils.data.TensorDataset(X_tensor, *y_tensors)
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
            y_val_array = y_val.values if isinstance(
                y_val, pd.DataFrame) else y_val
            y_val_tensors = []
            for i in range(self.num_labels):
                y_val_tensors.append(torch.LongTensor(y_val_array[:, i]))

            val_dataset = torch.utils.data.TensorDataset(
                X_val_tensor, *y_val_tensors)
            val_loader = DataLoader(
                val_dataset, batch_size=self.batch_size, shuffle=False)

        # 损失函数和优化器
        criterions = [nn.CrossEntropyLoss() for _ in range(self.num_labels)]
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)

        # 训练循环
        for epoch in range(self.num_epochs):
            # 训练阶段
            self.model.train()
            total_loss = 0
            for batch_data in train_loader:
                batch_X = batch_data[0].to(self.device)
                batch_y_list = [
                    batch_data[i+1].to(self.device) for i in range(self.num_labels)]

                optimizer.zero_grad()
                outputs = self.model(batch_X)

                # 计算每个标签的损失
                loss = 0
                for i in range(self.num_labels):
                    loss += criterions[i](outputs[i], batch_y_list[i])

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
        """在数据加载器上评估模型F1分数（所有标签的宏平均）"""
        self.model.eval()
        all_predictions = [[] for _ in range(self.num_labels)]
        all_targets = [[] for _ in range(self.num_labels)]

        with torch.no_grad():
            for batch_data in data_loader:
                batch_X = batch_data[0].to(self.device)
                batch_y_list = [
                    batch_data[i+1].to(self.device) for i in range(self.num_labels)]

                outputs = self.model(batch_X)

                for i in range(self.num_labels):
                    _, predicted = torch.max(outputs[i], 1)
                    all_predictions[i].append(predicted.cpu().numpy())
                    all_targets[i].append(batch_y_list[i].cpu().numpy())

        # 计算每个标签的F1分数
        f1_scores = []
        for i in range(self.num_labels):
            predictions = np.concatenate(all_predictions[i])
            targets = np.concatenate(all_targets[i])
            f1 = multi_class_f1_score(targets, predictions, average='macro')
            f1_scores.append(f1)

        return np.mean(f1_scores)  # 返回所有标签F1的平均值

    def predict(self, X):
        """预测"""
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用fit方法")

        self.model.eval()
        X_tensor = torch.FloatTensor(X.values if isinstance(
            X, pd.DataFrame) else X).to(self.device)

        predictions = []
        with torch.no_grad():
            outputs = self.model(X_tensor)
            for i in range(self.num_labels):
                _, predicted = torch.max(outputs[i], 1)
                predictions.append(predicted.cpu().numpy())

        # 转换为numpy数组格式 (n_samples, n_labels)
        return np.column_stack(predictions)

    def predict_proba(self, X):
        """预测概率"""
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用fit方法")

        self.model.eval()
        X_tensor = torch.FloatTensor(X.values if isinstance(
            X, pd.DataFrame) else X).to(self.device)

        probabilities = []
        with torch.no_grad():
            outputs = self.model(X_tensor)
            for i in range(self.num_labels):
                proba = torch.softmax(outputs[i], dim=1)
                probabilities.append(proba.cpu().numpy())

        return probabilities  # 返回每个标签的概率分布列表

    def score(self, X, y, metric='f1_macro'):
        """计算评估指标"""
        predictions = self.predict(X)

        if metric == 'f1_macro':
            # 所有标签的宏平均F1
            f1_scores = []
            y_array = y.values if isinstance(y, pd.DataFrame) else y
            for i in range(self.num_labels):
                f1 = multi_class_f1_score(
                    y_array[:, i], predictions[:, i], average='macro')
                f1_scores.append(f1)
            return np.mean(f1_scores)
        elif metric == 'f1_micro':
            # 所有标签的微平均F1
            f1_scores = []
            y_array = y.values if isinstance(y, pd.DataFrame) else y
            for i in range(self.num_labels):
                f1 = multi_class_f1_score(
                    y_array[:, i], predictions[:, i], average='micro')
                f1_scores.append(f1)
            return np.mean(f1_scores)
        elif metric == 'accuracy':
            # 子集准确率（所有标签都正确才算正确）
            y_array = y.values if isinstance(y, pd.DataFrame) else y
            exact_matches = np.all(y_array == predictions, axis=1)
            return np.mean(exact_matches)
        elif metric == 'label_accuracy':
            # 每个标签的平均准确率
            accuracies = []
            y_array = y.values if isinstance(y, pd.DataFrame) else y
            for i in range(self.num_labels):
                acc = accuracy_score(y_array[:, i], predictions[:, i])
                accuracies.append(acc)
            return np.mean(accuracies)
        else:
            raise ValueError(f"不支持的评估指标: {metric}")

    def get_label_scores(self, X, y):
        """获取每个标签的详细评估结果"""
        predictions = self.predict(X)
        y_array = y.values if isinstance(y, pd.DataFrame) else y

        results = {}
        for i, label_name in enumerate(self.label_names):
            acc = accuracy_score(y_array[:, i], predictions[:, i])
            f1_macro = multi_class_f1_score(
                y_array[:, i], predictions[:, i], average='macro')
            f1_micro = multi_class_f1_score(
                y_array[:, i], predictions[:, i], average='micro')
            f1_weighted = multi_class_f1_score(
                y_array[:, i], predictions[:, i], average='weighted')

            results[label_name] = {
                'accuracy': acc,
                'f1_macro': f1_macro,
                'f1_micro': f1_micro,
                'f1_weighted': f1_weighted
            }

        return results


def train_multi_label_multi_class(df_train, df_val, label_columns, shared_layers=True):
    """训练多标签多分类模型"""
    print(f"\n{'='*60}")
    print(f"训练多标签多分类模型 ({'共享层' if shared_layers else '独立层'})")
    print(f"{'='*60}")

    # 分离特征和标签
    feature_columns = [
        col for col in df_train.columns if col not in label_columns]

    X_train = df_train[feature_columns]
    y_train = df_train[label_columns]
    X_val = df_val[feature_columns]
    y_val = df_val[label_columns]

    print(f"训练数据形状: X_train {X_train.shape}, y_train {y_train.shape}")
    print(f"验证数据形状: X_val {X_val.shape}, y_val {y_val.shape}")

    # 创建多标签多分类模型实例
    model = MultiLabelMultiClassifierModel(
        hyperparameters={
            'learning_rate': 0.001,
            'batch_size': 64,
            'num_epochs': 50,
            'num_layers': 3,
            'hidden_size': 128,
            'dropout_prob': 0.2,
            'patience': 5,
            'use_early_stopping': True
        },
        shared_layers=shared_layers
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
    train_label_acc = model.score(X_train, y_train, metric='label_accuracy')

    print(f"  宏平均F1: {train_f1_macro:.4f}")
    print(f"  微平均F1: {train_f1_micro:.4f}")
    print(f"  子集准确率: {train_accuracy:.4f}")
    print(f"  标签平均准确率: {train_label_acc:.4f}")

    # 验证集评估
    print("\n验证集评估:")
    val_f1_macro = model.score(X_val, y_val, metric='f1_macro')
    val_f1_micro = model.score(X_val, y_val, metric='f1_micro')
    val_accuracy = model.score(X_val, y_val, metric='accuracy')
    val_label_acc = model.score(X_val, y_val, metric='label_accuracy')

    print(f"  宏平均F1: {val_f1_macro:.4f}")
    print(f"  微平均F1: {val_f1_micro:.4f}")
    print(f"  子集准确率: {val_accuracy:.4f}")
    print(f"  标签平均准确率: {val_label_acc:.4f}")

    # 每个标签的详细评估
    print("\n各标签详细评估 (验证集):")
    label_scores = model.get_label_scores(X_val, y_val)
    for label_name, scores in label_scores.items():
        print(f"  {label_name}:")
        print(f"    准确率: {scores['accuracy']:.4f}")
        print(f"    F1宏平均: {scores['f1_macro']:.4f}")
        print(f"    F1微平均: {scores['f1_micro']:.4f}")
        print(f"    F1加权平均: {scores['f1_weighted']:.4f}")

    # 预测示例
    print(f"\n{'='*20} 预测示例 {'='*20}")
    sample_predictions = model.predict(X_val.iloc[:5])
    sample_probabilities = model.predict_proba(X_val.iloc[:5])

    print("前5个样本的预测结果:")
    for i in range(5):
        print(f"\n样本 {i+1}:")
        print(f"  真实标签: {y_val.iloc[i].values}")
        print(f"  预测标签: {sample_predictions[i]}")

        for j, label in enumerate(label_columns):
            true_class = int(y_val.iloc[i, j])
            pred_class = int(sample_predictions[i, j])
            class_probs = sample_probabilities[j][i]
            max_prob = np.max(class_probs)
            print(f"    {label}: 真实={true_class}, 预测={pred_class}, "
                  f"最高概率={max_prob:.3f} (类别{np.argmax(class_probs)})")

    return model


def train_single_label_multi_class(df_train, df_val, label_column):
    """训练多分类模型"""
    X_train = df_train.drop(columns=[label_column])
    y_train = df_train[label_column]
    X_val = df_val.drop(columns=[label_column])
    y_val = df_val[label_column]

    # 创建模型实例
    model = MultiClassifierModel(
        hyperparameters={
            'learning_rate': 0.01,
            'batch_size': 32,
            'num_layers': 3,
            'hidden_size': 64,
            'dropout_prob': 0.2,
            'patience': 10,
            'use_early_stopping': True,
            'f1_average': 'macro'  # 使用macro平均的F1
        }
    )

    model.fit(
        X=X_train,
        y=y_train,
        X_val=X_val,
        y_val=y_val
    )
    print("模型训练完成！")

    # 评估模型
    train_acc = model.score(X_train, y_train, metric='accuracy')
    print(f"训练集accuracy得分：{train_acc:.4f}")

    train_f1_macro = model.score(X_train, y_train, metric='f1_macro')
    print(f"训练集f1_macro得分：{train_f1_macro:.4f}")

    train_f1_micro = model.score(X_train, y_train, metric='f1_micro')
    print(f"训练集f1_micro得分：{train_f1_micro:.4f}")

    train_f1_weighted = model.score(X_train, y_train, metric='f1_weighted')
    print(f"训练集f1_weighted得分：{train_f1_weighted:.4f}")

    val_acc = model.score(X_val, y_val, metric='accuracy')
    print(f"验证集accuracy得分：{val_acc:.4f}")

    val_f1_macro = model.score(X_val, y_val, metric='f1_macro')
    print(f"验证集f1_macro得分：{val_f1_macro:.4f}")

    val_f1_micro = model.score(X_val, y_val, metric='f1_micro')
    print(f"验证集f1_micro得分：{val_f1_micro:.4f}")

    val_f1_weighted = model.score(X_val, y_val, metric='f1_weighted')
    print(f"验证集f1_weighted得分：{val_f1_weighted:.4f}")
