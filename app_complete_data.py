import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import sqlite3
import hashlib
import numpy as np
import warnings
import time
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup
import uuid
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="SaudeJá - Análise Completa de Dados",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização do estado da sessão
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:16]

# Classe para carregar todos os dados CSV
class DataManager:
    def __init__(self):
        self.data_cache = {}

    @st.cache_data
    def load_covid_states(_self):
        """Carrega dados COVID por estados"""
        try:
            return pd.read_csv('us-states.csv')
        except FileNotFoundError:
            return pd.DataFrame()

    @st.cache_data
    def load_covid_counties(_self):
        """Carrega dados COVID por condados"""
        try:
            return pd.read_csv('us-counties.csv')
        except FileNotFoundError:
            return pd.DataFrame()

    @st.cache_data
    def load_covid_national(_self):
        """Carrega dados COVID nacionais"""
        try:
            return pd.read_csv('us.csv')
        except FileNotFoundError:
            return pd.DataFrame()

    @st.cache_data
    def load_covid_yearly(_self, year):
        """Carrega dados COVID por ano específico"""
        try:
            return pd.read_csv(f'us-counties-{year}.csv')
        except FileNotFoundError:
            return pd.DataFrame()

    @st.cache_data
    def load_colleges(_self):
        """Carrega dados de faculdades"""
        try:
            return pd.read_csv('colleges/colleges.csv')
        except FileNotFoundError:
            return pd.DataFrame()

    @st.cache_data
    def load_excess_deaths(_self):
        """Carrega dados de mortes excessivas"""
        try:
            return pd.read_csv('excess-deaths/deaths.csv')
        except FileNotFoundError:
            return pd.DataFrame()

    @st.cache_data
    def load_mask_use(_self):
        """Carrega dados de uso de máscaras"""
        try:
            return pd.read_csv('mask-use/mask-use-by-county.csv')
        except FileNotFoundError:
            return pd.DataFrame()

    @st.cache_data
    def load_prisons(_self):
        """Carrega dados de prisões"""
        try:
            return pd.read_csv('prisons/facilities.csv')
        except FileNotFoundError:
            return pd.DataFrame()

    def get_available_datasets(self):
        """Retorna informações sobre datasets disponíveis"""
        datasets = {
            'us-states': {'name': 'COVID-19 por Estados', 'loader': self.load_covid_states},
            'us-counties': {'name': 'COVID-19 por Condados', 'loader': self.load_covid_counties},
            'us-national': {'name': 'COVID-19 Nacional', 'loader': self.load_covid_national},
            'colleges': {'name': 'Dados de Faculdades', 'loader': self.load_colleges},
            'excess-deaths': {'name': 'Mortes Excessivas', 'loader': self.load_excess_deaths},
            'mask-use': {'name': 'Uso de Máscaras', 'loader': self.load_mask_use},
            'prisons': {'name': 'Dados de Prisões', 'loader': self.load_prisons}
        }

        available = {}
        for key, info in datasets.items():
            data = info['loader']()
            if not data.empty:
                available[key] = {
                    'name': info['name'],
                    'rows': len(data),
                    'cols': len(data.columns),
                    'data': data
                }

        return available

