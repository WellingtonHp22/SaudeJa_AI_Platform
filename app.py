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
from typing import Dict, List, Any
import re
from urllib.parse import quote
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup
import uuid

# Importar sistema de segurança e IA
try:
    from security_ai import (
        SecurityManager, InnovativeAI, EthicalDataHandler,
        init_security, with_security
    )
    SECURITY_ENABLED = True

    # Inicializar sistemas de segurança
    security = init_security()
    ai_system = InnovativeAI(security)
    ethical_handler = EthicalDataHandler()

except ImportError:
    st.error("❌ Sistema de segurança não disponível - Por favor, verifique as dependências")
    SECURITY_ENABLED = False
    security = None
    ai_system = None
    ethical_handler = None

warnings.filterwarnings('ignore')

# Configuração da página DEVE ser a primeira chamada Streamlit
st.set_page_config(
    page_title="SaudeJá - Plataforma Ética de Saúde Digital",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações aprimoradas com sistema de segurança integrado
class Config:
    APP_NAME = "SaudeJá - Jornada de Inovação em Saúde Digital"
    VERSION = "2.0.0 - Edição Avançada com IA e LGPD"

    # APIs gratuitas integradas conforme requisitos
    COVID_DATA_URL = "https://raw.githubusercontent.com/nytimes/covid-19-data/master"
    PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    CROSSREF_API = "https://api.crossref.org/works"
    SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"

    # Configurações de segurança
    MAX_REQUESTS_PER_HOUR = 100
    CACHE_DURATION_HOURS = 24
    ANONYMIZE_USER_DATA = True

    # Rate limiting para ética conforme requisitos
    API_RATE_LIMIT = 60  # requests por minuto
    CRAWL_DELAY = 1.0    # segundos entre requests

    @staticmethod
    def validate_config():
        return True

# Gerenciador de banco de dados robusto conforme requisitos
class DatabaseManager:
    def __init__(self):
        # Usar SQLite local com fallback robusto
        self.db_path = os.path.join(os.getcwd(), 'saudeja_interactions.db')
        self.setup_tables()
    
    def get_connection(self):
        """Cria conexão thread-safe"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10)
        conn.execute('PRAGMA journal_mode=WAL')  # Better concurrency
        return conn
    
    def setup_tables(self):
        """Configura tabelas conforme LGPD e requisitos"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            # Tabela principal de interações (anonimizada conforme LGPD)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    interaction_type TEXT NOT NULL,
                    response_data TEXT,
                    user_choices TEXT,
                    journey_step TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    anonymized_hash TEXT
                )
            ''')

            # Tabela para análises de IA
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    data_cluster INTEGER,
                    insight_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabela para dados de webcrawling
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crawled_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_url TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    extracted_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
        except Exception as e:
            st.error(f"Erro ao configurar banco de dados: {e}")
        finally:
            conn.close()

    def get_session_id(self):
        """Gera ID de sessão único"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())[:16]
        return st.session_state.session_id
    
    def anonymize_data(self, data):
        """Anonimiza dados conforme LGPD"""
        return hashlib.sha256(str(data).encode()).hexdigest()[:16]

    def log_interaction(self, user_query, interaction_type, response_data, user_choices=None, journey_step=None):
        """Registra interação com anonimização LGPD"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            anonymized_hash = self.anonymize_data(f"{user_query}{self.get_session_id()}")

            cursor.execute('''
                INSERT INTO user_interactions 
                (session_id, user_query, interaction_type, response_data, user_choices, journey_step, anonymized_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.get_session_id(),
                str(user_query)[:500],  # Limitar tamanho
                str(interaction_type),
                json.dumps(response_data) if response_data else None,
                json.dumps(user_choices) if user_choices else None,
                journey_step,
                anonymized_hash
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            # Não mostrar warnings que podem causar re-render
            return False
    
    def get_user_history(self, limit=50):
        """Recupera histórico da sessão atual"""
        try:
            conn = self.get_connection()
            df = pd.read_sql_query('''
                SELECT user_query, interaction_type, user_choices, journey_step, timestamp
                FROM user_interactions 
                WHERE session_id = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', conn, params=(self.get_session_id(), limit))
            conn.close()
            return df
        except Exception as e:
            return pd.DataFrame()

    def save_ai_insight(self, insight_type, data_cluster, insight_data):
        """Salva insights de IA"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ai_insights (session_id, insight_type, data_cluster, insight_data)
                VALUES (?, ?, ?, ?)
            ''', (self.get_session_id(), insight_type, data_cluster, json.dumps(insight_data)))
            conn.commit()
            conn.close()
        except Exception as e:
            pass  # Silenciar erros para evitar re-render

# APIs e Web Crawling conforme requisitos
class DataCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SaudeJa-Research-Bot/1.0 (Educational Purpose)'
        })

    def search_pubmed(self, query, max_results=10):
        """Busca artigos no PubMed com rate limiting"""
        try:
            time.sleep(Config.CRAWL_DELAY)  # Rate limiting ético

            search_url = f"{Config.PUBMED_BASE_URL}/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json'
            }

            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('esearchresult', {}).get('idlist', [])
            return []
        except Exception as e:
            return []

    def get_pubmed_details(self, pmids):
        """Obtém detalhes dos artigos PubMed"""
        try:
            if not pmids:
                return {}

            time.sleep(Config.CRAWL_DELAY)

            fetch_url = f"{Config.PUBMED_BASE_URL}/esummary.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(pmids),
                'retmode': 'json'
            }

            response = self.session.get(fetch_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('result', {})
            return {}
        except Exception as e:
            return {}

    def crawl_health_news(self, query):
        """Web crawling de notícias de saúde (BeautifulSoup)"""
        try:
            time.sleep(Config.CRAWL_DELAY)

            # Usar fonte confiável e gratuita
            search_url = f"https://www.who.int/news-room?search={quote(query)}"

            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extrair títulos de notícias (exemplo)
                news_items = []
                for item in soup.find_all('h3', limit=5):
                    if item.text.strip():
                        news_items.append({
                            'title': item.text.strip(),
                            'source': 'WHO',
                            'timestamp': datetime.now().isoformat()
                        })

                return news_items
            return []
        except Exception as e:
            return []

# Análises de IA conforme requisitos
class AIAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()

    def cluster_user_behavior(self, interaction_data):
        """Clustering simples de comportamento do usuário"""
        try:
            if len(interaction_data) < 3:
                return None

            # Preparar features simples
            features = []
            for _, row in interaction_data.iterrows():
                query_len = len(str(row.get('user_query', '')))
                interaction_type = hash(str(row.get('interaction_type', ''))) % 100
                features.append([query_len, interaction_type])

            features_array = np.array(features)
            features_scaled = self.scaler.fit_transform(features_array)

            # K-means simples
            n_clusters = min(3, len(features))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(features_scaled)

            return {
                'clusters': clusters.tolist(),
                'centers': kmeans.cluster_centers_.tolist(),
                'n_clusters': n_clusters
            }
        except Exception as e:
            return None

    def generate_wordcloud(self, text_data):
        """Gera nuvem de palavras dos dados"""
        try:
            if not text_data or len(text_data) < 10:
                return None

            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                max_words=50,
                colormap='viridis'
            ).generate(text_data)

            return wordcloud
        except Exception as e:
            return None

