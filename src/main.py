import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import psycopg2
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"

st.set_page_config(
    page_title="PharmaSense AI - Otimização Logística",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚚 Otimização Logística e Distribuição - PharmaSense AI")
st.markdown(
    "Dashboard de monitoramento e análise de eficiência da cadeia de suprimentos farmacêutica."
)


def get_db_connection():
    """Obtém conexão com o banco de dados PostgreSQL"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        st.error("Variável de ambiente DATABASE_URL não configurada.")
        st.info(
            "Configure a variável DATABASE_URL no arquivo .env ou nas variáveis de ambiente."
        )
        return None

    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None


def load_logistica_csv():
    """Carrega dados de logA-stica a partir do CSV local"""
    csv_path = ASSETS_DIR / "logistica_simulada.csv"
    if not csv_path.exists():
        st.error("Arquivo logistica_simulada.csv nA�o encontrado na pasta assets.")
        return pd.DataFrame()

    try:
        df = pd.read_csv(csv_path)
        df["Data"] = pd.to_datetime(df["Data"])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados de logA-stica do CSV: {e}")
        return pd.DataFrame()


def load_estoque_csv():
    """Carrega dados de estoque e demanda a partir do CSV local"""
    csv_path = ASSETS_DIR / "demanda_estoque.csv"
    if not csv_path.exists():
        st.error("Arquivo demanda_estoque.csv nA�o encontrado na pasta assets.")
        return pd.DataFrame()

    try:
        df = pd.read_csv(csv_path)
        df["Data"] = pd.to_datetime(df["Data"])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados de estoque do CSV: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=60)
def load_data():
    """Carrega dados de logística do banco de dados"""
    conn = get_db_connection()
    if conn is None:
        st.info("Usando dados do CSV local para logA-stica.")
        return load_logistica_csv()

    try:
        query = """
            SELECT 
                data,
                estado,
                regiao,
                rota_id,
                tempo_resposta_previsto,
                tempo_resposta_real,
                status,
                custo_logistico_usd,
                emissao_co2_kg
            FROM logistica
            WHERE status != 'Em Rota'
            ORDER BY data DESC
        """
        df = pd.read_sql_query(query, conn)

        column_mapping = {
            "data": "Data",
            "estado": "Estado",
            "regiao": "Regiao",
            "rota_id": "Rota_ID",
            "tempo_resposta_previsto": "Tempo_Resposta_Previsto",
            "tempo_resposta_real": "Tempo_Resposta_Real",
            "status": "Status",
            "custo_logistico_usd": "Custo_Logistico_USD",
            "emissao_co2_kg": "Emissao_CO2_kg",
        }
        df = df.rename(columns=column_mapping)
        df["Data"] = pd.to_datetime(df["Data"])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados de logística: {e}")
        st.info("Usando dados do CSV local para logA-stica.")
        return load_logistica_csv()
    finally:
        conn.close()


@st.cache_data(ttl=60)
def load_estoque_data():
    """Carrega dados de estoque e demanda do banco de dados"""
    conn = get_db_connection()
    if conn is None:
        st.info("Usando dados do CSV local para estoque e demanda.")
        return load_estoque_csv()

    try:
        query = """
            SELECT 
                data,
                estado,
                regiao,
                demanda_diaria,
                entregas_concluidas,
                entregas_atrasadas,
                custo_total_usd,
                custo_medio_usd,
                emissao_total_co2_kg,
                emissao_media_co2_kg,
                tempo_medio_entrega_dias,
                tempo_previsto_medio_dias,
                estoque_inicial,
                estoque_disponivel,
                estoque_final,
                reabastecimento,
                reabastecimento_chegando,
                stock_out,
                demanda_atendida,
                demanda_nao_atendida,
                taxa_atendimento,
                nivel_servico,
                dias_estoque_restante,
                ponto_reposicao,
                indicador_estoque_baixo,
                indicador_stock_out,
                demanda_acumulada,
                stock_out_acumulado,
                custo_total_acumulado
            FROM demanda_estoque
            ORDER BY data DESC
        """
        df_estoque = pd.read_sql_query(query, conn)

        column_mapping = {
            "data": "Data",
            "estado": "Estado",
            "regiao": "Regiao",
            "demanda_diaria": "Demanda_Diaria",
            "entregas_concluidas": "Entregas_Concluidas",
            "entregas_atrasadas": "Entregas_Atrasadas",
            "custo_total_usd": "Custo_Total_USD",
            "custo_medio_usd": "Custo_Medio_USD",
            "emissao_total_co2_kg": "Emissao_Total_CO2_kg",
            "emissao_media_co2_kg": "Emissao_Media_CO2_kg",
            "tempo_medio_entrega_dias": "Tempo_Medio_Entrega_Dias",
            "tempo_previsto_medio_dias": "Tempo_Previsto_Medio_Dias",
            "estoque_inicial": "Estoque_Inicial",
            "estoque_disponivel": "Estoque_Disponivel",
            "estoque_final": "Estoque_Final",
            "reabastecimento": "Reabastecimento",
            "reabastecimento_chegando": "Reabastecimento_Chegando",
            "stock_out": "Stock_Out",
            "demanda_atendida": "Demanda_Atendida",
            "demanda_nao_atendida": "Demanda_Nao_Atendida",
            "taxa_atendimento": "Taxa_Atendimento",
            "nivel_servico": "Nivel_Servico",
            "dias_estoque_restante": "Dias_Estoque_Restante",
            "ponto_reposicao": "Ponto_Reposicao",
            "indicador_estoque_baixo": "Indicador_Estoque_Baixo",
            "indicador_stock_out": "Indicador_Stock_Out",
            "demanda_acumulada": "Demanda_Acumulada",
            "stock_out_acumulado": "Stock_Out_Acumulado",
            "custo_total_acumulado": "Custo_Total_Acumulado",
        }
        df_estoque = df_estoque.rename(columns=column_mapping)
        df_estoque["Data"] = pd.to_datetime(df_estoque["Data"])
        return df_estoque
    except Exception as e:
        st.error(f"Erro ao carregar dados de estoque: {e}")
        st.info("Usando dados do CSV local para estoque e demanda.")
        return load_estoque_csv()
    finally:
        conn.close()


df = load_data()
df_estoque = load_estoque_data()

if df.empty:
    st.stop()

tab1, tab2 = st.tabs(["📦 Logística", "📊 Estoque e Demanda"])

st.sidebar.header("Filtros de Análise")

data_min = df["Data"].min().date()
data_max = df["Data"].max().date()

data_selecionada = st.sidebar.date_input(
    "Selecione o Período", [data_min, data_max], min_value=data_min, max_value=data_max
)

if len(data_selecionada) == 2:
    start_date = pd.to_datetime(data_selecionada[0])
    end_date = pd.to_datetime(data_selecionada[1])
    df_filtered = df[(df["Data"] >= start_date) & (df["Data"] <= end_date)]
    if not df_estoque.empty:
        df_estoque_filtered = df_estoque[
            (df_estoque["Data"] >= start_date) & (df_estoque["Data"] <= end_date)
        ]
    else:
        df_estoque_filtered = df_estoque.copy()
else:
    df_filtered = df.copy()
    df_estoque_filtered = df_estoque.copy()

regioes_unicas = ["Todas"] + sorted(df["Regiao"].unique().tolist())
regiao_selecionada = st.sidebar.multiselect(
    "Filtrar por Região", regioes_unicas, default=["Todas"]
)

if "Todas" not in regiao_selecionada:
    df_filtered = df_filtered[df_filtered["Regiao"].isin(regiao_selecionada)]
    if not df_estoque_filtered.empty:
        df_estoque_filtered = df_estoque_filtered[
            df_estoque_filtered["Regiao"].isin(regiao_selecionada)
        ]

if "Estado" in df.columns:
    estados_unicos = ["Todos"] + sorted(df_filtered["Estado"].unique().tolist())
    estado_selecionado = st.sidebar.multiselect(
        "Filtrar por Estado", estados_unicos, default=["Todos"]
    )

    if "Todos" not in estado_selecionado:
        df_filtered = df_filtered[df_filtered["Estado"].isin(estado_selecionado)]
        if not df_estoque_filtered.empty:
            df_estoque_filtered = df_estoque_filtered[
                df_estoque_filtered["Estado"].isin(estado_selecionado)
            ]

with tab1:
    st.header("📦 Métricas de Impacto e Desempenho Logístico")

    tempo_medio_real = df_filtered["Tempo_Resposta_Real"].mean()
    tempo_medio_previsto = df_filtered["Tempo_Resposta_Previsto"].mean()
    reducao_tempo = (
        (1 - (tempo_medio_real / tempo_medio_previsto)) * 100
        if tempo_medio_previsto > 0
        else 0
    )
    custo_total = df_filtered["Custo_Logistico_USD"].sum()
    emissao_media = df_filtered["Emissao_CO2_kg"].mean()
    taxa_atraso = (
        (df_filtered["Status"] == "Atrasado").sum() / len(df_filtered) * 100
        if len(df_filtered) > 0
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Redução no Tempo de Resposta (Eficiência)",
            value=f"{reducao_tempo:.1f}%",
            delta="Meta: 25%",
            delta_color="normal",
        )

    with col2:
        st.metric(
            label="Tempo Médio de Entrega Real",
            value=f"{tempo_medio_real:.1f} dias",
            delta=f"-{tempo_medio_previsto:.1f} dias (Baseline)",
            delta_color="inverse",
        )

    with col3:
        st.metric(
            label="Taxa de Atraso (Ruptura)",
            value=f"{taxa_atraso:.1f}%",
            delta="-5.0% (Simulado)",
            delta_color="inverse",
        )

    with col4:
        st.metric(
            label="Pegada de Carbono Média (Sustentabilidade)",
            value=f"{emissao_media:.1f} kg CO2",
            delta="Redução de 20% (Simulada)",
            delta_color="inverse",
        )

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Tendência de Eficiência: Tempo Real vs. Previsto")
        df_trend = (
            df_filtered.groupby("Data")[
                ["Tempo_Resposta_Previsto", "Tempo_Resposta_Real"]
            ]
            .mean()
            .reset_index()
        )

        fig_trend = px.line(
            df_trend,
            x="Data",
            y=["Tempo_Resposta_Previsto", "Tempo_Resposta_Real"],
            labels={"value": "Tempo Médio (dias)", "variable": "Métrica"},
            title="Comparação de Tempo de Resposta ao Longo do Tempo",
        )
        fig_trend.update_layout(legend_title_text="Tempo de Resposta")
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_chart2:
        st.subheader("Desempenho da Distribuição por Região")
        df_region = (
            df_filtered.groupby(["Regiao", "Status"])
            .size()
            .reset_index(name="Contagem")
        )
        df_region_total = df_filtered.groupby("Regiao").size().reset_index(name="Total")
        df_region = pd.merge(df_region, df_region_total, on="Regiao")
        df_region["Taxa_Atraso"] = np.where(
            df_region["Status"] == "Atrasado",
            (df_region["Contagem"] / df_region["Total"]) * 100,
            0,
        )

        fig_region = px.bar(
            df_region.sort_values("Taxa_Atraso", ascending=False),
            x="Regiao",
            y="Taxa_Atraso",
            color="Regiao",
            labels={"Taxa_Atraso": "Taxa de Atraso (%)", "Regiao": "Região"},
            title="Taxa de Atraso por Região",
        )
        st.plotly_chart(fig_region, use_container_width=True)

    st.markdown("---")

    st.subheader("Monitoramento de Rotas")
    st.caption("Visualização das rotas com alertas de condições")

    df_latest = df_filtered.sort_values("Data", ascending=False).head(20)

    def highlight_status(s):
        if s.Status == "Atrasado":
            return ["background-color: #ff6b6b; color: #000000"] * len(s)
        else:
            return [""] * len(s)

    column_order = [
        "Rota_ID",
        "Data",
    ]
    if "Estado" in df_latest.columns:
        column_order.append("Estado")
    column_order.extend(
        [
            "Regiao",
            "Status",
            "Tempo_Resposta_Real",
            "Custo_Logistico_USD",
            "Emissao_CO2_kg",
        ]
    )

    st.dataframe(
        df_latest.style.apply(highlight_status, axis=1),
        use_container_width=True,
        column_order=column_order,
    )

    if "Estado" in df_filtered.columns:
        st.markdown("---")
        st.subheader("🗺️ Desempenho por Estado")

        col_estado1, col_estado2 = st.columns(2)

        with col_estado1:
            df_estado_tempo = (
                df_filtered.groupby("Estado")["Tempo_Resposta_Real"]
                .mean()
                .reset_index()
                .sort_values("Tempo_Resposta_Real")
                .head(10)
            )
            df_estado_tempo.columns = ["Estado", "Tempo Médio (dias)"]

            fig_estado_rapido = px.bar(
                df_estado_tempo,
                x="Tempo Médio (dias)",
                y="Estado",
                orientation="h",
                title="Top 10 Estados - Menor Tempo de Entrega",
                color="Tempo Médio (dias)",
                color_continuous_scale="Greens_r",
            )
            st.plotly_chart(fig_estado_rapido, use_container_width=True)

        with col_estado2:
            df_estado_tempo_lento = (
                df_filtered.groupby("Estado")["Tempo_Resposta_Real"]
                .mean()
                .reset_index()
                .sort_values("Tempo_Resposta_Real", ascending=False)
                .head(10)
            )
            df_estado_tempo_lento.columns = ["Estado", "Tempo Médio (dias)"]

            fig_estado_lento = px.bar(
                df_estado_tempo_lento,
                x="Tempo Médio (dias)",
                y="Estado",
                orientation="h",
                title="Top 10 Estados - Maior Tempo de Entrega",
                color="Tempo Médio (dias)",
                color_continuous_scale="Reds",
            )
            st.plotly_chart(fig_estado_lento, use_container_width=True)

    st.subheader("💰 Análise de Otimização de Custo e Sustentabilidade")

    df_summary = (
        df_filtered.groupby("Regiao")
        .agg(
            Custo_Medio_USD=("Custo_Logistico_USD", "mean"),
            Emissao_Media_CO2=("Emissao_CO2_kg", "mean"),
        )
        .reset_index()
        .sort_values("Custo_Medio_USD", ascending=False)
    )

    fig_cost_emission = px.scatter(
        df_summary,
        x="Custo_Medio_USD",
        y="Emissao_Media_CO2",
        color="Regiao",
        size="Emissao_Media_CO2",
        hover_name="Regiao",
        title="Relação Custo vs. Emissão de Carbono por Região",
        labels={
            "Custo_Medio_USD": "Custo Médio Logístico (USD)",
            "Emissao_Media_CO2": "Emissão Média de CO2 (kg)",
        },
    )
    st.plotly_chart(fig_cost_emission, use_container_width=True)

    st.markdown("---")

    st.subheader("📊 Análise de Correlações")
    st.markdown("Matriz de correlação entre variáveis de logística")

    vars_correlacao = ["Tempo_Resposta_Real", "Custo_Logistico_USD", "Emissao_CO2_kg"]
    df_corr = df_filtered[vars_correlacao].corr()

    fig_corr = px.imshow(
        df_corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu",
        title="Matriz de Correlação - Variáveis de Logística",
        labels=dict(color="Correlação"),
    )
    fig_corr.update_layout(height=500)
    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("---")

    st.subheader("📈 Análise Temporal Mensal")
    st.markdown("Tendências mensais de desempenho logístico")

    df_filtered["Ano_Mes"] = df_filtered["Data"].dt.to_period("M").astype(str)
    df_mensal = (
        df_filtered.groupby("Ano_Mes")
        .agg(
            {
                "Tempo_Resposta_Real": "mean",
                "Custo_Logistico_USD": "mean",
                "Emissao_CO2_kg": "mean",
                "Status": lambda x: (x == "Atrasado").sum() / len(x) * 100,
            }
        )
        .reset_index()
    )
    df_mensal.columns = [
        "Ano_Mes",
        "Tempo_Medio",
        "Custo_Medio",
        "Emissao_Media",
        "Taxa_Atraso",
    ]

    col_temp1, col_temp2 = st.columns(2)

    with col_temp1:
        fig_tempo_mensal = px.line(
            df_mensal,
            x="Ano_Mes",
            y="Tempo_Medio",
            markers=True,
            title="Tempo Médio de Entrega Mensal",
            labels={"Tempo_Medio": "Tempo (dias)", "Ano_Mes": "Mês"},
        )
        fig_tempo_mensal.update_xaxes(tickangle=45)
        st.plotly_chart(fig_tempo_mensal, use_container_width=True)

    with col_temp2:
        fig_custo_mensal = px.line(
            df_mensal,
            x="Ano_Mes",
            y="Custo_Medio",
            markers=True,
            title="Custo Médio Mensal (USD)",
            labels={"Custo_Medio": "Custo (USD)", "Ano_Mes": "Mês"},
        )
        fig_custo_mensal.update_xaxes(tickangle=45)
        st.plotly_chart(fig_custo_mensal, use_container_width=True)

    st.markdown("---")

    st.subheader("🏆 Rankings e Comparações")

    col_rank1, col_rank2 = st.columns(2)

    with col_rank1:
        st.markdown("**Top 10 Estados - Maior Custo Total**")
        df_custo_estado = (
            df_filtered.groupby("Estado")["Custo_Logistico_USD"]
            .sum()
            .reset_index()
            .sort_values("Custo_Logistico_USD", ascending=False)
            .head(10)
        )
        df_custo_estado.columns = ["Estado", "Custo Total (USD)"]

        fig_custo_estado = px.bar(
            df_custo_estado,
            x="Custo Total (USD)",
            y="Estado",
            orientation="h",
            title="Top 10 Estados - Maior Custo Logístico",
            color="Custo Total (USD)",
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig_custo_estado, use_container_width=True)

    with col_rank2:
        st.markdown("**Top 10 Estados - Maior Emissão de CO2**")
        df_emissao_estado = (
            df_filtered.groupby("Estado")["Emissao_CO2_kg"]
            .sum()
            .reset_index()
            .sort_values("Emissao_CO2_kg", ascending=False)
            .head(10)
        )
        df_emissao_estado.columns = ["Estado", "Emissão Total (kg CO2)"]

        fig_emissao_estado = px.bar(
            df_emissao_estado,
            x="Emissão Total (kg CO2)",
            y="Estado",
            orientation="h",
            title="Top 10 Estados - Maior Emissão de CO2",
            color="Emissão Total (kg CO2)",
            color_continuous_scale="Oranges",
        )
        st.plotly_chart(fig_emissao_estado, use_container_width=True)

with tab2:
    if df_estoque_filtered.empty:
        st.warning(
            "⚠️ Dados de estoque não disponíveis. Execute primeiro o script gerar_demanda_estoque.py para gerar os dados."
        )
        st.stop()

    st.header("📊 Análise de Estoque e Demanda")
    st.markdown("Monitoramento de estoque, stock out e demanda não atendida")

    st.subheader("📊 Métricas Principais de Estoque")

    demanda_total = df_estoque_filtered["Demanda_Diaria"].sum()
    demanda_atendida = df_estoque_filtered["Demanda_Atendida"].sum()
    demanda_nao_atendida = df_estoque_filtered["Demanda_Nao_Atendida"].sum()
    stock_out_total = df_estoque_filtered["Stock_Out"].sum()
    estoque_final_medio = df_estoque_filtered["Estoque_Final"].mean()
    taxa_atendimento_media = df_estoque_filtered["Taxa_Atendimento"].mean()
    dias_stock_out = (df_estoque_filtered["Indicador_Stock_Out"] == 1).sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Taxa de Atendimento",
            value=f"{taxa_atendimento_media:.1f}%",
            delta="Meta: 95%",
            delta_color="normal" if taxa_atendimento_media >= 95 else "inverse",
        )

    with col2:
        st.metric(
            label="Stock Out Total",
            value=f"{stock_out_total:,.0f}",
            delta=f"{stock_out_total / demanda_total * 100:.1f}% da demanda",
            delta_color="inverse",
        )

    with col3:
        st.metric(
            label="Estoque Final Médio",
            value=f"{estoque_final_medio:.0f} unidades",
            delta=f"Dias com stock out: {dias_stock_out}",
            delta_color="inverse" if dias_stock_out > 0 else "normal",
        )

    with col4:
        st.metric(
            label="Demanda Não Atendida",
            value=f"{demanda_nao_atendida:,.0f}",
            delta=f"{demanda_nao_atendida / demanda_total * 100:.1f}%",
            delta_color="inverse",
        )

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Demanda vs Estoque ao Longo do Tempo")
        df_tendencia = (
            df_estoque_filtered.groupby("Data")
            .agg({"Demanda_Diaria": "sum", "Estoque_Final": "mean", "Stock_Out": "sum"})
            .reset_index()
        )

        fig_demanda_estoque = px.line(
            df_tendencia,
            x="Data",
            y=["Demanda_Diaria", "Estoque_Final"],
            labels={"value": "Quantidade", "variable": "Métrica"},
            title="Tendência de Demanda e Estoque",
        )
        fig_demanda_estoque.update_layout(legend_title_text="Métrica")
        st.plotly_chart(fig_demanda_estoque, use_container_width=True)

    with col_chart2:
        st.subheader("Stock Out por Região")
        df_stock_out_regiao = (
            df_estoque_filtered.groupby("Regiao")
            .agg({"Stock_Out": "sum", "Demanda_Diaria": "sum"})
            .reset_index()
        )
        df_stock_out_regiao["Percentual_Stock_Out"] = (
            df_stock_out_regiao["Stock_Out"]
            / df_stock_out_regiao["Demanda_Diaria"]
            * 100
        )

        fig_stock_out = px.bar(
            df_stock_out_regiao.sort_values("Stock_Out", ascending=False),
            x="Regiao",
            y="Stock_Out",
            color="Percentual_Stock_Out",
            color_continuous_scale="Reds",
            labels={"Stock_Out": "Stock Out Total", "Regiao": "Região"},
            title="Stock Out Total por Região",
        )
        st.plotly_chart(fig_stock_out, use_container_width=True)

    st.markdown("---")

    st.subheader("✅ Análise de Atendimento e Nível de Serviço")

    col_atend1, col_atend2 = st.columns(2)

    with col_atend1:
        st.subheader("Taxa de Atendimento por Região")
        df_atendimento = (
            df_estoque_filtered.groupby("Regiao")["Taxa_Atendimento"]
            .mean()
            .reset_index()
        )
        df_atendimento = df_atendimento.sort_values("Taxa_Atendimento", ascending=False)

        fig_atendimento = px.bar(
            df_atendimento,
            x="Regiao",
            y="Taxa_Atendimento",
            color="Taxa_Atendimento",
            color_continuous_scale="Greens",
            labels={"Taxa_Atendimento": "Taxa de Atendimento (%)", "Regiao": "Região"},
            title="Taxa Média de Atendimento por Região",
        )
        st.plotly_chart(fig_atendimento, use_container_width=True)

    with col_atend2:
        st.subheader("Top 10 Estados - Maior Stock Out")
        df_stock_out_estado = (
            df_estoque_filtered.groupby("Estado")["Stock_Out"].sum().reset_index()
        )
        df_stock_out_estado = df_stock_out_estado.sort_values(
            "Stock_Out", ascending=False
        ).head(10)

        fig_estado_stock = px.bar(
            df_stock_out_estado,
            x="Stock_Out",
            y="Estado",
            orientation="h",
            color="Stock_Out",
            color_continuous_scale="Reds",
            labels={"Stock_Out": "Stock Out Total"},
            title="Top 10 Estados com Maior Stock Out",
        )
        st.plotly_chart(fig_estado_stock, use_container_width=True)

    st.markdown("---")

    st.subheader("⚠️ Monitoramento de Estoque e Stock Out")
    st.caption("Registros com indicadores de estoque baixo e stock out")

    df_monitor = (
        df_estoque_filtered[
            (df_estoque_filtered["Indicador_Estoque_Baixo"] == 1)
            | (df_estoque_filtered["Indicador_Stock_Out"] == 1)
        ]
        .sort_values("Data", ascending=False)
        .head(30)
    )

    if not df_monitor.empty:

        def highlight_estoque(s):
            styles = [""] * len(s)
            if s.Indicador_Stock_Out == 1:
                styles = ["background-color: #ff6b6b; color: #000000"] * len(s)
            elif s.Indicador_Estoque_Baixo == 1:
                styles = ["background-color: #ffd93d; color: #000000"] * len(s)
            return styles

        colunas_monitor = [
            "Data",
            "Estado",
            "Regiao",
            "Demanda_Diaria",
            "Estoque_Disponivel",
            "Estoque_Final",
            "Stock_Out",
            "Demanda_Nao_Atendida",
            "Taxa_Atendimento",
            "Indicador_Estoque_Baixo",
            "Indicador_Stock_Out",
        ]

        st.dataframe(
            df_monitor[colunas_monitor].style.apply(highlight_estoque, axis=1),
            use_container_width=True,
        )
    else:
        st.info(
            "✅ Nenhum registro com estoque baixo ou stock out no período selecionado."
        )

    if "Estado" in df_estoque_filtered.columns:
        st.markdown("---")
        st.subheader("📋 Resumo por Estado")

        resumo_estados = (
            df_estoque_filtered.groupby("Estado")
            .agg(
                {
                    "Regiao": "first",
                    "Demanda_Diaria": "sum",
                    "Stock_Out": "sum",
                    "Taxa_Atendimento": "mean",
                    "Estoque_Final": "mean",
                    "Reabastecimento": "sum",
                }
            )
            .reset_index()
        )

        resumo_estados.columns = [
            "Estado",
            "Região",
            "Demanda Total",
            "Stock Out Total",
            "Taxa Atendimento Média (%)",
            "Estoque Final Médio",
            "Total Reabastecimentos",
        ]

        resumo_estados = resumo_estados.sort_values("Stock Out Total", ascending=False)
        st.dataframe(resumo_estados, use_container_width=True)

    st.markdown("---")

    st.subheader("📊 Análise de Correlações - Estoque e Demanda")
    st.markdown("Matriz de correlação entre variáveis de estoque e demanda")

    vars_correlacao_estoque = [
        "Demanda_Diaria",
        "Estoque_Final",
        "Stock_Out",
        "Taxa_Atendimento",
        "Custo_Total_USD",
        "Tempo_Medio_Entrega_Dias",
    ]

    vars_disponiveis = [
        v for v in vars_correlacao_estoque if v in df_estoque_filtered.columns
    ]
    df_corr_estoque = df_estoque_filtered[vars_disponiveis].corr()

    fig_corr_estoque = px.imshow(
        df_corr_estoque,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdYlGn",
        title="Matriz de Correlação - Variáveis de Estoque e Demanda",
        labels=dict(color="Correlação"),
    )
    fig_corr_estoque.update_layout(height=600)
    st.plotly_chart(fig_corr_estoque, use_container_width=True)

    st.markdown("---")

    st.subheader("📈 Análise Temporal Mensal - Estoque")
    st.markdown("Tendências mensais de demanda, estoque e stock out")

    df_estoque_filtered["Ano_Mes"] = (
        df_estoque_filtered["Data"].dt.to_period("M").astype(str)
    )
    df_mensal_estoque = (
        df_estoque_filtered.groupby("Ano_Mes")
        .agg(
            {
                "Demanda_Diaria": "sum",
                "Estoque_Final": "mean",
                "Stock_Out": "sum",
                "Taxa_Atendimento": "mean",
                "Reabastecimento": "sum",
            }
        )
        .reset_index()
    )

    col_temp_est1, col_temp_est2 = st.columns(2)

    with col_temp_est1:
        fig_demanda_mensal = go.Figure()
        fig_demanda_mensal.add_trace(
            go.Scatter(
                x=df_mensal_estoque["Ano_Mes"],
                y=df_mensal_estoque["Demanda_Diaria"],
                name="Demanda Total",
                line=dict(color="#00FFC6", width=2),
                mode="lines+markers",
            )
        )
        fig_demanda_mensal.add_trace(
            go.Scatter(
                x=df_mensal_estoque["Ano_Mes"],
                y=df_mensal_estoque["Estoque_Final"],
                name="Estoque Final Médio",
                line=dict(color="#1DE9B6", width=2),
                mode="lines+markers",
            )
        )
        fig_demanda_mensal.update_layout(
            title="Demanda e Estoque Mensal",
            xaxis_title="Mês",
            yaxis_title="Quantidade",
            hovermode="x unified",
            height=400,
        )
        fig_demanda_mensal.update_xaxes(tickangle=45)
        st.plotly_chart(fig_demanda_mensal, use_container_width=True)

    with col_temp_est2:
        fig_stock_mensal = go.Figure()
        fig_stock_mensal.add_trace(
            go.Scatter(
                x=df_mensal_estoque["Ano_Mes"],
                y=df_mensal_estoque["Stock_Out"],
                name="Stock Out Total",
                line=dict(color="#FF6B6B", width=2),
                mode="lines+markers",
                yaxis="y",
            )
        )
        fig_stock_mensal.add_trace(
            go.Scatter(
                x=df_mensal_estoque["Ano_Mes"],
                y=df_mensal_estoque["Taxa_Atendimento"],
                name="Taxa de Atendimento (%)",
                line=dict(color="#FFD93D", width=2),
                mode="lines+markers",
                yaxis="y2",
            )
        )
        fig_stock_mensal.update_layout(
            title="Stock Out e Taxa de Atendimento Mensal",
            xaxis_title="Mês",
            yaxis=dict(title="Stock Out Total", side="left"),
            yaxis2=dict(title="Taxa de Atendimento (%)", side="right", overlaying="y"),
            hovermode="x unified",
            height=400,
        )
        fig_stock_mensal.update_xaxes(tickangle=45)
        st.plotly_chart(fig_stock_mensal, use_container_width=True)

    st.markdown("---")

    st.subheader("🏆 Rankings de Estoque e Demanda")

    col_rank_est1, col_rank_est2 = st.columns(2)

    with col_rank_est1:
        st.markdown("**Top 10 Estados - Maior Demanda Total**")
        df_demanda_estado = (
            df_estoque_filtered.groupby("Estado")["Demanda_Diaria"]
            .sum()
            .reset_index()
            .sort_values("Demanda_Diaria", ascending=False)
            .head(10)
        )
        df_demanda_estado.columns = ["Estado", "Demanda Total"]

        fig_demanda_estado = px.bar(
            df_demanda_estado,
            x="Demanda Total",
            y="Estado",
            orientation="h",
            title="Top 10 Estados - Maior Demanda Total",
            color="Demanda Total",
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig_demanda_estado, use_container_width=True)

    with col_rank_est2:
        st.markdown("**Top 10 Estados - Melhor Taxa de Atendimento**")
        df_atendimento_estado = (
            df_estoque_filtered.groupby("Estado")["Taxa_Atendimento"]
            .mean()
            .reset_index()
            .sort_values("Taxa_Atendimento", ascending=False)
            .head(10)
        )
        df_atendimento_estado.columns = ["Estado", "Taxa de Atendimento (%)"]

        fig_atendimento_estado = px.bar(
            df_atendimento_estado,
            x="Taxa de Atendimento (%)",
            y="Estado",
            orientation="h",
            title="Top 10 Estados - Melhor Taxa de Atendimento",
            color="Taxa de Atendimento (%)",
            color_continuous_scale="Greens",
        )
        st.plotly_chart(fig_atendimento_estado, use_container_width=True)

    st.markdown("---")

    st.subheader("🔄 Análise de Reabastecimento")
    st.markdown("Análise de reabastecimentos por região e estado")

    col_reab1, col_reab2 = st.columns(2)

    with col_reab1:
        st.markdown("**Total de Reabastecimentos por Região**")
        df_reab_regiao = (
            df_estoque_filtered.groupby("Regiao")["Reabastecimento"]
            .sum()
            .reset_index()
            .sort_values("Reabastecimento", ascending=False)
        )

        fig_reab_regiao = px.bar(
            df_reab_regiao,
            x="Regiao",
            y="Reabastecimento",
            title="Total de Reabastecimentos por Região",
            color="Reabastecimento",
            color_continuous_scale="Viridis",
            labels={"Reabastecimento": "Total Reabastecimentos", "Regiao": "Região"},
        )
        st.plotly_chart(fig_reab_regiao, use_container_width=True)

    with col_reab2:
        st.markdown("**Top 10 Estados - Mais Reabastecimentos**")
        df_reab_estado = (
            df_estoque_filtered.groupby("Estado")["Reabastecimento"]
            .sum()
            .reset_index()
            .sort_values("Reabastecimento", ascending=False)
            .head(10)
        )
        df_reab_estado.columns = ["Estado", "Total Reabastecimentos"]

        fig_reab_estado = px.bar(
            df_reab_estado,
            x="Total Reabastecimentos",
            y="Estado",
            orientation="h",
            title="Top 10 Estados - Mais Reabastecimentos",
            color="Total Reabastecimentos",
            color_continuous_scale="Purples",
        )
        st.plotly_chart(fig_reab_estado, use_container_width=True)

    st.markdown("---")

    st.subheader("📊 Comparação: Demanda Atendida vs Não Atendida")

    df_atend_vs_nao = (
        df_estoque_filtered.groupby("Regiao")
        .agg({"Demanda_Atendida": "sum", "Demanda_Nao_Atendida": "sum"})
        .reset_index()
    )

    fig_atend_comparacao = go.Figure()
    fig_atend_comparacao.add_trace(
        go.Bar(
            x=df_atend_vs_nao["Regiao"],
            y=df_atend_vs_nao["Demanda_Atendida"],
            name="Demanda Atendida",
            marker_color="#00FFC6",
        )
    )
    fig_atend_comparacao.add_trace(
        go.Bar(
            x=df_atend_vs_nao["Regiao"],
            y=df_atend_vs_nao["Demanda_Nao_Atendida"],
            name="Demanda Não Atendida",
            marker_color="#FF6B6B",
        )
    )
    fig_atend_comparacao.update_layout(
        title="Demanda Atendida vs Não Atendida por Região",
        xaxis_title="Região",
        yaxis_title="Demanda",
        barmode="group",
        height=500,
    )
    st.plotly_chart(fig_atend_comparacao, use_container_width=True)
