import streamlit as st

def display_kpi_card(rank, row):
    """상위 상권 요약 KPI 카드를 화면에 렌더링합니다."""
    st.subheader(f"🏆 {rank}위 상권 요약: {row['gu_name']} {row['dong_name']}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("블루오션 지수", f"{int(row['blue_ocean_score']):,}")
    c2.metric("주간 활동 배율", f"{row['activity_ratio']:.1f}배", "거주민 대비 유입량")
    c3.metric("점포당 잠재고객", f"{int(row['pop_per_cafe']):,}명")
    c4.metric("경쟁 카페 수", f"{int(row['cafe_count'])}개")