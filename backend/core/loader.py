import pandas as pd
from backend.utils.logger import get_logger
logger = get_logger("DataLoader")
class DataLoader:
    @staticmethod
    def load_file(uploaded_file):
        try:
            if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
            else: df = pd.read_excel(uploaded_file)
            return df, None
        except Exception as e: return None, str(e)