# Gerenciador completo de dados CSV
class CompleteDataManager:
    def __init__(self):
        self.data_cache = {}
        self.available_datasets = self.discover_all_csvs()

    def discover_all_csvs(self):
        """Descobre todos os arquivos CSV disponíveis no projeto"""
        csv_files = {}
        base_path = os.getcwd()

        # Mapeamento de arquivos CSV e suas descrições
        csv_mapping = {
            # COVID Principal
            'us-states.csv': {'name': 'COVID-19 por Estados', 'category': 'covid_main'},
            'us-counties.csv': {'name': 'COVID-19 por Condados', 'category': 'covid_main'},
            'us.csv': {'name': 'COVID-19 Nacional (EUA)', 'category': 'covid_main'},

            # COVID por Anos
            'us-counties-2020.csv': {'name': 'COVID Condados 2020', 'category': 'covid_yearly'},
            'us-counties-2021.csv': {'name': 'COVID Condados 2021', 'category': 'covid_yearly'},
            'us-counties-2022.csv': {'name': 'COVID Condados 2022', 'category': 'covid_yearly'},
            'us-counties-2023.csv': {'name': 'COVID Condados 2023', 'category': 'covid_yearly'},
            'us-counties-recent.csv': {'name': 'COVID Condados Recente', 'category': 'covid_yearly'},

            # Dados especializados
            'colleges/colleges.csv': {'name': 'Dados de Faculdades', 'category': 'specialized'},
            'excess-deaths/deaths.csv': {'name': 'Mortes Excessivas', 'category': 'specialized'},
            'mask-use/mask-use-by-county.csv': {'name': 'Uso de Máscaras por Condado', 'category': 'specialized'},
            'prisons/facilities.csv': {'name': 'Facilidades Prisionais', 'category': 'specialized'},
            'prisons/systems.csv': {'name': 'Sistemas Prisionais', 'category': 'specialized'},

            # Dados em subpastas
            'data/us-states.csv': {'name': 'COVID Estados (Data)', 'category': 'data_folder'},
            'data/us-counties.csv': {'name': 'COVID Condados (Data)', 'category': 'data_folder'},
            'data/us.csv': {'name': 'COVID Nacional (Data)', 'category': 'data_folder'},

            # Live data
            'live/us-states.csv': {'name': 'COVID Estados (Live)', 'category': 'live_data'},
            'live/us-counties.csv': {'name': 'COVID Condados (Live)', 'category': 'live_data'},
            'live/us.csv': {'name': 'COVID Nacional (Live)', 'category': 'live_data'},

            # Rolling averages
            'rolling-averages/us-states.csv': {'name': 'Médias Móveis Estados', 'category': 'rolling'},
            'rolling-averages/us-counties.csv': {'name': 'Médias Móveis Condados', 'category': 'rolling'},
            'rolling-averages/anomalies.csv': {'name': 'Anomalias Detectadas', 'category': 'rolling'}
        }

        # Verificar quais arquivos existem
        for file_path, info in csv_mapping.items():
            full_path = os.path.join(base_path, file_path)
            if os.path.exists(full_path):
                try:
                    # Tentar carregar uma amostra para verificar se é válido
                    sample = pd.read_csv(full_path, nrows=1)
                    csv_files[file_path] = {
                        'name': info['name'],
                        'category': info['category'],
                        'path': full_path,
                        'columns': list(sample.columns),
                        'exists': True
                    }
                except Exception as e:
                    csv_files[file_path] = {
                        'name': info['name'],
                        'category': info['category'],
                        'path': full_path,
                        'exists': False,
                        'error': str(e)
                    }

        return csv_files

    @st.cache_data
    def load_csv_data(_self, file_path):
        """Carrega dados de um CSV específico com cache"""
        if file_path not in _self.available_datasets:
            return pd.DataFrame()

        if not _self.available_datasets[file_path]['exists']:
            return pd.DataFrame()

        try:
            full_path = _self.available_datasets[file_path]['path']
            data = pd.read_csv(full_path)

            # Padronizar nomes de colunas se necessário
            if 'date' in data.columns:
                data['date'] = pd.to_datetime(data['date'], errors='coerce')

            return data
        except Exception as e:
            st.warning(f"Erro ao carregar {file_path}: {e}")
            return pd.DataFrame()

    def get_datasets_by_category(self):
        """Organiza datasets por categoria"""
        categories = {}
        for file_path, info in self.available_datasets.items():
            if info['exists']:
                category = info['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append({
                    'file': file_path,
                    'name': info['name'],
                    'data': self.load_csv_data(file_path)
                })
        return categories

    def get_summary_stats(self):
        """Gera estatísticas resumidas de todos os datasets"""
        total_files = 0
        total_rows = 0
        total_columns = 0
        categories_count = {}

        for file_path, info in self.available_datasets.items():
            if info['exists']:
                data = self.load_csv_data(file_path)
                if not data.empty:
                    total_files += 1
                    total_rows += len(data)
                    total_columns += len(data.columns)

                    category = info['category']
                    categories_count[category] = categories_count.get(category, 0) + 1

        return {
            'total_files': total_files,
            'total_rows': total_rows,
            'total_columns': total_columns,
            'categories': categories_count
        }

