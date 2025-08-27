

from generate import generate_multi_label_data, generate_multi_label_multi_class_data
from binary_cls import train_multi_label_binary_cls, train_single_label_binary_cls
from multi_cls import train_multi_label_multi_class, train_single_label_multi_class

if __name__ == "__main__":

    # 生成多标签数据
    print("正在生成多标签分类数据...")
    df_train, df_val, label_names = generate_multi_label_data(
        n_samples=2000, n_features=768, n_labels=4)

    print("\n" + "="*80)
    print("开始训练多标签分类模型...")

    # 训练独立模式的多标签模型
    print("\n1. 训练独立模式的多标签模型:")
    independent_model = train_multi_label_binary_cls(
        df_train, df_val, label_names, dependent_mode=False)

    # 训练相关模式的多标签模型
    print("\n2. 训练相关模式的多标签模型:")
    dependent_model = train_multi_label_binary_cls(
        df_train, df_val, label_names, dependent_mode=True)

    print("\n" + "="*80)
    print("多标签分类测试完成！")

    # 默认运行二分类训练
    train_single_label_binary_cls(df_train, df_val, label_names[0])

    print("\n" + "="*80)
    # 生成多标签多分类数据
    print("正在生成多标签多分类数据...")
    df_train, df_val, label_names = generate_multi_label_multi_class_data(
        n_samples=1500, n_features=50, n_labels=3)

    print("\n" + "="*80)
    print("开始训练多标签多分类模型...")

    # 训练共享层的多标签多分类模型
    print("\n1. 训练共享层的多标签多分类模型:")
    shared_model = train_multi_label_multi_class(df_train, df_val, label_names, shared_layers=True)

    # 训练独立层的多标签多分类模型
    print("\n2. 训练独立层的多标签多分类模型:")
    independent_model = train_multi_label_multi_class(
        df_train, df_val, label_names, shared_layers=False)

    print("\n" + "="*80)
    print("多标签多分类测试完成！")

    # 仅生成多标签多分类数据
    print("正在生成多标签多分类数据...")
    generate_multi_label_multi_class_data(
        n_samples=1500, n_features=50, n_labels=3)
    print("数据生成完成！")

    train_single_label_multi_class(df_train, df_val, label_names[0])
