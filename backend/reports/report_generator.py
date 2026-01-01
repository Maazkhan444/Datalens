import pandas as pd
class ReportGenerator:
    @staticmethod
    def generate_html_report(df):
        return f"<html><body><h1>Analysis Report</h1><p>Rows: {len(df)}</p>{df.describe().to_html()}</body></html>"