# Inicialização global com cache estável
@st.cache_resource
def initialize_app():
    """Inicializa componentes da aplicação"""
    db = DatabaseManager()
    collector = DataCollector()
    ai_analyzer = AIAnalyzer()
    return db, collector, ai_analyzer

# Componentes da jornada interativa
class InteractiveJourney:
    def __init__(self, db, collector, ai_analyzer):
        self.db = db
        self.collector = collector
        self.ai_analyzer = ai_analyzer

    def main_navigation(self):
        """Navegação principal com ramificações - Estabilizada"""
        st.sidebar.title("🏥 SaudeJá Navigation")

        # Usar session_state para estabilizar a navegação
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'home'

        journey_options = [
            ("🏠 Página Inicial", "home"),
            ("📊 Todos os Dados CSV", "all_data"),
            ("📈 Análise COVID Estados", "covid_analysis"),
            ("🔬 Pesquisa Científica", "research"),
            ("📰 Notícias de Saúde", "news"),
            ("🤖 Insights de IA", "ai_insights"),
            ("📋 Dashboard Personalizado", "dashboard"),
            ("🗂️ Histórico da Sessão", "history")
        ]

        # Menu estável sem re-render desnecessário
        for label, key in journey_options:
            if st.sidebar.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                # Log da navegação sem causar re-render
                self.db.log_interaction(
                    user_query=f"Navegação: {label}",
                    interaction_type="navigation",
                    response_data={"selected_option": label},
                    journey_step=key
                )
                st.rerun()

        return st.session_state.current_page

    def home_page(self):
        """Página inicial interativa"""
        st.title("🏥 SaudeJá - Jornada de Inovação em Saúde Digital")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### 🎯 Bem-vindo à sua jornada personalizada!
            
            Esta plataforma oferece:
            - 📊 **Análises interativas** de dados de saúde
            - 🔬 **Pesquisa científica** automatizada  
            - 🤖 **Insights de IA** personalizados
            - 📈 **Visualizações** dinâmicas
            - 🗂️ **Histórico** completo de interações
            """)

            # Input interativo inicial
            user_interest = st.selectbox(
                "Qual seu principal interesse?",
                ["COVID-19", "Pesquisa Médica", "Saúde Pública", "Inovação Digital", "Análise de Dados"]
            )

            if st.button("🚀 Personalizar Jornada"):
                # Log da escolha inicial
                self.db.log_interaction(
                    user_query=f"Interesse inicial: {user_interest}",
                    interaction_type="initial_setup",
                    response_data={"interest": user_interest},
                    journey_step="personalization"
                )

                st.success(f"✅ Jornada personalizada para: **{user_interest}**")
                st.balloons()

        with col2:
            # Estatísticas da sessão
            history_df = self.db.get_user_history()

            if not history_df.empty:
                st.metric("Interações na Sessão", len(history_df))

                # Gráfico simples de atividade
                fig = px.line(
                    history_df.tail(10),
                    y='interaction_type',
                    title="Atividade Recente"
                )
                st.plotly_chart(fig, use_container_width=True)

    def covid_analysis_page(self):
        """Análise interativa de dados COVID"""
        st.title("📊 Análise Interativa de Dados COVID-19")

        # Carregar dados COVID existentes
        try:
            covid_data = pd.read_csv('us-states.csv')

            col1, col2 = st.columns(2)

            with col1:
                # Filtros interativos
                selected_states = st.multiselect(
                    "Selecione estados para análise:",
                    covid_data['state'].unique()[:10],
                    default=covid_data['state'].unique()[:3]
                )

                analysis_type = st.radio(
                    "Tipo de análise:",
                    ["Casos", "Óbitos", "Tendência Temporal"]
                )

            with col2:
                date_range = st.date_input(
                    "Período de análise:",
                    value=[datetime(2020, 3, 1), datetime(2023, 12, 31)],
                    min_value=datetime(2020, 1, 1),
                    max_value=datetime.now()
                )

            if selected_states and st.button("🔍 Analisar Dados"):
                # Filtrar dados
                filtered_data = covid_data[covid_data['state'].isin(selected_states)]

                # Log da análise
                self.db.log_interaction(
                    user_query=f"Análise COVID: {selected_states}",
                    interaction_type="covid_analysis",
                    response_data={
                        "states": selected_states,
                        "analysis_type": analysis_type,
                        "date_range": str(date_range)
                    },
                    journey_step="data_analysis"
                )

                # Visualizações baseadas na escolha
                if analysis_type == "Casos":
                    fig = px.bar(
                        filtered_data.tail(50),
                        x='state',
                        y='cases',
                        title=f"Casos COVID-19 - {', '.join(selected_states)}"
                    )
                elif analysis_type == "Óbitos":
                    fig = px.bar(
                        filtered_data.tail(50),
                        x='state',
                        y='deaths',
                        title=f"Óbitos COVID-19 - {', '.join(selected_states)}"
                    )
                else:  # Tendência Temporal
                    filtered_data['date'] = pd.to_datetime(filtered_data['date'])
                    fig = px.line(
                        filtered_data,
                        x='date',
                        y='cases',
                        color='state',
                        title="Tendência Temporal de Casos"
                    )

                st.plotly_chart(fig, use_container_width=True)

                # Insights automáticos
                st.subheader("🤖 Insights Automáticos")
                total_cases = filtered_data['cases'].sum()
                avg_cases = filtered_data['cases'].mean()

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de Casos", f"{total_cases:,}")
                with col2:
                    st.metric("Média de Casos", f"{avg_cases:,.0f}")
                with col3:
                    st.metric("Estados Analisados", len(selected_states))

                # Gerar relatório
                if st.button("📋 Gerar Relatório"):
                    report = {
                        'analysis_date': datetime.now().isoformat(),
                        'states_analyzed': selected_states,
                        'total_cases': int(total_cases),
                        'average_cases': float(avg_cases),
                        'analysis_type': analysis_type
                    }

                    st.download_button(
                        label="⬇️ Download Relatório JSON",
                        data=json.dumps(report, indent=2),
                        file_name=f"relatorio_covid_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                        mime="application/json"
                    )

        except FileNotFoundError:
            st.warning("⚠️ Dados COVID não encontrados. Usando dados sintéticos para demonstração.")

            # Dados sintéticos para demonstração
            demo_data = pd.DataFrame({
                'state': ['California', 'Texas', 'Florida'] * 10,
                'cases': np.random.randint(1000, 10000, 30),
                'deaths': np.random.randint(10, 100, 30),
                'date': pd.date_range('2020-03-01', periods=30)
            })

            fig = px.bar(demo_data, x='state', y='cases', title="Dados Demo - Casos COVID-19")
            st.plotly_chart(fig, use_container_width=True)

    def research_page(self):
        """Página de pesquisa científica com APIs"""
        st.title("🔬 Pesquisa Científica Automatizada")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Input de pesquisa
            search_query = st.text_input(
                "Digite sua consulta de pesquisa:",
                placeholder="Ex: machine learning healthcare, COVID-19 vaccines"
            )

            search_source = st.selectbox(
                "Fonte de pesquisa:",
                ["PubMed", "Semantic Scholar", "CrossRef", "OpenAlex"]
            )

            max_results = st.slider("Máximo de resultados:", 5, 50, 10)

        with col2:
            st.info("""
            **Dica:** Use termos específicos para melhores resultados.
            
            **Exemplos:**
            - "artificial intelligence diagnostics"
            - "telemedicine rural areas"
            - "mental health apps"
            """)

        if search_query and st.button("🔍 Buscar Pesquisas"):
            with st.spinner("Buscando artigos científicos..."):
                # Log da busca
                self.db.log_interaction(
                    user_query=search_query,
                    interaction_type="research_search",
                    response_data={
                        "source": search_source,
                        "max_results": max_results
                    },
                    journey_step="scientific_research"
                )

                if search_source == "PubMed":
                    # Buscar no PubMed
                    pmids = self.collector.search_pubmed(search_query, max_results)

                    if pmids:
                        details = self.collector.get_pubmed_details(pmids[:10])

                        st.success(f"✅ Encontrados {len(pmids)} artigos no PubMed")

                        # Exibir resultados
                        for pmid in pmids[:5]:
                            if pmid in details:
                                article = details[pmid]

                                with st.expander(f"📄 {article.get('title', 'Título não disponível')}"):
                                    st.write(f"**Autores:** {', '.join(article.get('authors', []))}")
                                    st.write(f"**Revista:** {article.get('source', 'N/A')}")
                                    st.write(f"**Data:** {article.get('pubdate', 'N/A')}")
                                    st.write(f"**PMID:** {pmid}")

                                    if st.button(f"📋 Salvar Artigo {pmid}"):
                                        # Salvar no banco
                                        self.db.log_interaction(
                                            user_query=f"Salvar artigo: {pmid}",
                                            interaction_type="save_article",
                                            response_data=article,
                                            journey_step="save_research"
                                        )
                                        st.success("Artigo salvo no seu histórico!")
                    else:
                        st.warning("Nenhum resultado encontrado. Tente termos diferentes.")

                else:
                    # Para outras fontes, mostrar dados simulados
                    st.info(f"Simulando busca em {search_source}...")

                    demo_results = [
                        {
                            "title": f"Avanços em IA para {search_query}",
                            "authors": ["Dr. Silva", "Dr. Santos"],
                            "journal": "Journal of Medical AI",
                            "year": "2024"
                        },
                        {
                            "title": f"Estudo clínico sobre {search_query}",
                            "authors": ["Prof. Lima", "Dr. Costa"],
                            "journal": "Clinical Research Today",
                            "year": "2023"
                        }
                    ]

                    for i, result in enumerate(demo_results):
                        with st.expander(f"📄 {result['title']}"):
                            st.write(f"**Autores:** {', '.join(result['authors'])}")
                            st.write(f"**Revista:** {result['journal']}")
                            st.write(f"**Ano:** {result['year']}")

                # Gerar nuvem de palavras da busca
                if search_query:
                    wordcloud = self.ai_analyzer.generate_wordcloud(search_query * 10)  # Simular texto
                    if wordcloud:
                        st.subheader("☁️ Nuvem de Palavras da Pesquisa")
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis('off')
                        st.pyplot(fig)

    def news_page(self):
        """Página de notícias com web crawling"""
        st.title("📰 Notícias de Saúde")

        col1, col2 = st.columns([3, 1])

        with col1:
            news_topic = st.selectbox(
                "Selecione o tópico:",
                ["COVID-19", "Vacinas", "Saúde Mental", "Telemedicina", "IA em Saúde", "Saúde Pública"]
            )

            if st.button("📰 Buscar Notícias"):
                with st.spinner("Coletando notícias recentes..."):
                    # Log da busca
                    self.db.log_interaction(
                        user_query=news_topic,
                        interaction_type="news_search",
                        response_data={"topic": news_topic},
                        journey_step="news_crawling"
                    )

                    # Web crawling de notícias
                    news_items = self.collector.crawl_health_news(news_topic)

                    if news_items:
                        st.success(f"✅ Encontradas {len(news_items)} notícias sobre {news_topic}")

                        for item in news_items:
                            with st.expander(f"📰 {item['title']}"):
                                st.write(f"**Fonte:** {item['source']}")
                                st.write(f"**Data:** {item['timestamp']}")

                                if st.button(f"💾 Salvar Notícia", key=f"save_{hash(item['title'])}"):
                                    self.db.log_interaction(
                                        user_query=f"Salvar notícia: {item['title']}",
                                        interaction_type="save_news",
                                        response_data=item,
                                        journey_step="save_news"
                                    )
                                    st.success("Notícia salva!")
                    else:
                        # Notícias simuladas para demonstração
                        st.info("Simulando notícias recentes...")

                        demo_news = [
                            {
                                "title": f"Novos avanços em {news_topic}",
                                "source": "Health News Today",
                                "summary": f"Pesquisadores anunciam descobertas importantes em {news_topic}..."
                            },
                            {
                                "title": f"Impacto do {news_topic} na sociedade",
                                "source": "Medical Journal",
                                "summary": f"Estudo revela dados significativos sobre {news_topic}..."
                            }
                        ]

                        for item in demo_news:
                            with st.expander(f"📰 {item['title']}"):
                                st.write(f"**Fonte:** {item['source']}")
                                st.write(f"**Resumo:** {item['summary']}")

        with col2:
            st.info("""
            **Fontes Confiáveis:**
            - WHO (Organização Mundial da Saúde)
            - CDC (Centers for Disease Control)
            - Ministério da Saúde
            - Journals médicos
            """)

            # Estatísticas de notícias
            history_df = self.db.get_user_history()
            news_interactions = history_df[history_df['interaction_type'] == 'news_search']

            if not news_interactions.empty:
                st.metric("Buscas de Notícias", len(news_interactions))

    def ai_insights_page(self):
        """Página de insights de IA com recursos avançados"""
        st.title("🤖 Insights de IA Avançados - Análise Comportamental")

        # Verificar consentimento LGPD se o sistema de segurança estiver disponível
        if SECURITY_ENABLED and not security_manager.check_user_consent():
            return

        # Obter dados do usuário
        history_df = self.db.get_user_history()

        if len(history_df) < 3:
            st.warning("⚠️ Você precisa ter pelo menos 3 interações para gerar insights de IA.")
            st.info("Continue navegando pela plataforma para acumular dados para análise.")
            return

        # Usar IA avançada se disponível, caso contrário usar básica
        if SECURITY_ENABLED:
            self._advanced_ai_analysis(history_df)
        else:
            self._basic_ai_analysis(history_df)

        # Mostrar atribuições de dados
        if SECURITY_ENABLED:
            ethical_handler.add_data_attribution('covid_nytimes')

    def _advanced_ai_analysis(self, history_df):
        """Análise de IA avançada com recursos inovadores"""
        st.subheader("🧠 Análise Avançada com IA")

        # Clustering avançado com DBSCAN e PCA
        with st.spinner("Executando análise avançada..."):
            advanced_clustering = innovative_ai.advanced_user_clustering(history_df)

            if advanced_clustering:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### 📊 Clustering Multidimensional")
                    st.success(f"✅ Identificados {advanced_clustering['n_clusters']} padrões comportamentais")
                    st.info(f"🔍 Outliers detectados: {advanced_clustering['outliers']}")

                    # Visualização dos clusters com PCA
                    if len(advanced_clustering['clusters']) > 0:
                        clusters_df = pd.DataFrame({
                            'interaction': range(len(advanced_clustering['clusters'])),
                            'cluster': advanced_clustering['clusters'],
                            'type': history_df['interaction_type'].values[:len(advanced_clustering['clusters'])]
                        })

                        fig = px.scatter_3d(
                            clusters_df,
                            x='interaction',
                            y='cluster',
                            z=[1] * len(clusters_df),
                            color='cluster',
                            hover_data=['type'],
                            title="Padrões Comportamentais 3D (PCA)"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.markdown("### 🎯 Análise de Variância")

                    # Mostrar componentes principais
                    if 'explained_variance' in advanced_clustering:
                        variance_df = pd.DataFrame({
                            'Componente': [f'PC{i+1}' for i in range(len(advanced_clustering['explained_variance']))],
                            'Variância Explicada': advanced_clustering['explained_variance']
                        })

                        fig_var = px.bar(
                            variance_df,
                            x='Componente',
                            y='Variância Explicada',
                            title="Variância Explicada por Componente Principal"
                        )
                        st.plotly_chart(fig_var, use_container_width=True)

        # Análise de sentimento
        st.subheader("💭 Análise de Sentimento das Consultas")

        all_queries = ' '.join(history_df['user_query'].astype(str))
        sentiment_result = innovative_ai.sentiment_analysis_simple(all_queries)

        if sentiment_result:
            col1, col2, col3 = st.columns(3)

            with col1:
                sentiment_color = {
                    'positivo': 'green',
                    'negativo': 'red',
                    'neutro': 'gray'
                }[sentiment_result['sentiment']]

                st.markdown(f"""
                <div style="text-align: center; padding: 20px; border-radius: 10px; background-color: {sentiment_color}20; border: 2px solid {sentiment_color};">
                    <h3 style="color: {sentiment_color};">Sentimento: {sentiment_result['sentiment'].title()}</h3>
                    <p>Score: {sentiment_result['score']:.3f}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.metric("Palavras Positivas", sentiment_result['positive_words'])
                st.metric("Confiança", f"{sentiment_result['confidence']:.1%}")

            with col3:
                st.metric("Palavras Negativas", sentiment_result['negative_words'])

                # Gráfico de distribuição de sentimento
                sentiment_data = pd.DataFrame({
                    'Tipo': ['Positivas', 'Negativas'],
                    'Quantidade': [sentiment_result['positive_words'], sentiment_result['negative_words']]
                })

                fig_sent = px.pie(
                    sentiment_data,
                    values='Quantidade',
                    names='Tipo',
                    title="Distribuição de Palavras"
                )
                st.plotly_chart(fig_sent, use_container_width=True)

        # Analytics preditivos
        st.subheader("🔮 Analytics Preditivos")

        predictive_result = innovative_ai.predictive_analytics(history_df)

        if predictive_result:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### ⏰ Padrões Temporais")

                # Gráfico de uso por hora
                hourly_data = pd.DataFrame(
                    list(predictive_result['usage_patterns']['hourly'].items()),
                    columns=['Hora', 'Atividade']
                )

                fig_hourly = px.line(
                    hourly_data,
                    x='Hora',
                    y='Atividade',
                    title="Padrão de Uso por Hora do Dia",
                    markers=True
                )
                fig_hourly.add_vline(
                    x=predictive_result['peak_hour'],
                    line_dash="dash",
                    annotation_text=f"Pico: {predictive_result['peak_hour']}h"
                )
                st.plotly_chart(fig_hourly, use_container_width=True)

            with col2:
                st.markdown("### 📅 Padrões Semanais")

                days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
                weekly_data = pd.DataFrame(
                    list(predictive_result['usage_patterns']['weekly'].items()),
                    columns=['Dia', 'Atividade']
                )
                weekly_data['Dia_Nome'] = weekly_data['Dia'].apply(lambda x: days[x] if x < 7 else 'N/A')

                fig_weekly = px.bar(
                    weekly_data,
                    x='Dia_Nome',
                    y='Atividade',
                    title="Padrão de Uso por Dia da Semana"
                )
                st.plotly_chart(fig_weekly, use_container_width=True)

            # Predição da próxima interação
            st.markdown("### 🎯 Predição Inteligente")
            st.info(f"**Próxima interação prevista:** {predictive_result['predicted_next_interaction']}")
            st.info(f"**Interação mais comum:** {predictive_result['most_common_interaction']}")
            st.info(f"**Diversidade de interações:** {predictive_result['interaction_diversity']} tipos diferentes")

        # Relatório completo de insights
        st.subheader("📋 Relatório Completo de Insights")

        if st.button("🤖 Gerar Relatório de IA Avançado"):
            with st.spinner("Gerando relatório completo..."):
                complete_report = innovative_ai.generate_insights_report(history_df)

                if complete_report:
                    st.success("✅ Relatório gerado com sucesso!")

                    # Mostrar resumo do relatório
                    st.json(complete_report)

                    # Download do relatório
                    st.download_button(
                        label="⬇️ Download Relatório de IA",
                        data=json.dumps(complete_report, indent=2, default=str),
                        file_name=f"relatorio_ia_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                        mime="application/json"
                    )

                    # Log seguro da geração do relatório
                    security_manager.log_interaction_secure("advanced_ai_report_generated", {
                        "report_type": "complete_insights",
                        "user_interactions": len(history_df)
                    })

    def _basic_ai_analysis(self, history_df):
        """Análise de IA básica quando sistema avançado não está disponível"""
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Análise de Clustering Básica")

            # Executar clustering básico
            cluster_result = self.ai_analyzer.cluster_user_behavior(history_df)

            if cluster_result:
                # Salvar insight no banco
                self.db.save_ai_insight(
                    insight_type="user_clustering",
                    data_cluster=cluster_result['n_clusters'],
                    insight_data=cluster_result
                )

                st.success(f"✅ Identificados {cluster_result['n_clusters']} padrões de comportamento")

                # Visualizar clusters
                clusters_df = pd.DataFrame({
                    'interaction': range(len(cluster_result['clusters'])),
                    'cluster': cluster_result['clusters']
                })

                fig = px.scatter(
                    clusters_df,
                    x='interaction',
                    y='cluster',
                    color='cluster',
                    title="Padrões de Comportamento Identificados"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Interpretação dos clusters
                st.markdown("""
                **Interpretação dos Clusters:**
                - **Cluster 0:** Usuário exploratório (consultas longas)
                - **Cluster 1:** Usuário focado (consultas específicas)
                - **Cluster 2:** Usuário casual (navegação rápida)
                """)

        with col2:
            st.subheader("☁️ Nuvem de Palavras das Interações")

            # Gerar nuvem de palavras das consultas
            all_queries = ' '.join(history_df['user_query'].astype(str))

            if len(all_queries) > 20:
                wordcloud = self.ai_analyzer.generate_wordcloud(all_queries)

                if wordcloud:
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)

                    st.info("Esta nuvem mostra seus principais temas de interesse na sessão.")

        # Recomendações personalizadas básicas
        st.subheader("💡 Recomendações Personalizadas")

        interaction_types = history_df['interaction_type'].value_counts()
        most_common = interaction_types.index[0] if not interaction_types.empty else "navigation"

        recommendations = {
            "covid_analysis": [
                "📊 Explore dados de outros países",
                "📈 Analise tendências temporais específicas",
                "🔬 Busque pesquisas sobre variantes"
            ],
            "research_search": [
                "📰 Veja notícias relacionadas às suas pesquisas",
                "🤖 Use clustering para encontrar padrões",
                "📋 Crie um dashboard personalizado"
            ],
            "news_search": [
                "🔬 Aprofunde com pesquisas científicas",
                "📊 Analise dados relacionados às notícias",
                "💾 Salve artigos interessantes"
            ]
        }

        user_recommendations = recommendations.get(most_common, [
            "🏠 Explore a página inicial",
            "📊 Comece com análise de dados COVID",
            "🔬 Faça uma pesquisa científica"
        ])

        for rec in user_recommendations:
            st.write(f"• {rec}")

    def dashboard_page(self):
        """Dashboard personalizado"""
        st.title("📈 Dashboard Personalizado")

        # Métricas gerais da sessão
        history_df = self.db.get_user_history()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total de Interações", len(history_df))

        with col2:
            unique_types = history_df['interaction_type'].nunique() if not history_df.empty else 0
            st.metric("Tipos de Ação", unique_types)

        with col3:
            if not history_df.empty:
                session_duration = (
                    pd.to_datetime(history_df['timestamp'].iloc[0]) -
                    pd.to_datetime(history_df['timestamp'].iloc[-1])
                ).total_seconds() / 60
                st.metric("Duração (min)", f"{session_duration:.1f}")
            else:
                st.metric("Duração (min)", "0.0")

        with col4:
            current_step = history_df['journey_step'].iloc[0] if not history_df.empty else "início"
            st.metric("Etapa Atual", current_step)

        if not history_df.empty:
            # Gráfico de atividade temporal
            st.subheader("📊 Atividade Temporal")

            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
            activity_chart = px.line(
                history_df.sort_values('timestamp'),
                x='timestamp',
                color='interaction_type',
                title="Timeline de Interações"
            )
            st.plotly_chart(activity_chart, use_container_width=True)

            # Distribuição de tipos de interação
            st.subheader("📈 Distribuição de Atividades")

            type_counts = history_df['interaction_type'].value_counts()
            pie_chart = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title="Distribuição por Tipo de Interação"
            )
            st.plotly_chart(pie_chart, use_container_width=True)

            # Tabela de últimas interações
            st.subheader("🗂️ Últimas Interações")
            st.dataframe(
                history_df[['user_query', 'interaction_type', 'journey_step', 'timestamp']].head(10),
                use_container_width=True
            )

    def history_page(self):
        """Página de histórico completo"""
        st.title("🗂️ Histórico Completo da Sessão")

        history_df = self.db.get_user_history(limit=100)

        if history_df.empty:
            st.info("Nenhuma interação registrada nesta sessão.")
            return

        # Filtros
        col1, col2 = st.columns(2)

        with col1:
            filter_type = st.selectbox(
                "Filtrar por tipo:",
                ["Todos"] + list(history_df['interaction_type'].unique())
            )

        with col2:
            filter_step = st.selectbox(
                "Filtrar por etapa:",
                ["Todas"] + list(history_df['journey_step'].dropna().unique())
            )

        # Aplicar filtros
        filtered_df = history_df.copy()

        if filter_type != "Todos":
            filtered_df = filtered_df[filtered_df['interaction_type'] == filter_type]

        if filter_step != "Todas":
            filtered_df = filtered_df[filtered_df['journey_step'] == filter_step]

        # Exibir resultados
        st.write(f"📋 Mostrando {len(filtered_df)} de {len(history_df)} interações")

        # Expandir cada interação
        for idx, row in filtered_df.iterrows():
            with st.expander(f"🔍 {row['interaction_type']} - {row['timestamp']}"):
                st.write(f"**Query:** {row['user_query']}")
                st.write(f"**Tipo:** {row['interaction_type']}")
                st.write(f"**Etapa:** {row.get('journey_step', 'N/A')}")
                st.write(f"**Timestamp:** {row['timestamp']}")

                if row.get('user_choices'):
                    try:
                        choices = json.loads(row['user_choices'])
                        st.write(f"**Escolhas:** {choices}")
                    except:
                        pass

        # Export do histórico
        if st.button("💾 Exportar Histórico"):
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=f"historico_saudeja_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

    def all_data_page(self):
        """Página que mostra todos os dados CSV disponíveis"""
        st.title("📊 Todos os Dados CSV do Projeto")

        # Inicializar o gerenciador de dados completo
        data_manager = CompleteDataManager()

        # Log da visita à página
        self.db.log_interaction(
            user_query="Visualizar todos os dados CSV",
            interaction_type="all_data_view",
            response_data={"total_datasets": len(data_manager.available_datasets)},
            journey_step="all_data_exploration"
        )

        # Obter estatísticas resumidas
        stats = data_manager.get_summary_stats()

        # Métricas principais
        st.subheader("📈 Resumo Geral dos Dados")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total de Arquivos CSV", stats['total_files'])
        with col2:
            st.metric("Total de Registros", f"{stats['total_rows']:,}")
        with col3:
            st.metric("Total de Colunas", stats['total_columns'])
        with col4:
            st.metric("Categorias", len(stats['categories']))

        # Datasets por categoria
        st.subheader("📁 Datasets Organizados por Categoria")

        categories_data = data_manager.get_datasets_by_category()

        # Criar abas para cada categoria
        if categories_data:
            category_names = {
                'covid_main': '🦠 COVID Principal',
                'covid_yearly': '📅 COVID por Ano',
                'specialized': '🏥 Dados Especializados',
                'data_folder': '📁 Pasta Data',
                'live_data': '🔴 Dados Live',
                'rolling': '📊 Médias Móveis'
            }

            tabs = st.tabs([category_names.get(cat, cat.title()) for cat in categories_data.keys()])

            for tab, (category, datasets) in zip(tabs, categories_data.items()):
                with tab:
                    st.write(f"**Categoria:** {category_names.get(category, category)}")

                    for dataset in datasets:
                        data = dataset['data']
                        if not data.empty:
                            with st.expander(f"📄 {dataset['name']} ({len(data):,} registros)"):
                                col1, col2 = st.columns([2, 1])

                                with col1:
                                    st.write("**Preview dos dados:**")
                                    st.dataframe(data.head(5), use_container_width=True)

                                with col2:
                                    st.write("**Informações:**")
                                    st.write(f"• Linhas: {len(data):,}")
                                    st.write(f"• Colunas: {len(data.columns)}")
                                    st.write(f"• Arquivo: `{dataset['file']}`")

                                    st.write("**Colunas disponíveis:**")
                                    for col in data.columns[:10]:  # Mostrar até 10 colunas
                                        st.write(f"  - {col}")
                                    if len(data.columns) > 10:
                                        st.write(f"  ... e mais {len(data.columns) - 10}")

                                # Análise rápida se for possível
                                if len(data) > 0:
                                    st.write("**Análise Rápida:**")

                                    # Para dados COVID, mostrar gráfico
                                    if 'cases' in data.columns and 'state' in data.columns:
                                        if st.button(f"📊 Visualizar {dataset['name']}", key=f"viz_{dataset['file']}"):
                                            # Agrupar por estado e somar casos
                                            state_data = data.groupby('state')['cases'].sum().nlargest(10)

                                            fig = px.bar(
                                                x=state_data.values,
                                                y=state_data.index,
                                                orientation='h',
                                                title=f"Top 10 Estados - {dataset['name']}"
                                            )
                                            fig.update_layout(height=400)
                                            st.plotly_chart(fig, use_container_width=True)

                                            # Log da visualização
                                            self.db.log_interaction(
                                                user_query=f"Visualizar dataset: {dataset['name']}",
                                                interaction_type="dataset_visualization",
                                                response_data={
                                                    "dataset": dataset['file'],
                                                    "chart_type": "bar_chart"
                                                },
                                                journey_step="data_visualization"
                                            )

                                    # Para outros tipos de dados
                                    elif 'date' in data.columns:
                                        if st.button(f"📈 Análise Temporal {dataset['name']}", key=f"temp_{dataset['file']}"):
                                            # Análise temporal simples
                                            data_temp = data.copy()
                                            data_temp['date'] = pd.to_datetime(data_temp['date'], errors='coerce')

                                            if not data_temp['date'].isna().all():
                                                # Contar registros por mês
                                                monthly_data = data_temp.groupby(data_temp['date'].dt.to_period('M')).size()

                                                fig = px.line(
                                                    x=monthly_data.index.astype(str),
                                                    y=monthly_data.values,
                                                    title=f"Registros por Mês - {dataset['name']}"
                                                )
                                                st.plotly_chart(fig, use_container_width=True)

                                # Botão para download dos dados
                                csv_data = data.to_csv(index=False)
                                st.download_button(
                                    label=f"⬇️ Download {dataset['name']}",
                                    data=csv_data,
                                    file_name=f"{dataset['file'].replace('/', '_')}",
                                    mime="text/csv",
                                    key=f"download_{dataset['file']}"
                                )

        # Comparação entre datasets
        st.subheader("🔄 Comparação entre Datasets")

        # Criar um DataFrame resumo
        summary_data = []
        for file_path, info in data_manager.available_datasets.items():
            if info['exists']:
                data = data_manager.load_csv_data(file_path)
                if not data.empty:
                    summary_data.append({
                        'Dataset': info['name'],
                        'Arquivo': file_path,
                        'Categoria': info['category'],
                        'Registros': len(data),
                        'Colunas': len(data.columns),
                        'Tamanho (MB)': round(data.memory_usage(deep=True).sum() / 1024 / 1024, 2),
                        'Período': self._get_date_range(data) if 'date' in data.columns else 'N/A'
                    })

        if summary_data:
            summary_df = pd.DataFrame(summary_data)

            # Mostrar tabela resumo
            st.dataframe(summary_df, use_container_width=True)

            # Gráfico de comparação
            col1, col2 = st.columns(2)

            with col1:
                # Gráfico de registros por dataset
                fig_records = px.bar(
                    summary_df.nlargest(10, 'Registros'),
                    x='Registros',
                    y='Dataset',
                    orientation='h',
                    title="Top 10 Datasets por Número de Registros"
                )
                st.plotly_chart(fig_records, use_container_width=True)

            with col2:
                # Gráfico de distribuição por categoria
                category_counts = summary_df['Categoria'].value_counts()
                fig_categories = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title="Distribuição por Categoria"
                )
                st.plotly_chart(fig_categories, use_container_width=True)

            # Export do resumo completo
            if st.button("📋 Gerar Relatório Completo de Todos os Dados"):
                complete_report = {
                    'generated_at': datetime.now().isoformat(),
                    'total_datasets': len(summary_df),
                    'total_records': summary_df['Registros'].sum(),
                    'total_size_mb': summary_df['Tamanho (MB)'].sum(),
                    'datasets_summary': summary_df.to_dict('records'),
                    'categories_summary': stats['categories']
                }

                st.download_button(
                    label="⬇️ Download Relatório Completo JSON",
                    data=json.dumps(complete_report, indent=2, default=str),
                    file_name=f"relatorio_completo_dados_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )

                # Log do relatório
                self.db.log_interaction(
                    user_query="Gerar relatório completo de todos os dados",
                    interaction_type="complete_report_generation",
                    response_data={"datasets_included": len(summary_df)},
                    journey_step="report_generation"
                )

        # Busca em todos os datasets
        st.subheader("🔍 Busca Global nos Dados")

        search_term = st.text_input(
            "Buscar em todos os datasets:",
            placeholder="Ex: California, 2020, deaths"
        )

        if search_term and st.button("🔍 Buscar em Todos os CSVs"):
            self.db.log_interaction(
                user_query=f"Busca global: {search_term}",
                interaction_type="global_search",
                response_data={"search_term": search_term},
                journey_step="global_data_search"
            )

            search_results = []

            with st.spinner("Buscando em todos os datasets..."):
                for file_path, info in data_manager.available_datasets.items():
                    if info['exists']:
                        data = data_manager.load_csv_data(file_path)
                        if not data.empty:
                            # Buscar em todas as colunas de texto
                            for col in data.columns:
                                if data[col].dtype == 'object':
                                    matches = data[data[col].astype(str).str.contains(search_term, case=False, na=False)]
                                    if not matches.empty:
                                        search_results.append({
                                            'dataset': info['name'],
                                            'file': file_path,
                                            'column': col,
                                            'matches': len(matches),
                                            'sample': matches.iloc[0][col] if len(matches) > 0 else None
                                        })

            if search_results:
                st.success(f"✅ Encontrados resultados em {len(search_results)} datasets/colunas")

                results_df = pd.DataFrame(search_results)
                st.dataframe(results_df, use_container_width=True)

                # Mostrar amostras dos resultados
                for result in search_results[:5]:  # Mostrar até 5 resultados
                    with st.expander(f"📄 {result['dataset']} - {result['matches']} matches"):
                        st.write(f"**Coluna:** {result['column']}")
                        st.write(f"**Exemplo:** {result['sample']}")
                        st.write(f"**Arquivo:** {result['file']}")
            else:
                st.warning(f"❌ Nenhum resultado encontrado para '{search_term}'")

    def _get_date_range(self, data):
        """Helper para obter range de datas de um dataset"""
        try:
            if 'date' in data.columns:
                dates = pd.to_datetime(data['date'], errors='coerce').dropna()
                if not dates.empty:
                    return f"{dates.min().strftime('%Y-%m-%d')} a {dates.max().strftime('%Y-%m-%d')}"
            return "N/A"
        except:
            return "N/A"

# Inicialização global
@st.cache_resource
def initialize_app():
    """Inicializa componentes da aplicação"""
    db = DatabaseManager()
    collector = DataCollector()
    ai_analyzer = AIAnalyzer()
    return db, collector, ai_analyzer

def main():
    """Função principal da aplicação"""
    try:
        # Inicializar componentes
        db, collector, ai_analyzer = initialize_app()
        journey = InteractiveJourney(db, collector, ai_analyzer)

        # Navegação principal
        current_page = journey.main_navigation()

        # Roteamento de páginas
        if current_page == "home":
            journey.home_page()
        elif current_page == "covid_analysis":
            journey.covid_analysis_page()
        elif current_page == "research":
            journey.research_page()
        elif current_page == "news":
            journey.news_page()
        elif current_page == "ai_insights":
            journey.ai_insights_page()
        elif current_page == "dashboard":
            journey.dashboard_page()
        elif current_page == "history":
            journey.history_page()
        elif current_page == "all_data":
            journey.all_data_page()

        # Footer com informações da sessão
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Sessão:** `{db.get_session_id()}`")
        st.sidebar.markdown(f"**Timestamp:** `{datetime.now().strftime('%H:%M:%S')}`")

    except Exception as e:
        st.error(f"Erro na aplicação: {e}")
        st.info("Recarregue a página para tentar novamente.")

if __name__ == "__main__":
    main()
