import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
import requests
import os

# configuracao pagina
st.set_page_config(
    page_title="Driva Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# definir fonte e estilo
st.markdown("""
    <style>
        .block-container {padding-top: 1rem; padding-bottom: 0rem;}
        h1 {font-size: 1.8rem;}
        h3 {font-size: 1.2rem;}
    </style>
""", unsafe_allow_html=True)

# define fuso horario
br_tz = pytz.timezone('America/Sao_Paulo')

# Carregar dados pela api
@st.cache_data(ttl=10)
def load_data():
    api_url = os.getenv("API_URL", "http://api:3000")
    
    try:
        response = requests.get(f"{api_url}/analytics/list")
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            
            if df.empty:
                return df

            df = df.rename(columns={
                "id_enriquecimento": "id",
                "nome_workspace": "workspace_name",
                "total_contatos": "total_contacts",
                "tipo_contato": "contact_type",
                "data_criacao": "created_at"
            })

            # Colocar as datas no horario de Brasilia
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at'])
                try:
                    df['created_at'] = df['created_at'].dt.tz_localize('UTC').dt.tz_convert(br_tz)
                except:
                    df['created_at'] = df['created_at'].dt.tz_convert(br_tz)

            if 'data_atualizacao' in df.columns:
                df['data_atualizacao'] = pd.to_datetime(df['data_atualizacao'])
                try:
                    df['data_atualizacao'] = df['data_atualizacao'].dt.tz_localize('UTC').dt.tz_convert(br_tz)
                except:
                    df['data_atualizacao'] = df['data_atualizacao'].dt.tz_convert(br_tz)
            
            return df
        else:
            st.error(f"Erro na API: {response.status_code}")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erro ao conectar na API: {e}")
        return pd.DataFrame()

df = load_data()

# parte lateral do dashboard (sidebar)
with st.sidebar:
    st.title("Driva Pipeline")
    st.markdown("### Dashboard Unificado")
    st.info("Sistema Online")
    hora_atual = datetime.now(br_tz).strftime('%H:%M:%S')
    st.caption(f"Atualizado: {hora_atual} (BRT)")

# parte de cima
st.title("Visão Geral")

if not df.empty:
    
    # calcular métricas
    total_recs = len(df)
    total_contatos = df['total_contacts'].sum()
    total_sucesso = df[df['status_processamento'] == 'CONCLUIDO'].shape[0]
    taxa_sucesso = (total_sucesso / total_recs) * 100 if total_recs > 0 else 0 

    # layout
    col_kpi, col_graph = st.columns([1, 2])
    
    # kpis
    with col_kpi:
        st.markdown("#### Métricas Principais")
        st.metric("Total Jobs", f"{total_recs:,.0f}")
        st.metric("Total Contatos", f"{total_contatos:,.0f}")
        st.metric("Taxa de Sucesso", f"{taxa_sucesso:.1f}%")

    # gráfico de pizza
    with col_graph:
        st.markdown("#### Status do Pipeline")
        status_counts = df['status_processamento'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        fig_status = px.pie(
            status_counts, 
            values='Count', 
            names='Status', 
            hole=0.6, 
            color_discrete_sequence=px.colors.sequential.RdBu, 
            template="plotly_dark",
            height=300 
        )
        fig_status.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_status, use_container_width=True)

    # explorador de dados ou lista/tabela de enriquecimentos
    st.markdown("---")
    st.markdown("Lista/Tabela de Enriquecimentos")
    
    # filtros
    with st.expander("Filtros", expanded=False):
        f1, f2 = st.columns(2)
        with f1:
            opcoes_status = df['status_processamento'].unique()
            filtro_status = st.multiselect("Status:", options=opcoes_status, default=opcoes_status)
        with f2:
            opcoes_tipo = df['contact_type'].unique()
            filtro_tipo = st.multiselect("Tipo:", options=opcoes_tipo, default=opcoes_tipo)
    
    df_view = df.copy()
    if filtro_status:
        df_view = df_view[df_view['status_processamento'].isin(filtro_status)]
    if filtro_tipo:
        df_view = df_view[df_view['contact_type'].isin(filtro_tipo)]
    
    # tabela
    st.dataframe(
        df_view, 
        use_container_width=True,
        height=350,
        column_order=[
            "created_at",
            "data_atualizacao",
            "workspace_name", 
            "categoria_tamanho_job",
            "contact_type", 
            "total_contacts", 
            "status_processamento"
        ],
        column_config={
            "created_at": st.column_config.DatetimeColumn("Criado em", format="DD/MM HH:mm"),
            "data_atualizacao": st.column_config.DatetimeColumn("Atualizado em", format="DD/MM HH:mm"),
            "workspace_name": st.column_config.TextColumn("Workspace"),
            "categoria_tamanho_job": st.column_config.TextColumn("Tamanho"),
            "contact_type": st.column_config.TextColumn("Tipo"),
            "total_contacts": st.column_config.NumberColumn("Contatos", format="%d"),
            "status_processamento": st.column_config.TextColumn("Status")
        },
        hide_index=True
    )
    st.caption(f"Total: {len(df_view)} registros.")

else:
    st.warning("Aguardando dados... Rode o workflow no n8n!")