import plotly.express as px
import pandas as pd

class DataVisualizer:
    @staticmethod
    def auto_generate_charts(df):
        charts = []
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # 1. HEATMAP (Dark Template)
        if len(num_cols) > 1:
            corr = df[num_cols].corr()
            fig = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', 
                            title="<b>Correlation Matrix</b>", template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            charts.append({"title": "Heatmap", "fig": fig, "type": "wide"})

        # 2. DISTRIBUTION (Top 3)
        for col in num_cols[:3]:
            fig = px.histogram(df, x=col, title=f"<b>Dist: {col}</b>", 
                               color_discrete_sequence=['#4c8bf5'], template="plotly_dark")
            fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            charts.append({"title": f"Dist {col}", "fig": fig, "type": "normal"})

        # 3. CATEGORY COUNTS (Top 3)
        for col in cat_cols[:3]:
            if df[col].nunique() < 15:
                counts = df[col].value_counts().reset_index()
                counts.columns = ['category', 'count']
                fig = px.bar(counts, x='category', y='count', color='count', 
                             title=f"<b>Count: {col}</b>", template="plotly_dark",
                             color_continuous_scale='Viridis')
                fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                charts.append({"title": f"Count {col}", "fig": fig, "type": "normal"})

        # 4. SCATTER (Top 2)
        if len(num_cols) >= 2:
            for i in range(min(2, len(num_cols)-1)):
                c1 = num_cols[i]
                c2 = num_cols[i+1]
                fig = px.scatter(df, x=c1, y=c2, title=f"<b>{c1} vs {c2}</b>", 
                                 opacity=0.8, template="plotly_dark", color_discrete_sequence=['#00d26a'])
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                charts.append({"title": f"Scatter {i}", "fig": fig, "type": "normal"})

        return charts

    @staticmethod
    def create_chart(df, viz_config):
        if not viz_config: return None
        ctype = viz_config.get('chart_type')
        x = viz_config.get('x')
        y = viz_config.get('y')
        try:
            # Force Dark Mode template on all AI charts
            kwargs = {"template": "plotly_dark"}
            if ctype == 'bar': return px.bar(df, x=x, y=y, title=f"{y} by {x}", **kwargs)
            if ctype == 'line': return px.line(df, x=x, y=y, title=f"{y} over {x}", **kwargs)
            if ctype == 'scatter': return px.scatter(df, x=x, y=y, title=f"{y} vs {x}", **kwargs)
            if ctype == 'histogram': return px.histogram(df, x=x, title=f"Dist of {x}", **kwargs)
            if ctype == 'heatmap': return px.imshow(df.select_dtypes(include='number').corr(), text_auto=True, **kwargs)
        except: return None
        return None
