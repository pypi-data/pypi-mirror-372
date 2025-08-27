import pickle
import pandas as pd


class ColumnType:
    CATEGORICAL = 'categorical'
    NUMERICAL = 'numerical'
    DATETIME = 'datetime'
    BOOLEAN = 'boolean'
    OTHER = 'other'

    def __init__(self,df:pd.DataFrame):
        self.df = df

    def is_categorical(self,col):
        """
        判断是否为类别型.
        """
        threshold = 100 if self.df.shape[0] > 10000 else int(100/self.df.shape[0])
        return self.df[col].nunique() < threshold

    def is_numerical(self,col):
        """
        判断是否为数值型
        """
        return self.df[col].dtype == 'float64' or self.df[col].dtype == 'int64'

    def is_datetime(self,col):
        """
        判断是否为时间型
        """
        return self.df[col].dtype == 'datetime64[ns]'

    def is_boolean(self,col):
        """
        判断是否为布尔型
        """
        bool_values = self.df[col].unique()
        if self.df[col].nunique() == 2:
            return True,
        else:
            return False

    def get_column_type(self,col):
        """
        获取列类型
        """
        if self.is_categorical(col):
            return ColumnType.CATEGORICAL
        elif self.is_numerical(col):
            return ColumnType.NUMERICAL
        elif self.is_datetime(col):
            return ColumnType.DATETIME
        elif self.is_boolean(col):
            return ColumnType.BOOLEAN
        else:
            return ColumnType.OTHER

    def guess_columns_type(self):
        """
        猜测列类型
        """
        column_types = {}
        for col in self.df.columns:
            column_types[col] = self.get_column_type(col)
        return column_types

    def check_column_type(self,column_types:dict):
        """
        检查列类型是否正确
        """
        for col, col_type in column_types.items():
            if self.get_column_type(col) != col_type:
                print(f"列`{col}`类型错误, 正确类型为`{col_type}`, 实际类型为`{self.get_column_type(col)}`")
                return False
        return True

def save_model(model, path, model_config: dict):
    with open(path, 'wb') as f:
        pickle.dump(model, f)

def load_model(path):
    with open(path, 'rb') as f:
        return pickle.load(f)
