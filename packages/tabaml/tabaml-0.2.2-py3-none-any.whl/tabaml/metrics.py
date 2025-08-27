import numpy as np


def accuracy_score(y_true, y_pred):
    """
    计算准确率
    Args:
        y_true: 真实标签 (numpy array)
        y_pred: 预测标签 (numpy array) 
    Returns:
        float: 准确率
    """
    return np.mean(y_true == y_pred)


def precision_score(y_true, y_pred):
    """
    计算精确率 (查准率)
    Args:
        y_true: 真实标签 (numpy array)
        y_pred: 预测标签 (numpy array)
    Returns:
        float: 精确率
    """
    # TP: 预测为正例且实际为正例
    true_positives = np.sum((y_pred == 1) & (y_true == 1))
    # FP: 预测为正例但实际为负例
    false_positives = np.sum((y_pred == 1) & (y_true == 0))

    if true_positives + false_positives == 0:
        return 0.0

    return true_positives / (true_positives + false_positives)


def recall_score(y_true, y_pred):
    """
    计算召回率 (查全率)
    Args:
        y_true: 真实标签 (numpy array)
        y_pred: 预测标签 (numpy array)
    Returns:
        float: 召回率
    """
    # TP: 预测为正例且实际为正例
    true_positives = np.sum((y_pred == 1) & (y_true == 1))
    # FN: 预测为负例但实际为正例
    false_negatives = np.sum((y_pred == 0) & (y_true == 1))

    if true_positives + false_negatives == 0:
        return 0.0

    return true_positives / (true_positives + false_negatives)


def f1_score(y_true, y_pred):
    """
    计算F1分数
    Args:
        y_true: 真实标签 (numpy array)
        y_pred: 预测标签 (numpy array)
    Returns:
        float: F1分数
    """
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)

    if prec + rec == 0:
        return 0.0

    return 2 * (prec * rec) / (prec + rec)


def roc_auc_score(y_true, y_scores):
    """
    计算ROC曲线下面积
    Args:
        y_true: 真实标签 (numpy array)
        y_scores: 预测概率分数 (numpy array)
    Returns:
        float: AUC值
    """
    # 确保输入为numpy数组
    y_true = np.array(y_true)
    y_scores = np.array(y_scores)

    # 获取排序索引（按分数降序）
    desc_score_indices = np.argsort(y_scores)[::-1]
    y_true_sorted = y_true[desc_score_indices]
    y_scores_sorted = y_scores[desc_score_indices]

    # 获取唯一的阈值
    distinct_value_indices = np.where(np.diff(y_scores_sorted))[0]
    threshold_idxs = np.r_[distinct_value_indices, y_true.size - 1]

    # 计算TPR和FPR
    tps = np.cumsum(y_true_sorted)[threshold_idxs]
    fps = 1 + threshold_idxs - tps

    # 添加起始点
    tps = np.r_[0, tps]
    fps = np.r_[0, fps]

    # 计算TPR和FPR
    if tps[-1] <= 0:
        return 0.5

    fpr = fps / fps[-1]
    tpr = tps / tps[-1]

    # 使用梯形法则计算AUC
    return np.trapezoid(tpr, fpr)


def multi_class_f1_score(y_true, y_pred, average='macro'):
    """
    计算多分类F1分数
    Args:
        y_true: 真实标签
        y_pred: 预测标签  
        average: 'macro', 'micro', 'weighted'
    Returns:
        float: F1分数
    """
    # 转换为numpy数组
    if hasattr(y_true, 'values'):
        y_true = y_true.values
    if hasattr(y_pred, 'values'):
        y_pred = y_pred.values

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    # 获取所有类别
    classes = np.unique(np.concatenate([y_true, y_pred]))

    if average == 'micro':
        # Micro平均：计算全局的TP, FP, FN
        tp = np.sum(y_true == y_pred)
        fp_fn = np.sum(y_true != y_pred)
        if tp + fp_fn == 0:
            return 0.0
        precision = recall = tp / (tp + fp_fn)
        if precision + recall == 0:
            return 0.0
        return 2 * precision * recall / (precision + recall)

    elif average == 'macro':
        # Macro平均：计算每个类别的F1，然后平均
        f1_scores = []
        for cls in classes:
            tp = np.sum((y_true == cls) & (y_pred == cls))
            fp = np.sum((y_true != cls) & (y_pred == cls))
            fn = np.sum((y_true == cls) & (y_pred != cls))

            if tp + fp == 0:
                precision = 0.0
            else:
                precision = tp / (tp + fp)

            if tp + fn == 0:
                recall = 0.0
            else:
                recall = tp / (tp + fn)

            if precision + recall == 0:
                f1 = 0.0
            else:
                f1 = 2 * precision * recall / (precision + recall)

            f1_scores.append(f1)

        return np.mean(f1_scores)

    elif average == 'weighted':
        # 加权平均：按照每个类别的支持数加权
        f1_scores = []
        weights = []
        for cls in classes:
            support = np.sum(y_true == cls)
            if support == 0:
                continue

            tp = np.sum((y_true == cls) & (y_pred == cls))
            fp = np.sum((y_true != cls) & (y_pred == cls))
            fn = np.sum((y_true == cls) & (y_pred != cls))

            if tp + fp == 0:
                precision = 0.0
            else:
                precision = tp / (tp + fp)

            if tp + fn == 0:
                recall = 0.0
            else:
                recall = tp / (tp + fn)

            if precision + recall == 0:
                f1 = 0.0
            else:
                f1 = 2 * precision * recall / (precision + recall)

            f1_scores.append(f1)
            weights.append(support)

        if not weights:
            return 0.0
        return np.average(f1_scores, weights=weights)

    else:
        raise ValueError(f"不支持的平均方式: {average}")
