import numpy as np
import pandas as pd


def generate_multi_label_data(n_samples=2000, n_features=768, n_labels=4, random_state=42):
    """
    生成多标签分类的模拟数据
    
    Args:
        n_samples: 样本数量
        n_features: 特征维度
        n_labels: 标签数量
        random_state: 随机种子
    """
    np.random.seed(random_state)
    
    # 生成特征数据 (模拟768维的向量特征)
    X = np.random.randn(n_samples, n_features).astype(np.float32)
    
    # 为了让数据更真实，添加一些结构化的模式
    # 每个标签与特征的不同子集相关
    labels = np.zeros((n_samples, n_labels), dtype=int)
    
    # 标签名称
    label_names = ['技术问题', '服务质量', '价格敏感', '用户体验']
    
    # 为每个标签创建不同的特征权重模式
    for label_idx in range(n_labels):
        # 每个标签关注不同的特征区间
        feature_start = label_idx * (n_features // n_labels)
        feature_end = (label_idx + 1) * (n_features // n_labels)
        
        # 计算该标签的概率（基于相关特征的线性组合）
        weights = np.random.randn(feature_end - feature_start) * 0.5
        feature_scores = X[:, feature_start:feature_end].dot(weights)
        
        # 添加一些随机噪声和偏置
        bias = np.random.randn() * 0.3
        noise = np.random.randn(n_samples) * 0.2
        scores = feature_scores + bias + noise
        
        # 使用sigmoid转换为概率，然后转换为二分类标签
        probabilities = 1 / (1 + np.exp(-scores))
        labels[:, label_idx] = (probabilities > 0.5).astype(int)
    
    # 添加标签之间的一些依赖关系
    # 例如：如果有技术问题，更可能有用户体验问题
    tech_issues = labels[:, 0] == 1
    labels[tech_issues, 3] = np.random.choice([0, 1], size=np.sum(tech_issues), p=[0.3, 0.7])
    
    # 如果服务质量不好，更可能对价格敏感
    service_issues = labels[:, 1] == 1
    labels[service_issues, 2] = np.random.choice([0, 1], size=np.sum(service_issues), p=[0.4, 0.6])
    
    # 创建特征列名
    feature_columns = [f'v_{i}' for i in range(n_features)]
    
    # 创建DataFrame
    df_features = pd.DataFrame(X, columns=feature_columns)
    df_labels = pd.DataFrame(labels, columns=label_names)
    
    # 合并特征和标签
    df = pd.concat([df_features, df_labels], axis=1)
    
    # 划分训练集和验证集
    train_size = int(0.8 * n_samples)
    df_train = df.iloc[:train_size]
    df_val = df.iloc[train_size:]
    
    print(f"生成的多标签数据统计:")
    print(f"总样本数: {n_samples}")
    print(f"特征维度: {n_features}")
    print(f"标签数量: {n_labels}")
    print(f"训练集大小: {len(df_train)}")
    print(f"验证集大小: {len(df_val)}")
    print("\n标签分布统计:")
    for i, label_name in enumerate(label_names):
        train_positive = df_train[label_name].sum()
        val_positive = df_val[label_name].sum()
        print(f"{label_name}: 训练集正例 {train_positive}/{len(df_train)} ({train_positive/len(df_train):.2%}), "
              f"验证集正例 {val_positive}/{len(df_val)} ({val_positive/len(df_val):.2%})")
    
    return df_train, df_val,label_names


def generate_multi_label_multi_class_data(n_samples=2000, n_features=50, n_labels=3, random_state=42):
    """
    生成多标签多分类的模拟数据

    Args:
        n_samples: 样本数量
        n_features: 特征维度
        n_labels: 标签数量
        random_state: 随机种子
    """
    np.random.seed(random_state)

    # 生成特征数据
    X = np.random.randn(n_samples, n_features).astype(np.float32)

    # 标签名称和每个标签的类别数
    label_names = ['产品类型', '服务等级', '用户群体']
    num_classes_per_label = [4, 3, 5]  # 分别有4、3、5个类别

    # 为了让数据更真实，添加一些结构化的模式
    labels = np.zeros((n_samples, n_labels), dtype=int)

    # 标签0: 产品类型 (4个类别: 0-基础版, 1-标准版, 2-高级版, 3-企业版)
    for i in range(n_samples):
        # 基于前几个特征的线性组合决定产品类型
        score = X[i, 0] + X[i, 1] * 0.5 + np.random.normal(0, 0.3)
        if score < -1:
            labels[i, 0] = 0  # 基础版
        elif score < 0:
            labels[i, 0] = 1  # 标准版
        elif score < 1:
            labels[i, 0] = 2  # 高级版
        else:
            labels[i, 0] = 3  # 企业版

    # 标签1: 服务等级 (3个类别: 0-普通, 1-优先, 2-VIP)
    for i in range(n_samples):
        # 服务等级与产品类型相关，高级产品更可能有高级服务
        product_type = labels[i, 0]
        base_score = X[i, 2] + X[i, 3] * 0.3

        # 产品类型影响服务等级概率
        if product_type >= 2:  # 高级版或企业版
            base_score += 1.0
        elif product_type >= 1:  # 标准版
            base_score += 0.3

        if base_score < -0.5:
            labels[i, 1] = 0  # 普通
        elif base_score < 0.8:
            labels[i, 1] = 1  # 优先
        else:
            labels[i, 1] = 2  # VIP

    # 标签2: 用户群体 (5个类别: 0-学生, 1-个人, 2-小企业, 3-中企业, 4-大企业)
    for i in range(n_samples):
        # 用户群体与前面两个标签都有关联
        product_type = labels[i, 0]
        service_level = labels[i, 1]

        base_score = X[i, 4] + X[i, 5] * 0.4

        # 产品类型和服务等级影响用户群体
        if product_type == 0:  # 基础版更可能是学生或个人
            base_score -= 1.5
        elif product_type == 3:  # 企业版更可能是企业用户
            base_score += 1.5

        if service_level == 2:  # VIP服务更可能是企业用户
            base_score += 1.0
        elif service_level == 0:  # 普通服务更可能是个人用户
            base_score -= 0.5

        if base_score < -1.5:
            labels[i, 2] = 0  # 学生
        elif base_score < -0.5:
            labels[i, 2] = 1  # 个人
        elif base_score < 0.5:
            labels[i, 2] = 2  # 小企业
        elif base_score < 1.5:
            labels[i, 2] = 3  # 中企业
        else:
            labels[i, 2] = 4  # 大企业

    # 创建特征列名
    feature_columns = [f'feature_{i}' for i in range(n_features)]

    # 创建DataFrame
    df_features = pd.DataFrame(X, columns=feature_columns)
    df_labels = pd.DataFrame(labels, columns=label_names)

    # 合并特征和标签
    df = pd.concat([df_features, df_labels], axis=1)

    # 划分训练集和验证集
    train_size = int(0.8 * n_samples)
    df_train = df.iloc[:train_size]
    df_val = df.iloc[train_size:]


    print(f"生成的多标签多分类数据统计:")
    print(f"总样本数: {n_samples}")
    print(f"特征维度: {n_features}")
    print(f"标签数量: {n_labels}")
    print(f"训练集大小: {len(df_train)}")
    print(f"验证集大小: {len(df_val)}")

    print("\n标签分布统计:")
    for i, (label_name, num_classes) in enumerate(zip(label_names, num_classes_per_label)):
        print(f"\n{label_name} ({num_classes}个类别):")
        train_dist = df_train[label_name].value_counts().sort_index()
        val_dist = df_val[label_name].value_counts().sort_index()
        for cls in range(num_classes):
            train_count = train_dist.get(cls, 0)
            val_count = val_dist.get(cls, 0)
            print(f"  类别{cls}: 训练集{train_count}/{len(df_train)} ({train_count/len(df_train):.2%}), "
                  f"验证集{val_count}/{len(df_val)} ({val_count/len(df_val):.2%})")

    return df_train, df_val,label_names
