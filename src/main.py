import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- Configuração da Página ---
st.set_page_config(
    page_title="PharmaSense AI - Otimização Logística",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚚 Otimização Logística e Distribuição - PharmaSense AI")
st.markdown(
    "Dashboard de monitoramento e análise de eficiência da cadeia de suprimentos farmacêutica. [cite: 253, 254]"
)


# --- 1. Carregamento dos Dados ---
# O arquivo deve estar no mesmo diretório ou dentro de 'assets/'
@st.cache_data(ttl=60)  # Cache por 60 segundos para permitir atualizações
def load_data():
    try:
        # Tenta carregar o arquivo simulado
        df = pd.read_csv("assets/logistica_simulada.csv")
        df["Data"] = pd.to_datetime(df["Data"])
        # Garantir que não há "Em Rota" em dados históricos
        df = df[df["Status"] != "Em Rota"]
        return df
    except FileNotFoundError:
        st.error(
            "Arquivo 'logistica_simulada.csv' não encontrado. Certifique-se de que o arquivo de dados simulados está no diretório correto."
        )
        return pd.DataFrame()  # Retorna DataFrame vazio em caso de erro


@st.cache_data(ttl=60)
def load_estoque_data():
    try:
        df_estoque = pd.read_csv("assets/demanda_estoque.csv")
        df_estoque["Data"] = pd.to_datetime(df_estoque["Data"])
        return df_estoque
    except FileNotFoundError:
        st.error(
            "Arquivo 'demanda_estoque.csv' não encontrado. Execute primeiro o script gerar_demanda_estoque.py."
        )
        return pd.DataFrame()


df = load_data()
df_estoque = load_estoque_data()

if df.empty:
    st.stop()

# Criar abas
tab1, tab2 = st.tabs(["📦 Logística", "📊 Estoque e Demanda"])

# --- 2. Filtros Laterais ---
st.sidebar.header("Filtros de Análise")

# Filtros comuns para ambas as abas
data_min = df["Data"].min().date()
data_max = df["Data"].max().date()

# Seletor de Período
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

# Seletor de Região
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

# Seletor de Estado (se a coluna existir)
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

# ========== ABA 1: LOGÍSTICA ==========
with tab1:
    # --- 3. KPIs de Impacto (Redução e Eficiência) ---
    st.header("Métricas de Impacto e Desempenho Logístico")

    # Cálculo de KPIs
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
            delta="Meta: 25%",  # Baseado no impacto esperado [cite: 232]
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
            delta="-5.0% (Simulado)",  # Alvo é reduzir ao máximo
            delta_color="inverse",
        )

    with col4:
        st.metric(
            label="Pegada de Carbono Média (Sustentabilidade)",
            value=f"{emissao_media:.1f} kg CO2",
            delta="Redução de 20% (Simulada)",  # Baseado no impacto esperado [cite: 234]
            delta_color="inverse",
        )

    st.markdown("---")

    # --- 4. Visualizações Detalhadas ---
    col_chart1, col_chart2 = st.columns(2)

    # Gráfico 1: Eficiência de Distribuição ao Longo do Tempo
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

    # Gráfico 2: Desempenho por Região e Status (Mapeamento Geoespacial - Proxy)
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
            title="Taxa de Atraso por Região (Alerta Geoespacial)",  # Simulação de Alerta
        )
        st.plotly_chart(fig_region, use_container_width=True)

    st.markdown("---")

    # --- 5. Tabela Detalhada (Monitoramento em Tempo Real - Conceito) ---
    st.subheader("Monitoramento de Rotas (Alerta de Condições)")
    st.caption(
        "Visualização para Roberto Almeida: Mapeamento Geoespacial e Alertas [cite: 255]"
    )

    # Tabela com as últimas 20 rotas e destaque para atrasos
    df_latest = df_filtered.sort_values("Data", ascending=False).head(20)

    def highlight_status(s):
        if s.Status == "Atrasado":
            return ["background-color: #ff6b6b; color: #000000"] * len(
                s
            )  # Vermelho mais forte
        else:
            return [""] * len(s)  # Entregue sem destaque

    # Definir ordem de colunas (incluir Estado se existir)
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

    # --- 6. Análise por Estado (se disponível) ---
    if "Estado" in df_filtered.columns:
        st.markdown("---")
        st.subheader("Desempenho por Estado")

        col_estado1, col_estado2 = st.columns(2)

        with col_estado1:
            # Top 10 estados mais rápidos
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
            # Top 10 estados mais lentos
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

    # --- 7. Insights de Otimização de Custo ---
    st.subheader("Análise de Otimização de Custo e Sustentabilidade")

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

# ========== ABA 2: ESTOQUE E DEMANDA ==========
with tab2:
    if df_estoque_filtered.empty:
        st.warning(
            "⚠️ Dados de estoque não disponíveis. Execute primeiro o script gerar_demanda_estoque.py para gerar os dados."
        )
        st.stop()

    st.header("📊 Análise de Estoque e Demanda")
    st.markdown("Monitoramento de estoque, stock out e demanda não atendida")

    # KPIs de Estoque
    st.subheader("Métricas Principais de Estoque")

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

    # Gráficos de Estoque
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

    # Análise de Atendimento
    st.subheader("Análise de Atendimento e Nível de Serviço")

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

    # Tabela de Monitoramento de Estoque
    st.subheader("Monitoramento de Estoque e Stock Out")
    st.caption("Últimos registros com indicadores de estoque baixo e stock out")

    # Filtrar registros relevantes
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

    # Resumo por Estado
    if "Estado" in df_estoque_filtered.columns:
        st.markdown("---")
        st.subheader("Resumo por Estado")

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
