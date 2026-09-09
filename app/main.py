import streamlit as st
import pandas as pd
from repository import get_blueocean_kpi, get_hourly_pattern
from charts import draw_horizontal_bar, draw_line_chart

st.set_page_config(page_title="2030 카페 상권 분석", layout="wide")

df_kpi = get_blueocean_kpi()
df_kpi_top10 = df_kpi.sort_values(by='blue_ocean_score', ascending=False).head(10)

with st.sidebar:
    st.header("상권 상세 검색")
    target_region = st.selectbox(
        "분석할 행정동을 선택하세요:",
        options=df_kpi_top10['dong_name'].tolist()
    )
    st.markdown("---")
    st.markdown("**데이터 추출**")
    csv = df_kpi_top10.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="Top 10 상권 데이터 다운로드",
        data=csv,
        file_name='top10_cafe_kpi.csv',
        mime='text/csv',
    )

top3_dongs = df_kpi_top10['dong_name'].head(3).tolist()
dynamic_title = f"{'·'.join(top3_dongs)}, 2030 타겟 카페 창업 최적 입지로 도출되었습니다"

st.title(dynamic_title)
st.markdown("거주 인구 대비 유동 인구가 풍부하고 경쟁 점포가 적은 블루오션 상권 분석 결과입니다.")

selected_kpi = df_kpi_top10[df_kpi_top10['dong_name'] == target_region].iloc[0]

avg_blue_ocean = df_kpi_top10['blue_ocean_score'].mean()
avg_living_pop = df_kpi_top10['living_pop_2030'].mean()
avg_activity = df_kpi_top10['activity_ratio'].mean()
avg_pop_per_cafe = df_kpi_top10['pop_per_cafe'].mean()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    label="블루오션 지수", 
    value=f"{selected_kpi['blue_ocean_score']:,.1f}점",
    delta=f"{(selected_kpi['blue_ocean_score'] - avg_blue_ocean):+,.1f}점 (Top 10 평균 대비)"
)
c2.metric(
    label="2030 일평균 유동인구", 
    value=f"{int(selected_kpi['living_pop_2030']):,}명",
    delta=f"{(selected_kpi['living_pop_2030'] - avg_living_pop):+,.0f}명 (Top 10 평균 대비)"
)
c3.metric(
    label="주간 활동 배율 (유동/거주)", 
    value=f"{selected_kpi['activity_ratio']:.1f}배",
    delta=f"{(selected_kpi['activity_ratio'] - avg_activity):+,.1f}배 (Top 10 평균 대비)"
)
c4.metric(
    label="점포당 2030 잠재고객", 
    value=f"{int(selected_kpi['pop_per_cafe']):,}명",
    delta=f"{(selected_kpi['pop_per_cafe'] - avg_pop_per_cafe):+,.0f}명 (Top 10 평균 대비)"
)


st.markdown("---")

tab1, tab2, tab3 = st.tabs(["상황 - 전체 시장", "문제 - 상권별 격차", "근거 - 상세 프로파일"])

with tab1:
    st.subheader("거주인구와 유동인구는 비례하지 않습니다")
    st.write("단순히 주거지가 밀집된 곳이 아닌, 외부 2030 인구를 강하게 끌어들이는 상권을 발굴해야 합니다.")
    
    display_df = df_kpi_top10[['dong_name', 'living_pop_2030', 'resident_pop_2030', 'activity_ratio', 'cafe_count']].rename(columns={
        'dong_name': '행정동명',
        'living_pop_2030': '2030 유동인구(명)',
        'resident_pop_2030': '2030 거주인구(명)',
        'activity_ratio': '주간 활동 배율',
        'cafe_count': '경쟁 카페 수(개)'
    })
    
    st.dataframe(display_df, use_container_width=True)

with tab2:
    st.subheader("상권별 블루오션 지수 격차 (Top 10)")
    st.caption("차트 설명: 유동인구(수요) 대비 경쟁 카페 수(공급)를 교차 연산한 '블루오션 지수'를 비교한 정렬형 가로 막대 차트입니다.")
    
    if not df_kpi_top10.empty:
        fig_bar = draw_horizontal_bar(df_kpi_top10)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("현재 분석 가능한 상권 데이터가 부족합니다. 파이프라인 수집 상태를 확인해주세요.")

with tab3:
    st.subheader(f"[{target_region}] 24시간 시간대별 유동인구 추이")
    st.caption("차트 설명: 해당 상권의 시간에 따른 유동인구 변동 흐름을 보여주는 선 그래프입니다. 피크 타임에 맞춘 인력 배치 전략 수립에 활용할 수 있습니다.")
    
    target_code = selected_kpi['region_code']
    df_hourly = get_hourly_pattern(target_code)
    
    if not df_hourly.empty:
        fig_line = draw_line_chart(df_hourly, target_region)
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("해당 지역의 시간대별 데이터가 존재하지 않습니다.")

st.markdown("---")

st.caption("""
**[데이터 한계 및 가정사항]**
* **데이터 기준시점:** 2026년 7월 15일(수) 24시간 생활인구 기준이며, 요일 및 계절적 요인은 반영되지 않았습니다.
* **가정사항:** 경쟁 카페 수는 '카페/커피숍' 중분류 기준이며, 개별 매장의 면적이나 브랜드 파워는 동일하다고 가정했습니다.
* **수집 제약:** 서울시 OpenAPI의 일일 트래픽 한도 및 데이터 제공 주기에 따라 최신화 시점이 일부 지연될 수 있습니다.
""")