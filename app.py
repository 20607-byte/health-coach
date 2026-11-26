import pickle
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from Orange.data import Table, Domain

# 페이지 기본 설정
st.set_page_config(
    page_title="AI 맞춤 헬스케어 코치",
    page_icon="🩺",
    layout="wide",
)

# 모델 로드 (캐싱 처리로 속도 최적화)
@st.cache_resource
def load_orange_model(model_path: str):
    with open(model_path, "rb") as f:
        return pickle.load(f)

try:
    model = load_orange_model("health_coach_model.pkcls")
except FileNotFoundError:
    st.error("⚠️ 'health_coach_model.pkcls' 파일을 찾을 수 없습니다. app.py와 같은 폴더에 배치해 주세요.")
    st.stop()

# 도넛 게이지 차트 생성 함수
def create_donut_gauge(prob: float):
    if prob >= 60:
        color = "#EF4444"  # 위험 (빨강)
        status = "집중 관리 필요"
    elif prob >= 40:
        color = "#F59E0B"  # 주의 (주황)
        status = "주의 관찰 단계"
    else:
        color = "#10B981"  # 양호 (초록)
        status = "비교적 양호"

    fig = go.Figure(
        data=[
            go.Pie(
                values=[prob, max(0.0, 100.0 - prob)],
                labels=["비만·혈압 주의 확률", "정상 유지 확률"],
                hole=0.72,
                marker_colors=[color, "#E5E7EB"],
                textinfo="none",
                hoverinfo="label+percent",
                sort=False,
            )
        ]
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=340,
        annotations=[
            dict(
                text=f"<span style='font-size:15px; color:#6B7280;'>비만·혈압 주의 확률</span><br>"
                     f"<b style='font-size:42px; color:{color};'>{prob:.1f}%</b><br>"
                     f"<span style='font-size:16px; color:#374151;'>[{status}]</span>",
                x=0.5,
                y=0.5,
                font_size=20,
                showarrow=False,
            )
        ],
    )
    return fig, status

# 생애주기별 맞춤 저염식 & 운동 가이드 생성 함수
def get_lifecycle_guide(age_group: str, job_type: str, gender: str):
    youth = ["19세이하", "20~24세", "25~29세", "30~34세", "35~39세"]
    middle = ["40~44세", "45~49세", "50~54세", "55~59세"]

    if age_group in youth:
        stage = "청년·사회초년기 (대사증후군 예방기)"
        diet = {
            "아침": "귀리 오트밀 + 무가당 그릭요거트 + 블루베리",
            "점심": "현미밥 2/3공기 + 닭가슴살 샐러드(발사믹 드레싱) + 두부구이",
            "저녁": "연어 포케(소스 절반만 사용) + 아보카도 + 방울토마토",
            "핵심 팁": "배달음식·국물 섭취를 줄이고, 나트륨 배출을 돕는 칼륨(바나나·토마토·시금치)을 챙기세요.",
        }
        exercise = [
            "**유산소 (주 3~4회, 30분 이상):** 빠른 걷기, 러닝, 실내 사이클 등 심박수를 높이는 운동",
            "**근력 (주 2~3회):** 스쿼트, 런지, 플랭크 등 기초대사량을 높이는 대근육 운동",
            "**생활 습관:** 좌식 시간이 긴 경우 50분마다 일어나 5분간 스트레칭하기",
        ]
    elif age_group in middle:
        stage = "중장년기 (혈압·내장지방 집중 관리기)"
        diet = {
            "아침": "잡곡밥 1/2공기 + 저염 된장국(건더기 위주) + 달걀찜 + 나물무침",
            "점심": "보리밥 + 고등어구이(소금 간 최소화) + 쌈채소 + 다시마쌈",
            "저녁": "두부버섯전골(맑은 육수) + 브로콜리 숙회 + 구운 견과류 한 줌",
            "핵심 팁": "소금 대신 마늘, 양파, 레몬즙, 허브로 풍미를 내어 하루 나트륨 섭취량을 2,000mg 이하로 제한하세요.",
        }
        exercise = [
            "**유산소 (주 4~5회, 40분):** 혈압 안정에 효과적인 중강도 속보, 수영, 등산(완만한 코스)",
            "**근력 (주 2회):** 가벼운 아령, 밴드 운동, 푸시업 (숨을 참지 않고 호흡을 내쉬며 실시)",
            "**주의사항:** 고혈압 전단계일 경우 무거운 역기를 순간적으로 드는 고중량 운동은 피하세요.",
        ]
    else:
        stage = "노년기 (근감소 예방 및 혈관 건강 유지기)"
        diet = {
            "아침": "부드러운 현미죽 + 연두부 간장양념(저염) + 삶은 달걀 1개",
            "점심": "잡곡밥 1/2공기 + 소고기 무국(국물 남기기) + 시금치나물 + 백김치",
            "저녁": "흰살생선 찜 + 애호박볶음 + 우유 또는 두유 1잔",
            "핵심 팁": "싱겁게 먹되 단백질 섭취가 부족해지지 않도록 매 끼니 두부·생선·살코기 중 1가지를 꼭 포함하세요.",
        }
        exercise = [
            "**유산소 (매일 30분):** 평지 걷기, 아쿠아로빅 등 관절 부담이 적은 유산소 운동",
            "**하체·균형 (주 3회):** 의자 잡고 스쿼트, 뒤꿈치 들기, 한 발 서기로 낙상 및 근감소 예방",
            "**주의사항:** 기온 차가 큰 새벽 운동을 피하고, 운동 전후 충분한 준비운동과 수분 섭취를 하세요.",
        ]

    if job_type == "근로자":
        job_tip = "💼 **근로자 맞춤 팁:** 회식 및 외식 시 국물·소스류를 덜어내고, 점심 식사 후 15분 산책을 루틴화하세요."
    elif job_type == "공무원":
        job_tip = "🏛️ **공무원 맞춤 팁:** 장시간 사무 업무로 인한 복부비만 예방을 위해 계단 이용과 스탠딩 데스크 활용을 권장합니다."
    else:
        job_tip = "🏡 **지역가입자 맞춤 팁:** 불규칙한 식사 시간을 일정하게 고정하고, 보건소 무료 혈압·체성분 측정을 정기적으로 활용하세요."

    return stage, diet, exercise, job_tip

