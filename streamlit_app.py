import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard WFH Burnout", layout="wide")

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

# ==========================================
# BARRA LATERAL (WIDGETS)
# ==========================================
st.sidebar.header("Filtros Interativos")

# Widget 1: Multiselect para o Tipo de Dia
dias_unicos = df['day_type'].unique().tolist()
filtro_dia = st.sidebar.multiselect(
    "1. Selecione o Tipo de Dia:",
    options=dias_unicos,
    default=dias_unicos
)

# Widget 2: Slider para Horas Trabalhadas
min_horas = float(df['work_hours'].min())
max_horas = float(df['work_hours'].max())
filtro_horas = st.sidebar.slider(
    "2. Filtre por Horas Trabalhadas:",
    min_value=min_horas,
    max_value=max_horas,
    value=(min_horas, max_horas) 
)

# Aplicando os filtros
df_filtrado = df[
    (df['day_type'].isin(filtro_dia)) & 
    (df['work_hours'] >= filtro_horas[0]) & 
    (df['work_hours'] <= filtro_horas[1])
]

# ==========================================
# MÉTRICAS PRINCIPAIS
# ==========================================
col1, col2, col3 = st.columns(3)
col1.metric("Registros Filtrados", len(df_filtrado))
if len(df_filtrado) > 0:
    col2.metric("Média de Horas de Sono", f"{df_filtrado['sleep_hours'].mean():.1f}h")
    col3.metric("Média de Fadiga", f"{df_filtrado['fatigue_score'].mean():.1f}/10")

st.write("---")

# ==========================================
# GRÁFICOS INTERATIVOS
# ==========================================
if len(df_filtrado) > 0:
    # --- PRIMEIRA LINHA DE GRÁFICOS ---
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
            labels={"work_hours": "Horas", "burnout_score": "Score", "burnout_risk": "Risco"}
        )
        # APENAS O GRÁFICO (Sem parâmetros adicionais de largura para evitar avisos)
        st.plotly_chart(fig1)

    with col_grafico2:
        st.subheader("Média de Burnout por Tipo de Dia")
        df_agrupado = df_filtrado.groupby('day_type')['burnout_score'].mean().reset_index()
        fig2 = px.bar(
            df_agrupado, 
            x="day_type", 
            y="burnout_score", 
            color="day_type",
            text_auto='.2f',
            labels={"day_type": "Dia", "burnout_score": "Média Score"}
        )
        # APENAS O GRÁFICO
        st.plotly_chart(fig2)

    st.write("---")
    
    # --- SEGUNDA LINHA DE GRÁFICOS ---
    col_grafico3, col_grafico4 = st.columns(2)
    
    with col_grafico3:
        st.subheader("Proporção de Risco de Burnout")
        fig3 = px.pie(
            df_filtrado, 
            names="burnout_risk", 
            hole=0.4, 
            color="burnout_risk",
            color_discrete_map={"Low": "#00CC96", "Medium": "#FFA15A", "High": "#EF553B"}
        )
        fig3.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        # APENAS O GRÁFICO
        st.plotly_chart(fig3)
        
    with col_grafico4:
        st.subheader("Distribuição de Fadiga por Risco")
        fig4 = px.box(
            df_filtrado, 
            x="burnout_risk", 
            y="fatigue_score", 
            color="burnout_risk",
            color_discrete_map={"Low": "#00CC96", "Medium": "#FFA15A", "High": "#EF553B"},
            labels={"burnout_risk": "Nível de Risco", "fatigue_score": "Score de Fadiga"}
        )
        fig4.update_layout(showlegend=False) 
        # APENAS O GRÁFICO
        st.plotly_chart(fig4)

else:
    st.warning("Nenhum dado encontrado para os filtros selecionados. Por favor, ajuste os filtros na barra lateral.")

st.write("---")

# ==========================================
# TABELA DE DADOS
# ==========================================
st.subheader("Base de Dados Completa (Filtrada)")
# NA TABELA usamos o width="stretch" (novo padrão que o Streamlit pede)
st.dataframe(df_filtrado, width="stretch")