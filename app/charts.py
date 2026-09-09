import plotly.express as px

def draw_horizontal_bar(df_top10):
    fig = px.bar(
        df_top10, 
        x='blue_ocean_score', 
        y='dong_name', 
        orientation='h',
        text_auto='.0f',
        labels={'blue_ocean_score': '블루오션 지수', 'dong_name': '행정동'}
    )
    fig.update_layout(
        height=500, 
        yaxis={'categoryorder': 'total ascending'} 
    )
    return fig

def draw_line_chart(df_hourly, target_region):
    fig = px.line(
        df_hourly, 
        x='time_hour', 
        y='avg_pop_2030',
        markers=True,
        labels={'time_hour': '시간대 (시)', 'avg_pop_2030': '평균 유동인구(명)'}
    )
    fig.update_xaxes(tickvals=list(range(24)), range=[-0.5, 23.5])
    fig.update_layout(height=500)
    return fig