# Classe principal da aplicação expandida
class SaudeJaExpandedApp:
    def __init__(self):
        self.db_path = os.path.join(os.getcwd(), 'saudeja_expanded.db')
        self.data_manager = DataManager()
        self.setup_database()

    def setup_database(self):
        """Configura banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    action TEXT,
                    dataset TEXT,
                    data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()
        except Exception:
            pass

    def log_action(self, action, dataset=None, data=None):
        """Log de ação com dataset"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interactions (session_id, action, dataset, data) 
                VALUES (?, ?, ?, ?)
            ''', (st.session_state.session_id, action, dataset, json.dumps(data) if data else None))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def navigation(self):
        """Navegação principal"""
        st.sidebar.title("🏥 SaudeJá - Análise Completa")

        pages = {
            "🏠 Visão Geral": "overview",
            "📊 COVID Estados": "covid_states",
            "🏙️ COVID Condados": "covid_counties",
            "🇺🇸 COVID Nacional": "covid_national",
            "📚 Análise por Ano": "yearly_analysis",
            "🎓 Faculdades": "colleges",
            "💀 Mortes Excessivas": "excess_deaths",
            "😷 Uso de Máscaras": "mask_use",
            "🏢 Prisões": "prisons",
            "🔄 Comparar Datasets": "compare",
            "📈 Dashboard Geral": "dashboard"
        }

        for label, key in pages.items():
            if st.sidebar.button(label, key=f"btn_{key}"):
                st.session_state.page = key
                self.log_action(f"navigate_to_{key}")
                st.rerun()

        # Mostrar datasets disponíveis
        st.sidebar.markdown("---")
        st.sidebar.subheader("📁 Datasets Disponíveis")

        available = self.data_manager.get_available_datasets()
        for key, info in available.items():
            st.sidebar.write(f"✅ **{info['name']}**")
            st.sidebar.write(f"   📊 {info['rows']:,} linhas, {info['cols']} colunas")

        st.sidebar.markdown("---")
        st.sidebar.write(f"**Session:** {st.session_state.session_id}")

        return st.session_state.page

    def overview_page(self):
        """Página de visão geral de todos os dados"""
        st.title("🏠 Visão Geral - Todos os Datasets do Projeto")

        available_datasets = self.data_manager.get_available_datasets()

        st.markdown(f"""
        ### 📊 Resumo dos Dados Disponíveis
        
        Seu projeto contém **{len(available_datasets)} datasets** com dados reais de saúde pública:
        """)

        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)

        total_rows = sum(info['rows'] for info in available_datasets.values())
        total_cols = sum(info['cols'] for info in available_datasets.values())

        with col1:
            st.metric("Total de Datasets", len(available_datasets))
        with col2:
            st.metric("Total de Registros", f"{total_rows:,}")
        with col3:
            st.metric("Total de Colunas", total_cols)
        with col4:
            st.metric("Período", "2020-2024")

        # Tabela de datasets
        st.subheader("📋 Detalhes dos Datasets")

        dataset_summary = []
        for key, info in available_datasets.items():
            dataset_summary.append({
                'Dataset': info['name'],
                'Registros': f"{info['rows']:,}",
                'Colunas': info['cols'],
                'Tamanho': f"{info['rows'] * info['cols']:,} células",
                'Status': '✅ Carregado'
            })

        df_summary = pd.DataFrame(dataset_summary)
        st.dataframe(df_summary, use_container_width=True)

        # Gráfico de comparação de tamanhos
        st.subheader("📊 Comparação de Tamanhos dos Datasets")

        fig = px.bar(
            x=[info['name'] for info in available_datasets.values()],
            y=[info['rows'] for info in available_datasets.values()],
            title="Número de Registros por Dataset",
            labels={'x': 'Dataset', 'y': 'Número de Registros'}
        )
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

        # Seletor para preview
        st.subheader("👀 Preview dos Dados")

        selected_dataset = st.selectbox(
            "Selecione um dataset para preview:",
            options=list(available_datasets.keys()),
            format_func=lambda x: available_datasets[x]['name']
        )

        if selected_dataset:
            data = available_datasets[selected_dataset]['data']

            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Dataset:** {available_datasets[selected_dataset]['name']}")
                st.write(f"**Dimensões:** {data.shape[0]:,} linhas × {data.shape[1]} colunas")

                # Mostrar preview
                st.dataframe(data.head(10), use_container_width=True)

            with col2:
                st.write("**Colunas disponíveis:**")
                for col in data.columns:
                    st.write(f"• {col}")

                if st.button(f"📊 Analisar {available_datasets[selected_dataset]['name']}", key="analyze_selected"):
                    self.log_action("analyze_dataset", selected_dataset)
                    st.success(f"Análise de {available_datasets[selected_dataset]['name']} iniciada!")

    def covid_states_page(self):
        """Análise COVID por Estados (original aprimorada)"""
        st.title("📊 COVID-19 - Análise por Estados")

        covid_data = self.data_manager.load_covid_states()

        if covid_data.empty:
            st.error("❌ Dados de estados não encontrados")
            return

        col1, col2 = st.columns(2)

        with col1:
            selected_states = st.multiselect(
                "Selecione estados para análise:",
                options=sorted(covid_data['state'].unique()),
                default=sorted(covid_data['state'].unique())[:5],
                key="states_selector"
            )

            analysis_type = st.radio(
                "Tipo de análise:",
                ["Casos", "Óbitos", "Tendência Temporal", "Comparação Estados"],
                key="analysis_type"
            )

        with col2:
            if 'date' in covid_data.columns:
                covid_data['date'] = pd.to_datetime(covid_data['date'])
                min_date = covid_data['date'].min()
                max_date = covid_data['date'].max()

                date_range = st.date_input(
                    "Período de análise:",
                    value=[min_date, max_date],
                    min_value=min_date,
                    max_value=max_date,
                    key="date_range"
                )

            show_per_capita = st.checkbox("Mostrar per capita", key="per_capita")
            show_stats = st.checkbox("Mostrar estatísticas", key="show_stats")

        if selected_states and st.button("🔍 Analisar Estados", key="analyze_states_btn"):
            self.log_action("covid_states_analysis", "us-states", {
                "states": selected_states,
                "type": analysis_type
            })

            # Filtrar dados
            filtered_data = covid_data[covid_data['state'].isin(selected_states)]

            if 'date' in filtered_data.columns and len(date_range) == 2:
                filtered_data = filtered_data[
                    (filtered_data['date'] >= pd.to_datetime(date_range[0])) &
                    (filtered_data['date'] <= pd.to_datetime(date_range[1]))
                ]

            # Criar visualização
            if analysis_type == "Casos":
                fig = px.bar(
                    filtered_data.groupby('state')['cases'].sum().reset_index(),
                    x='state',
                    y='cases',
                    title=f"Total de Casos COVID-19 - {', '.join(selected_states)}"
                )
            elif analysis_type == "Óbitos":
                fig = px.bar(
                    filtered_data.groupby('state')['deaths'].sum().reset_index(),
                    x='state',
                    y='deaths',
                    title=f"Total de Óbitos COVID-19 - {', '.join(selected_states)}"
                )
            elif analysis_type == "Tendência Temporal":
                fig = px.line(
                    filtered_data,
                    x='date',
                    y='cases',
                    color='state',
                    title="Tendência Temporal de Casos"
                )
            else:  # Comparação Estados
                comparison_data = filtered_data.groupby('state').agg({
                    'cases': 'sum',
                    'deaths': 'sum'
                }).reset_index()

                fig = px.scatter(
                    comparison_data,
                    x='cases',
                    y='deaths',
                    text='state',
                    title="Comparação: Casos vs Óbitos por Estado"
                )
                fig.update_traces(textposition="top center")

            st.plotly_chart(fig, use_container_width=True)

            # Estatísticas
            if show_stats:
                st.subheader("📈 Estatísticas Detalhadas")

                stats_data = filtered_data.groupby('state').agg({
                    'cases': ['sum', 'mean', 'max'],
                    'deaths': ['sum', 'mean', 'max']
                }).round(2)

                st.dataframe(stats_data, use_container_width=True)

            # Relatório
            if st.button("📋 Gerar Relatório Completo", key="report_states_btn"):
                report = {
                    'dataset': 'COVID-19 Estados',
                    'analysis_date': datetime.now().isoformat(),
                    'states_analyzed': selected_states,
                    'period': str(date_range) if 'date_range' in locals() else 'Todos os dados',
                    'total_records': len(filtered_data),
                    'summary_stats': filtered_data.describe().to_dict()
                }

                st.download_button(
                    label="⬇️ Download Relatório JSON",
                    data=json.dumps(report, indent=2, default=str),
                    file_name=f"relatorio_estados_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )

    def covid_counties_page(self):
        """Análise COVID por Condados"""
        st.title("🏙️ COVID-19 - Análise por Condados")

        counties_data = self.data_manager.load_covid_counties()

        if counties_data.empty:
            st.warning("⚠️ Dados de condados não encontrados")
            return

        st.success(f"✅ Dados carregados: {len(counties_data):,} registros de condados")

        # Filtros
        col1, col2, col3 = st.columns(3)

        with col1:
            if 'state' in counties_data.columns:
                selected_states = st.multiselect(
                    "Filtrar por estados:",
                    options=sorted(counties_data['state'].unique()),
                    default=sorted(counties_data['state'].unique())[:3]
                )

        with col2:
            if 'county' in counties_data.columns and selected_states:
                filtered_counties = counties_data[counties_data['state'].isin(selected_states)]
                selected_counties = st.multiselect(
                    "Filtrar por condados:",
                    options=sorted(filtered_counties['county'].unique()),
                    default=sorted(filtered_counties['county'].unique())[:10]
                )

        with col3:
            analysis_level = st.selectbox(
                "Nível de análise:",
                ["Top 10 Condados", "Por Estado", "Comparação Temporal"]
            )

        if st.button("🔍 Analisar Condados", key="analyze_counties_btn"):
            self.log_action("covid_counties_analysis", "us-counties")

            # Análise baseada no nível selecionado
            if analysis_level == "Top 10 Condados":
                top_counties = counties_data.groupby(['state', 'county'])['cases'].sum().reset_index()
                top_counties = top_counties.nlargest(10, 'cases')
                top_counties['location'] = top_counties['county'] + ', ' + top_counties['state']

                fig = px.bar(
                    top_counties,
                    x='location',
                    y='cases',
                    title="Top 10 Condados com Mais Casos"
                )
                fig.update_xaxis(tickangle=45)

            elif analysis_level == "Por Estado" and selected_states:
                state_data = counties_data[counties_data['state'].isin(selected_states)]
                state_summary = state_data.groupby('state')['cases'].sum().reset_index()

                fig = px.pie(
                    state_summary,
                    values='cases',
                    names='state',
                    title=f"Distribuição de Casos por Estado"
                )

            else:  # Comparação Temporal
                if 'date' in counties_data.columns:
                    counties_data['date'] = pd.to_datetime(counties_data['date'])
                    temporal_data = counties_data.groupby(['date', 'state'])['cases'].sum().reset_index()

                    fig = px.line(
                        temporal_data[temporal_data['state'].isin(selected_states[:5])],
                        x='date',
                        y='cases',
                        color='state',
                        title="Evolução Temporal por Estado"
                    )

            st.plotly_chart(fig, use_container_width=True)

            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Condados", counties_data['county'].nunique())
            with col2:
                st.metric("Total Estados", counties_data['state'].nunique())
            with col3:
                st.metric("Total Casos", f"{counties_data['cases'].sum():,}")
            with col4:
                st.metric("Total Óbitos", f"{counties_data['deaths'].sum():,}")

    def run(self):
        """Executa a aplicação expandida"""
        try:
            current_page = self.navigation()

            if current_page == 'overview':
                self.overview_page()
            elif current_page == 'covid_states':
                self.covid_states_page()
            elif current_page == 'covid_counties':
                self.covid_counties_page()
            # Implementar outras páginas conforme necessário
            else:
                st.title(f"🚧 Página em Desenvolvimento: {current_page}")
                st.info("Esta seção será implementada em breve com análises específicas do dataset selecionado.")

        except Exception as e:
            st.error(f"Erro na aplicação: {e}")
            st.info("Recarregue a página para tentar novamente.")

# Executar aplicação
if __name__ == "__main__":
    app = SaudeJaExpandedApp()
    app.run()
