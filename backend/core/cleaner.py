import pandas as pd
import numpy as np
from backend.utils.logger import get_logger

logger = get_logger("DataCleaner")

class DataCleaner:
    def __init__(self, df):
        self.df = df
        self.log = []

    def auto_clean(self):
        """Runs a full cleaning pipeline automatically without user input"""
        initial_rows = len(self.df)
        
        # 1. Drop Duplicates
        self.df = self.df.drop_duplicates()
        if len(self.df) < initial_rows:
            self.log.append(f"Removed {initial_rows - len(self.df)} duplicate rows")

        # 2. Handle Missing Values
        for col in self.df.columns:
            if self.df[col].isnull().sum() > 0:
                # If numeric, fill with median (robust to outliers)
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    fill_val = self.df[col].median()
                    self.df[col] = self.df[col].fillna(fill_val)
                    self.log.append(f"Filled missing numbers in '{col}' with median: {fill_val}")
                
                # If categorical, fill with mode (most frequent)
                else:
                    if not self.df[col].mode().empty:
                        fill_val = self.df[col].mode()[0]
                        self.df[col] = self.df[col].fillna(fill_val)
                        self.log.append(f"Filled missing text in '{col}' with mode: {fill_val}")
        
        return self.df, self.log

    def execute_action(self, action_dict):
        # ... (Keeps chat-based cleaning capability) ...
        operation = action_dict.get('operation')
        targets = action_dict.get('target_columns', [])
        params = action_dict.get('parameters', {})
        
        try:
            if operation == 'remove_duplicates':
                self.df = self.df.drop_duplicates()
                return "Removed duplicates."
            elif operation == 'fill_missing':
                method = params.get('method', 'mean')
                for col in targets:
                    if col in self.df.columns and pd.api.types.is_numeric_dtype(self.df[col]):
                         self.df[col] = self.df[col].fillna(self.df[col].mean())
                return f"Filled missing values in {targets}"
            elif operation == 'remove_outliers':
                # IQR Method
                for col in targets:
                     if col in self.df.columns and pd.api.types.is_numeric_dtype(self.df[col]):
                        Q1 = self.df[col].quantile(0.25)
                        Q3 = self.df[col].quantile(0.75)
                        IQR = Q3 - Q1
                        self.df = self.df[~((self.df[col] < (Q1 - 1.5 * IQR)) | (self.df[col] > (Q3 + 1.5 * IQR)))]
                return f"Removed outliers in {targets}"
            return "Operation done."
        except Exception as e:
            return f"Error: {e}"

    def get_dataframe(self):
        return self.df