# ---------------- UI 레이아웃 ----------------
st.title("🩺 AI 생애주기 맞춤 헬스케어 코치")
st.markdown("국민건강검진 학습 모델(`health_coach_model.pkcls`)을 기반으로 **비만·혈압 관리 필요 확률**을 실시간으로 분석합니다.")
st.divider()

# 사이드바 사용자 입력
with st.sidebar:
    st.header("📋 검진자 정보 입력")
    job_options = ["근로자", "공무원", "지역"]
    age_options = [
        "19세이하", "20~24세", "25~29세", "30~34세", "35~39세",
        "40~44세", "45~49세", "50~54세", "55~59세", "60~64세",
        "65~69세", "70~74세", "75~79세", "80~84세", "85세이상",
    ]
    gender_options = ["남성", "여성"]

    selected_job = st.selectbox("1. 직역 구분", job_options, index=0)
    selected_age = st.selectbox("2. 연령대", age_options, index=5)
    selected_gender = st.radio("3. 성별", gender_options, horizontal=True)

    st.info("💡 선택 값을 변경하면 AI 모델이 실시간으로 추론 결과를 업데이트합니다.")

# Orange3 모델 입력용 Table 생성 (수검인원 100명 기준 정규화)
feature_domain = Domain(model.domain.attributes)
orange_table = Table.from_numpy(
    feature_domain,
    X=np.array(
        [
            [
                feature_domain["직역"].to_val(selected_job),
                feature_domain["연령대"].to_val(selected_age),
                feature_domain["성별"].to_val(selected_gender),
                100.0,
            ]
        ]
    ),
)

# 실시간 추론 및 확률(%) 보정 (0~100% 범위 클리핑)
raw_pred = float(model(orange_table)[0])
risk_prob = float(np.clip(raw_pred, 0.0, 100.0))

# 결과 시각화 및 맞춤 가이드 출력
col1, col2 = st.columns([1, 1.3], gap="large")

with col1:
    st.subheader("📊 실시간 비만·혈압 주의 판정")
    fig, status_label = create_donut_gauge(risk_prob)
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        f"선택 조건: **{selected_job}** · **{selected_age}** · **{selected_gender}** "
        f"(동일 조건 100명 중 약 **{risk_prob:.1f}명**이 비만·혈압 관리 대상에 해당)"
    )

with col2:
    stage_name, diet_plan, workout_list, job_advice = get_lifecycle_guide(
        selected_age, selected_job, selected_gender
    )
    st.subheader(f"🥗 {stage_name} 맞춤 코칭")
    st.success(job_advice)

    tab1, tab2 = st.tabs(["🍱 저염식 추천 식단표", "🏃 맞춤 운동 가이드"])

    with tab1:
        diet_df = pd.DataFrame(
            [
                {"끼니": "아침", "추천 메뉴": diet_plan["아침"]},
                {"끼니": "점심", "추천 메뉴": diet_plan["점심"]},
                {"끼니": "저녁", "추천 메뉴": diet_plan["저녁"]},
            ]
        )
        st.table(diet_df)
        st.info(f"🧂 **저염 식습관 핵심 팁:** {diet_plan['핵심 팁']}")

    with tab2:
        for item in workout_list:
            st.markdown(f"- {item}")
