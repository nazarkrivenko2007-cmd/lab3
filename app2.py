from datetime import date
import random

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Аналіз кінотеатру",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def create_cinema_data() -> pd.DataFrame:
    """Створює демонстраційні дані про відвідуваність кінотеатрів."""
    rng = random.Random(42)
    cinemas = ["Cinema City", "Movie Park", "Star Hall"]
    genres = ["Комедія", "Пригоди", "Фантастика", "Драма", "Анімація"]
    base_price = {
        "Комедія": 180,
        "Пригоди": 210,
        "Фантастика": 230,
        "Драма": 170,
        "Анімація": 160,
    }
    rows = []

    for day in pd.date_range(end=date.today(), periods=180):
        weekend_bonus = 45 if day.dayofweek >= 5 else 0
        for cinema in cinemas:
            cinema_bonus = cinemas.index(cinema) * 14
            for genre in genres:
                visitors = rng.randint(35, 145) + weekend_bonus + cinema_bonus
                sessions = rng.randint(2, 6)
                price = base_price[genre]
                rows.append(
                    {
                        "Дата": day,
                        "Кінотеатр": cinema,
                        "Жанр": genre,
                        "Відвідувачі": visitors,
                        "Сеанси": sessions,
                        "Дохід, грн": visitors * price,
                    }
                )

    return pd.DataFrame(rows)


def hryvnias(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ") + " грн"


data = create_cinema_data()

st.markdown(
    """
    <style>
        .stApp { background: #11100f; color: #f6f4ef; }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] { background: #1d1b18; }
        [data-testid="stSidebar"] * { color: #f6f4ef; }
        .block-container { padding-top: 3rem; padding-bottom: 3rem; }
        h1, h2, h3, p, label { color: #f6f4ef !important; }
        h1 { font-weight: 800 !important; letter-spacing: -0.04em; }
        [data-testid="stMetric"] {
            background: #25231f;
            border: 1px solid #4b4840;
            border-radius: 0.75rem;
            padding: 1rem;
        }
        [data-testid="stMetricLabel"] p,
        [data-testid="stMetricValue"] { color: #f6f4ef !important; }
        [data-baseweb="select"] > div,
        [data-testid="stDateInput"] input {
            background: #2a2824 !important;
            border-color: #4b4840 !important;
            color: #f6f4ef !important;
        }
        .stDownloadButton > button {
            background: #d44c5b;
            border: 0;
            color: white;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Аналіз відвідуваності кінотеатрів 🎬")
st.write("Інтерактивний дашборд із демонстраційними даними за останні 180 днів.")

with st.sidebar:
    st.header("Фільтри")
    selected_cinemas = st.multiselect(
        "Кінотеатри",
        options=sorted(data["Кінотеатр"].unique()),
        default=sorted(data["Кінотеатр"].unique()),
    )
    selected_genres = st.multiselect(
        "Жанри",
        options=sorted(data["Жанр"].unique()),
        default=sorted(data["Жанр"].unique()),
    )
    dates = st.date_input(
        "Період",
        value=(data["Дата"].min().date(), data["Дата"].max().date()),
        min_value=data["Дата"].min().date(),
        max_value=data["Дата"].max().date(),
    )

if len(dates) != 2:
    st.info("Оберіть початкову та кінцеву дату для перегляду статистики.")
    st.stop()

filtered = data[
    data["Кінотеатр"].isin(selected_cinemas)
    & data["Жанр"].isin(selected_genres)
    & data["Дата"].between(pd.Timestamp(dates[0]), pd.Timestamp(dates[1]))
].copy()

if filtered.empty:
    st.warning("За вибраними фільтрами даних немає. Змініть параметри ліворуч.")
    st.stop()

total_visitors = filtered["Відвідувачі"].sum()
total_revenue = filtered["Дохід, грн"].sum()
total_sessions = filtered["Сеанси"].sum()
top_genre = filtered.groupby("Жанр")["Відвідувачі"].sum().idxmax()

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Відвідувачі", f"{total_visitors:,}".replace(",", " "))
metric_2.metric("Дохід", hryvnias(total_revenue))
metric_3.metric("Сеанси", f"{total_sessions:,}".replace(",", " "))
metric_4.metric("Популярний жанр", top_genre)

daily_visitors = filtered.groupby("Дата", as_index=False)["Відвідувачі"].sum()
genre_summary = (
    filtered.groupby("Жанр", as_index=False)[["Відвідувачі", "Дохід, грн"]].sum().sort_values("Відвідувачі")
)
cinema_revenue = filtered.groupby("Кінотеатр", as_index=False)["Дохід, грн"].sum()

left, right = st.columns((1.55, 1))
with left:
    st.subheader("Відвідуваність за днями")
    daily_chart = px.line(
        daily_visitors,
        x="Дата",
        y="Відвідувачі",
        template="plotly_dark",
        color_discrete_sequence=["#e95a6a"],
    )
    daily_chart.update_layout(
        height=330,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="#11100f",
        plot_bgcolor="#11100f",
    )
    st.plotly_chart(daily_chart, use_container_width=True)

with right:
    st.subheader("Дохід за кінотеатрами")
    cinema_chart = px.pie(
        cinema_revenue,
        names="Кінотеатр",
        values="Дохід, грн",
        hole=0.58,
        template="plotly_dark",
        color_discrete_sequence=["#e95a6a", "#f0b86b", "#76a5df"],
    )
    cinema_chart.update_layout(
        height=330,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="#11100f",
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(cinema_chart, use_container_width=True)

st.subheader("Популярність жанрів")
genre_chart = px.bar(
    genre_summary,
    x="Відвідувачі",
    y="Жанр",
    orientation="h",
    text="Відвідувачі",
    template="plotly_dark",
    color="Відвідувачі",
    color_continuous_scale=["#7b2630", "#e95a6a", "#f0b86b"],
)
genre_chart.update_layout(
    height=310,
    margin=dict(l=0, r=0, t=10, b=0),
    paper_bgcolor="#11100f",
    plot_bgcolor="#11100f",
    coloraxis_showscale=False,
)
st.plotly_chart(genre_chart, use_container_width=True)

with st.expander("Переглянути дані"):
    st.dataframe(
        filtered.sort_values("Дата", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Завантажити відфільтровані дані у CSV",
        data=filtered.to_csv(index=False).encode("utf-8-sig"),
        file_name="відвідуваність_кінотеатрів.csv",
        mime="text/csv",
    )
