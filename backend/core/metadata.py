import pandas as pd
import io
class MetadataEngine:
    @staticmethod
    def generate_metadata(df):
        return {
            "columns": list(df.columns),
            "dtypes": {k: str(v) for k, v in df.dtypes.items()},
            "shape": df.shape,
            "missing_values": df.isnull().sum().to_dict(),
            "sample_data": df.head(3).to_dict(orient='records')
        }
