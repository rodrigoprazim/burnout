import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard WFH Burnout", layout="wide")

# ==========================================
# REQUISITO: 01 Figura (Imagem fixa)
# ==========================================
st.image(
    "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=1200&q=80",
    caption="Análise de Fatores no Home Office",
    use_container_width=True
)

st.title("📊 Dashboard: Fatores de Burnout no Home Office")
st.write("---")

@st.cache_data
def load_data():
    df = pd.read_csv("wfh_burnout_dataset.csv")
    return df

df = load_data()

st.sidebar.header("Filtros Interativos")

# ==========================================
# REQUISITO: 02 Widgets (Componentes de entrada)
# ==========================================

dias_unicos = df['day_type'].unique().tolist()
filtro_dia = st.sidebar.multiselect(
    "1. Selecione o Tipo de Dia:",
    options=dias_unicos,
    default=dias_unicos
)

min_horas = float(df['work_hours'].min())
max_horas = float(df['work_hours'].max())
filtro_horas = st.sidebar.slider(
    "2. Filtre por Horas Trabalhadas:",
    min_value=min_horas,
    max_value=max_horas,
    value=(min_horas, max_horas) 
)

df_filtrado = df[
    (df['day_type'].isin(filtro_dia)) & 
    (df['work_hours'] >= filtro_horas[0]) & 
    (df['work_hours'] <= filtro_horas[1])
]

col1, col2, col3 = st.columns(3)
col1.metric("Registros Filtrados", len(df_filtrado))
if len(df_filtrado) > 0:
    col2.metric("Média de Horas de Sono", f"{df_filtrado['sleep_hours'].mean():.1f}h")
    col3.metric("Média de Fadiga", f"{df_filtrado['fatigue_score'].mean():.1f}/10")

st.write("---")

# ==========================================
# REQUISITO: 02 Gráficos Interativos (Plotly)
# ==========================================

if len(df_filtrado) > 0:
    col_grafico1, col_grafico2 = st.columns(2)

    with col_grafico1:
        st.subheader("Relação: Horas de Trabalho vs Burnout")
        fig1 = px.scatter(
            df_filtrado, 
            x="work_hours", 
            y="burnout_score", 
            color="burnout_risk",
            hover_data=["fatigue_score", "meetings_count"],
            color_discrete_map={"Low": "#00CC96", "Medium": "#FFA15A", "High": "#EF553B"},
            labels={"work_hours": "Horas Trabalhadas", "burnout_score": "Score de Burnout", "burnout_risk": "Risco"}
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_grafico2:
        st.subheader("Média de Burnout por Tipo de Dia")
        df_agrupado = df_filtrado.groupby('day_type')['burnout_score'].mean().reset_index()
        fig2 = px.bar(
            df_agrupado, 
            x="day_type", 
            y="burnout_score", 
            color="day_type",
            text_auto='.2f',
            labels={"day_type": "Tipo de Dia", "burnout_score": "Média do Score de Burnout"}
        )
        st.plotly_chart(fig2, use_container_width=True)

else:
    st.warning("Nenhum dado encontrado para os filtros selecionados. Por favor, ajuste os filtros na barra lateral.")

st.write("---")
st.subheader("Base de Dados Completa (Filtrada)")
st.dataframe(df_filtrado, use_container_width=True)