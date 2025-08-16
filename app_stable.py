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
    page_title="SaudeJá - Jornada de Inovação",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização do estado da sessão
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:16]

# Classe principal da aplicação
class SaudeJaApp:
    def __init__(self):
        self.db_path = os.path.join(os.getcwd(), 'saudeja_stable.db')
        self.setup_database()

    def setup_database(self):
        """Configura banco de dados de forma estável"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    action TEXT,
                    data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()
        except Exception:
            pass  # Silenciar erros para evitar warnings

    def log_action(self, action, data=None):
        """Log de ação simplificado"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interactions (session_id, action, data) 
                VALUES (?, ?, ?)
            ''', (st.session_state.session_id, action, json.dumps(data) if data else None))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def get_history(self):
        """Recupera histórico de forma segura"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query('''
                SELECT action, data, timestamp 
                FROM interactions 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 50
            ''', conn, params=(st.session_state.session_id,))
            conn.close()
            return df
        except Exception:
            return pd.DataFrame()

    def navigation(self):
        """Navegação estável sem conflitos"""
        st.sidebar.title("🏥 SaudeJá Navigation")

        pages = {
            "🏠 Início": "home",
            "📊 COVID Analysis": "covid",
            "🔬 Research": "research",
            "📰 News": "news",
            "🤖 AI Insights": "ai",
            "📈 Dashboard": "dashboard",
            "🗂️ History": "history"
        }

        # Navigation buttons
        for label, key in pages.items():
            if st.sidebar.button(label, key=f"btn_{key}"):
                st.session_state.page = key
                self.log_action(f"navigate_to_{key}")
                st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.write(f"**Session:** {st.session_state.session_id}")
        st.sidebar.write(f"**Time:** {datetime.now().strftime('%H:%M:%S')}")

        return st.session_state.page

    def home_page(self):
        """Página inicial simplificada"""
        st.title("🏥 SaudeJá - Health Innovation Journey")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### Welcome to your personalized health data journey!
            
            **Features:**
            - 📊 Interactive COVID-19 data analysis
            - 🔬 Scientific research automation
            - 📰 Health news crawling
            - 🤖 AI-powered insights
            - 📈 Personalized dashboard
            """)

            interest = st.selectbox(
                "Select your main interest:",
                ["COVID-19", "Medical Research", "Public Health", "Digital Innovation"]
            )

            if st.button("🚀 Personalize Journey"):
                self.log_action("personalize", {"interest": interest})
                st.success(f"✅ Journey personalized for: **{interest}**")
                st.balloons()

        with col2:
            history = self.get_history()
            if not history.empty:
                st.metric("Session Interactions", len(history))

                # Simple activity chart
                recent_actions = history.head(10)['action'].value_counts()
                if not recent_actions.empty:
                    fig = px.bar(
                        x=recent_actions.values,
                        y=recent_actions.index,
                        orientation='h',
                        title="Recent Activity"
                    )
                    st.plotly_chart(fig, use_container_width=True)

    def covid_page(self):
        """Página de análise COVID estabilizada"""
        st.title("📊 COVID-19 Interactive Data Analysis")

        # Load COVID data
        try:
            covid_data = pd.read_csv('us-states.csv')

            col1, col2 = st.columns(2)

            with col1:
                selected_states = st.multiselect(
                    "Select states for analysis:",
                    options=covid_data['state'].unique()[:15],
                    default=covid_data['state'].unique()[:3],
                    key="states_selector"
                )

                analysis_type = st.radio(
                    "Analysis type:",
                    ["Cases", "Deaths", "Temporal Trend"],
                    key="analysis_type"
                )

            with col2:
                date_range = st.date_input(
                    "Analysis period:",
                    value=[datetime(2020, 3, 1), datetime(2023, 12, 31)],
                    key="date_range"
                )

                show_per_capita = st.checkbox("Show per capita", key="per_capita")

            if selected_states and st.button("🔍 Analyze Data", key="analyze_btn"):
                # Filter data
                filtered_data = covid_data[covid_data['state'].isin(selected_states)]

                # Log analysis
                self.log_action("covid_analysis", {
                    "states": selected_states,
                    "type": analysis_type,
                    "per_capita": show_per_capita
                })

                # Create visualization
                if analysis_type == "Cases":
                    fig = px.bar(
                        filtered_data.tail(50),
                        x='state',
                        y='cases',
                        title=f"COVID-19 Cases - {', '.join(selected_states)}"
                    )
                elif analysis_type == "Deaths":
                    fig = px.bar(
                        filtered_data.tail(50),
                        x='state',
                        y='deaths',
                        title=f"COVID-19 Deaths - {', '.join(selected_states)}"
                    )
                else:  # Temporal Trend
                    filtered_data['date'] = pd.to_datetime(filtered_data['date'])
                    fig = px.line(
                        filtered_data,
                        x='date',
                        y='cases',
                        color='state',
                        title="Temporal Trend of Cases"
                    )

                st.plotly_chart(fig, use_container_width=True)

                # Insights
                st.subheader("🤖 Automatic Insights")
                total_cases = filtered_data['cases'].sum()
                avg_cases = filtered_data['cases'].mean()

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Cases", f"{total_cases:,}")
                with col2:
                    st.metric("Average Cases", f"{avg_cases:,.0f}")
                with col3:
                    st.metric("States Analyzed", len(selected_states))

                # Generate report
                if st.button("📋 Generate Report", key="report_btn"):
                    report = {
                        'analysis_date': datetime.now().isoformat(),
                        'states': selected_states,
                        'total_cases': int(total_cases),
                        'average_cases': float(avg_cases),
                        'type': analysis_type
                    }

                    st.download_button(
                        label="⬇️ Download JSON Report",
                        data=json.dumps(report, indent=2),
                        file_name=f"covid_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                        mime="application/json"
                    )

        except FileNotFoundError:
            st.warning("⚠️ COVID data not found. Using synthetic data for demonstration.")

            # Synthetic data
            demo_data = pd.DataFrame({
                'state': ['California', 'Texas', 'Florida'] * 10,
                'cases': np.random.randint(1000, 10000, 30),
                'deaths': np.random.randint(10, 100, 30),
                'date': pd.date_range('2020-03-01', periods=30)
            })

            fig = px.bar(demo_data, x='state', y='cases', title="Demo Data - COVID-19 Cases")
            st.plotly_chart(fig, use_container_width=True)

    def research_page(self):
        """Página de pesquisa científica"""
        st.title("🔬 Scientific Research Automation")

        col1, col2 = st.columns([2, 1])

        with col1:
            search_query = st.text_input(
                "Enter your research query:",
                placeholder="e.g., machine learning healthcare",
                key="research_query"
            )

            source = st.selectbox(
                "Research source:",
                ["PubMed", "arXiv", "Google Scholar", "Semantic Scholar"],
                key="research_source"
            )

            max_results = st.slider("Max results:", 5, 50, 10, key="max_results")

        with col2:
            st.info("""
            **Tips:**
            - Use specific terms
            - Try different sources
            - Check recent publications
            """)

        if search_query and st.button("🔍 Search Research", key="search_btn"):
            self.log_action("research_search", {
                "query": search_query,
                "source": source,
                "max_results": max_results
            })

            with st.spinner("Searching scientific articles..."):
                # Simulate research results
                demo_results = [
                    {
                        "title": f"Advances in AI for {search_query}",
                        "authors": ["Dr. Smith", "Dr. Johnson"],
                        "journal": "Nature Medicine",
                        "year": "2024",
                        "doi": "10.1038/example.2024"
                    },
                    {
                        "title": f"Clinical applications of {search_query}",
                        "authors": ["Prof. Wilson", "Dr. Brown"],
                        "journal": "The Lancet",
                        "year": "2023",
                        "doi": "10.1016/example.2023"
                    }
                ]

                st.success(f"✅ Found {len(demo_results)} articles")

                for i, result in enumerate(demo_results):
                    with st.expander(f"📄 {result['title']}"):
                        st.write(f"**Authors:** {', '.join(result['authors'])}")
                        st.write(f"**Journal:** {result['journal']}")
                        st.write(f"**Year:** {result['year']}")
                        st.write(f"**DOI:** {result['doi']}")

                        if st.button(f"💾 Save Article", key=f"save_article_{i}"):
                            self.log_action("save_article", result)
                            st.success("Article saved!")

                # Word cloud simulation
                if len(search_query) > 5:
                    st.subheader("☁️ Research Terms Cloud")
                    try:
                        wordcloud = WordCloud(
                            width=800, height=400,
                            background_color='white'
                        ).generate(search_query * 20)

                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis('off')
                        st.pyplot(fig)
                    except Exception:
                        st.info("Word cloud generation temporarily unavailable")

    def news_page(self):
        """Página de notícias de saúde"""
        st.title("📰 Health News")

        col1, col2 = st.columns([3, 1])

        with col1:
            topic = st.selectbox(
                "Select news topic:",
                ["COVID-19", "Vaccines", "Mental Health", "Telemedicine", "AI in Health"],
                key="news_topic"
            )

            if st.button("📰 Fetch News", key="news_btn"):
                self.log_action("news_search", {"topic": topic})

                with st.spinner("Collecting recent news..."):
                    # Simulate news
                    demo_news = [
                        {
                            "title": f"Latest developments in {topic}",
                            "source": "Health News Today",
                            "summary": f"Researchers announce important discoveries in {topic}...",
                            "url": "https://example.com/news1"
                        },
                        {
                            "title": f"Impact of {topic} on society",
                            "source": "Medical Journal Daily",
                            "summary": f"Study reveals significant data about {topic}...",
                            "url": "https://example.com/news2"
                        }
                    ]

                    st.success(f"✅ Found {len(demo_news)} news articles")

                    for i, article in enumerate(demo_news):
                        with st.expander(f"📰 {article['title']}"):
                            st.write(f"**Source:** {article['source']}")
                            st.write(f"**Summary:** {article['summary']}")

                            if st.button(f"💾 Save News", key=f"save_news_{i}"):
                                self.log_action("save_news", article)
                                st.success("News saved!")

        with col2:
            st.info("""
            **Trusted Sources:**
            - WHO
            - CDC
            - Medical journals
            - Government health agencies
            """)

            history = self.get_history()
            news_count = len(history[history['action'] == 'news_search']) if not history.empty else 0
            st.metric("News Searches", news_count)

    def ai_page(self):
        """Página de insights de IA"""
        st.title("🤖 AI Insights - Behavioral Analysis")

        history = self.get_history()

        if len(history) < 3:
            st.warning("⚠️ You need at least 3 interactions to generate AI insights.")
            st.info("Continue navigating the platform to accumulate data for analysis.")
            return

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Clustering Analysis")

            # Simple clustering simulation
            try:
                # Prepare features
                features = []
                for _, row in history.iterrows():
                    action_len = len(str(row['action']))
                    action_hash = hash(str(row['action'])) % 100
                    features.append([action_len, action_hash])

                if len(features) >= 3:
                    from sklearn.preprocessing import StandardScaler
                    scaler = StandardScaler()
                    features_scaled = scaler.fit_transform(features)

                    n_clusters = min(3, len(features))
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                    clusters = kmeans.fit_predict(features_scaled)

                    st.success(f"✅ Identified {n_clusters} behavior patterns")

                    # Visualize clusters
                    clusters_df = pd.DataFrame({
                        'interaction': range(len(clusters)),
                        'cluster': clusters
                    })

                    fig = px.scatter(
                        clusters_df,
                        x='interaction',
                        y='cluster',
                        color='cluster',
                        title="Behavioral Patterns"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    self.log_action("ai_clustering", {"n_clusters": n_clusters})

            except Exception:
                st.info("Clustering analysis temporarily unavailable")

        with col2:
            st.subheader("📈 Activity Analysis")

            if not history.empty:
                action_counts = history['action'].value_counts()

                fig = px.pie(
                    values=action_counts.values,
                    names=action_counts.index,
                    title="Activity Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)

        # Recommendations
        st.subheader("💡 Personalized Recommendations")

        if not history.empty:
            most_common = history['action'].value_counts().index[0]

            recommendations = {
                "covid_analysis": [
                    "📊 Explore data from other countries",
                    "📈 Analyze specific temporal trends",
                    "🔬 Search for related research"
                ],
                "research_search": [
                    "📰 Check related news",
                    "🤖 Use clustering for patterns",
                    "📋 Create a personalized dashboard"
                ]
            }

            user_recs = recommendations.get(most_common, [
                "🏠 Explore the home page",
                "📊 Start with COVID analysis",
                "🔬 Try scientific research"
            ])

            for rec in user_recs:
                st.write(f"• {rec}")

    def dashboard_page(self):
        """Dashboard personalizado"""
        st.title("📈 Personalized Dashboard")

        history = self.get_history()

        # Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Interactions", len(history))

        with col2:
            unique_actions = history['action'].nunique() if not history.empty else 0
            st.metric("Action Types", unique_actions)

        with col3:
            if not history.empty:
                session_start = pd.to_datetime(history['timestamp'].iloc[-1])
                session_now = pd.to_datetime(history['timestamp'].iloc[0])
                duration = (session_now - session_start).total_seconds() / 60
                st.metric("Duration (min)", f"{duration:.1f}")
            else:
                st.metric("Duration (min)", "0.0")

        with col4:
            current_page = st.session_state.page
            st.metric("Current Page", current_page)

        if not history.empty:
            # Timeline
            st.subheader("📊 Activity Timeline")

            history['timestamp'] = pd.to_datetime(history['timestamp'])
            timeline_data = history.sort_values('timestamp')

            fig = px.scatter(
                timeline_data,
                x='timestamp',
                y='action',
                color='action',
                title="Timeline of Interactions"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Action distribution
            st.subheader("📈 Action Distribution")

            action_counts = history['action'].value_counts()
            fig = px.bar(
                x=action_counts.values,
                y=action_counts.index,
                orientation='h',
                title="Actions by Frequency"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Recent activities table
            st.subheader("🗂️ Recent Activities")
            st.dataframe(
                history[['action', 'timestamp']].head(10),
                use_container_width=True
            )

    def history_page(self):
        """Página de histórico"""
        st.title("🗂️ Complete Session History")

        history = self.get_history()

        if history.empty:
            st.info("No interactions recorded in this session.")
            return

        # Filters
        col1, col2 = st.columns(2)

        with col1:
            filter_action = st.selectbox(
                "Filter by action:",
                ["All"] + list(history['action'].unique()),
                key="filter_action"
            )

        with col2:
            show_data = st.checkbox("Show detailed data", key="show_data")

        # Apply filters
        filtered_history = history.copy()

        if filter_action != "All":
            filtered_history = filtered_history[filtered_history['action'] == filter_action]

        st.write(f"📋 Showing {len(filtered_history)} of {len(history)} interactions")

        # Display history
        for idx, row in filtered_history.iterrows():
            with st.expander(f"🔍 {row['action']} - {row['timestamp']}"):
                st.write(f"**Action:** {row['action']}")
                st.write(f"**Timestamp:** {row['timestamp']}")

                if show_data and row['data']:
                    try:
                        data = json.loads(row['data'])
                        st.write(f"**Data:** {data}")
                    except:
                        st.write(f"**Data:** {row['data']}")

        # Export
        if st.button("💾 Export History", key="export_btn"):
            csv_data = filtered_history.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=f"saudeja_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

    def run(self):
        """Executa a aplicação"""
        try:
            current_page = self.navigation()

            if current_page == 'home':
                self.home_page()
            elif current_page == 'covid':
                self.covid_page()
            elif current_page == 'research':
                self.research_page()
            elif current_page == 'news':
                self.news_page()
            elif current_page == 'ai':
                self.ai_page()
            elif current_page == 'dashboard':
                self.dashboard_page()
            elif current_page == 'history':
                self.history_page()

        except Exception as e:
            st.error(f"Application error: {e}")
            st.info("Please refresh the page to try again.")

# Execute the application
if __name__ == "__main__":
    app = SaudeJaApp()
    app.run()
