import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os

# Configuração da Página
st.set_page_config(page_title="Driva Dashboard", layout="wide")
st.title("📊 Dashboard de Monitoramento de Enriquecimento")
st.markdown("*Conectado via API Analytics (Arquitetura Desacoplada)*")

# --- CONFIGURAÇÃO DA URL DA API ---
# Pega a variável de ambiente do Docker. Se não existir, usa localhost.
API_URL = os.getenv("API_URL", "http://localhost:3000")

# Função auxiliar para pegar dados da API
def get_data(endpoint):
    try:
        response = requests.get(f"{API_URL}/analytics/{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro na API: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Não foi possível conectar na API ({API_URL}): {e}")
        return None

# 1. Carregar KPIs (Overview)
overview = get_data("overview")

if overview:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Processamentos", overview["total_processamentos"])
    col2.metric("Sucesso (%)", f"{overview['taxa_sucesso']}%")
    col3.metric("Tempo Médio (min)", f"{overview['tempo_medio_minutos']}")
    col4.metric("Contatos Processados", f"{overview['total_contatos_processados']:,}")

st.markdown("---")

# 2. Carregar Gráficos
charts = get_data("charts")

if charts:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Distribuição por Status")
        df_status = pd.DataFrame(list(charts["status_distribution"].items()), columns=["Status", "Quantidade"])
        if not df_status.empty:
            fig_status = px.pie(df_status, names='Status', values='Quantidade', title='Status dos Jobs', hole=0.4)
            st.plotly_chart(fig_status, use_container_width=True)

    with c2:
        st.subheader("Tamanho dos Jobs")
        df_size = pd.DataFrame(list(charts["size_distribution"].items()), columns=["Categoria", "Quantidade"])
        ordem = ["PEQUENO", "MEDIO", "GRANDE", "MUITO_GRANDE"]
        if not df_size.empty:
            fig_cat = px.bar(df_size, x='Categoria', y='Quantidade', title='Contagem por Tamanho', 
                             category_orders={"Categoria": ordem})
            st.plotly_chart(fig_cat, use_container_width=True)

# 3. Carregar Lista Detalhada
st.subheader("Detalhamento dos Dados (Camada Gold)")
data_list = get_data("list")

if data_list:
    df_lista = pd.DataFrame(data_list)
    st.dataframe(df_lista)