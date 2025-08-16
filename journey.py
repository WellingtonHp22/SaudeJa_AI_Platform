import streamlit as st
import json
from datetime import datetime
from database import get_database_manager
from data_sources import get_covid_manager, get_pubmed_manager, get_patent_manager
from analytics import get_analytics_engine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class InnovationJourney:
    """Orquestrador da jornada interativa de inovação"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
        self.covid_manager = get_covid_manager()
        self.pubmed_manager = get_pubmed_manager()
        self.patent_manager = get_patent_manager()
        self.analytics_engine = get_analytics_engine()
        
        # Inicializar estado da jornada
        if 'journey_state' not in st.session_state:
            st.session_state.journey_state = {
                'current_step': 0,
                'topic': None,
                'data_collected': {},
                'insights_generated': {},
                'user_preferences': {}
            }
    
    def start_journey(self, topic):
        """Inicia uma nova jornada de inovação"""
        st.session_state.journey_state = {
            'current_step': 1,
            'topic': topic,
            'data_collected': {},
            'insights_generated': {},
            'user_preferences': {},
            'started_at': datetime.now().isoformat()
        }
        
        # Registrar início da jornada
        self.db_manager.log_interaction(
            user_query=topic,
            interaction_type="journey_start",
            response_data={"topic": topic, "timestamp": datetime.now().isoformat()}
        )
        
        return True
    
    def execute_step(self, step_number):
        """Executa um passo específico da jornada"""
        journey_steps = {
            1: self._step_1_topic_analysis,
            2: self._step_2_data_collection,
            3: self._step_3_research_analysis,
            4: self._step_4_patent_landscape,
            5: self._step_5_ai_insights,
            6: self._step_6_recommendations,
            7: self._step_7_action_plan
        }
        
        if step_number in journey_steps:
            return journey_steps[step_number]()
        else:
            st.error(f"Passo {step_number} não encontrado")
            return False
    
    def _step_1_topic_analysis(self):
        """Passo 1: Análise inicial do tópico"""
        st.subheader("🎯 Passo 1: Análise do Tópico")
        
        topic = st.session_state.journey_state['topic']
        
        with st.spinner("Analisando tópico..."):
            # Análise básica do tópico
            analysis = {
                'topic_category': self._categorize_topic(topic),
                'complexity_level': self._assess_complexity(topic),
                'market_relevance': self._assess_market_relevance(topic),
                'research_maturity': self._assess_research_maturity(topic)
            }
            
            st.session_state.journey_state['data_collected']['topic_analysis'] = analysis
        
        # Mostrar resultados
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Categoria", analysis['topic_category'])
        with col2:
            st.metric("Complexidade", analysis['complexity_level'])
        with col3:
            st.metric("Relevância de Mercado", f"{analysis['market_relevance']}/10")
        with col4:
            st.metric("Maturidade da Pesquisa", analysis['research_maturity'])
        
        # Perguntas de refinamento
        st.markdown("### 🎨 Personalize sua análise:")
        
        focus_area = st.selectbox(
            "Qual área você quer focar?",
            ["Pesquisa Básica", "Desenvolvimento Clínico", "Comercialização", "Todas"]
        )
        
        timeline = st.selectbox(
            "Qual seu horizonte de tempo?",
            ["Curto prazo (1-2 anos)", "Médio prazo (3-5 anos)", "Longo prazo (5+ anos)"]
        )
        
        st.session_state.journey_state['user_preferences'] = {
            'focus_area': focus_area,
            'timeline': timeline
        }
        
        return True
    
    def _step_2_data_collection(self):
        """Passo 2: Coleta de dados"""
        st.subheader("📊 Passo 2: Coleta de Dados")
        
        topic = st.session_state.journey_state['topic']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🦠 Dados COVID-19")
            if 'covid' in topic.lower() or st.button("Coletar dados COVID"):
                with st.spinner("Coletando dados COVID..."):
                    covid_data = self.covid_manager.get_trending_states()
                    st.session_state.journey_state['data_collected']['covid'] = covid_data
                    st.success(f"✅ {len(covid_data)} registros coletados")
        
        with col2:
            st.markdown("#### 📚 Literatura Científica")
            if st.button("Buscar artigos científicos"):
                with st.spinner("Buscando artigos..."):
                    articles = self.pubmed_manager.search_articles(topic, 20)
                    st.session_state.journey_state['data_collected']['articles'] = articles
                    st.success(f"✅ {len(articles)} artigos encontrados")
        
        # Mostrar preview dos dados coletados
        if 'articles' in st.session_state.journey_state['data_collected']:
            st.markdown("#### 📋 Preview dos Artigos:")
            articles = st.session_state.journey_state['data_collected']['articles']
            
            for i, article in enumerate(articles[:3]):
                with st.expander(f"📄 {article['title']}"):
                    st.write(f"**Autores:** {', '.join(article['authors'])}")
                    st.write(f"**Revista:** {article['journal']}")
                    st.write(f"**Ano:** {article['year']}")
                    st.write(f"**Resumo:** {article['abstract']}")
        
        return True
    
    def _step_3_research_analysis(self):
        """Passo 3: Análise de pesquisa"""
        st.subheader("🔬 Passo 3: Análise de Pesquisa")
        
        topic = st.session_state.journey_state['topic']
        data_collected = st.session_state.journey_state['data_collected']
        
        if 'articles' in data_collected:
            with st.spinner("Analisando tendências de pesquisa..."):
                research_trends = self.analytics_engine.analyze_research_trends(
                    topic, data_collected['articles']
                )
                
                st.session_state.journey_state['insights_generated']['research_trends'] = research_trends
            
            # Visualizar tendências
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Total de Publicações", 
                    research_trends['total_publications'],
                    f"{research_trends['growth_rate']:.1f}%"
                )
                
                st.markdown("#### 🔬 Principais Pesquisadores:")
                for researcher in research_trends['key_researchers']:
                    st.write(f"• {researcher}")
            
            with col2:
                st.markdown("#### 🌱 Subtópicos Emergentes:")
                for subtopic in research_trends['emerging_subtopics']:
                    st.write(f"• {subtopic}")
            
            # Gráfico de timeline
            timeline_fig = self.analytics_engine._create_timeline_chart(research_trends)
            st.plotly_chart(timeline_fig, use_container_width=True)
        
        else:
            st.warning("⚠️ Nenhum dado de pesquisa coletado ainda. Volte ao Passo 2.")
        
        return True
    
    def _step_4_patent_landscape(self):
        """Passo 4: Panorama de patentes"""
        st.subheader("⚗️ Passo 4: Panorama de Patentes")
        
        topic = st.session_state.journey_state['topic']
        
        if st.button("Analisar Patentes"):
            with st.spinner("Analisando panorama de patentes..."):
                patents = self.patent_manager.search_patents(topic, 50)
                patent_analysis = self.patent_manager.analyze_patent_landscape(topic)
                
                st.session_state.journey_state['data_collected']['patents'] = patents
                st.session_state.journey_state['insights_generated']['patent_analysis'] = patent_analysis
            
            # Mostrar análise
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Patentes", patent_analysis['total_patents'])
            with col2:
                st.metric("Patentes Ativas", patent_analysis['active_patents'])
            with col3:
                maturity = patent_analysis.get('technology_maturity', 'N/A')
                st.metric("Maturidade Tecnológica", maturity)
            
            # Principais detentores
            st.markdown("#### 🏢 Principais Detentores de Patentes:")
            if patent_analysis['top_assignees']:
                assignees_df = pd.DataFrame(
                    list(patent_analysis['top_assignees'].items()),
                    columns=['Empresa', 'Patentes']
                )
                
                fig = px.bar(
                    assignees_df.head(10), 
                    x='Patentes', 
                    y='Empresa',
                    orientation='h',
                    title="Top 10 Detentores de Patentes"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Gaps de inovação
            st.markdown("#### 💡 Oportunidades de Inovação:")
            for gap in patent_analysis['technology_gaps']:
                st.write(f"🎯 {gap}")
        
        return True
    
    def _step_5_ai_insights(self):
        """Passo 5: Insights de IA"""
        st.subheader("🤖 Passo 5: Insights de Inteligência Artificial")
        
        topic = st.session_state.journey_state['topic']
        data_collected = st.session_state.journey_state['data_collected']
        
        if st.button("Gerar Insights com IA"):
            with st.spinner("Processando com IA..."):
                # Gerar score de inovação
                innovation_score = self.analytics_engine.generate_innovation_score(
                    topic,
                    data_collected.get('articles', []),
                    data_collected.get('patents', [])
                )
                
                st.session_state.journey_state['insights_generated']['innovation_score'] = innovation_score
            
            # Mostrar score
            score = innovation_score['total_score']
            level = innovation_score['level']
            
            st.markdown(f"### 🎯 Score de Inovação: {score:.1f}/100")
            st.markdown(f"### {level}")
            
            # Componentes do score
            col1, col2, col3, col4 = st.columns(4)
            components = innovation_score['components']
            
            with col1:
                st.metric("Volume de Pesquisa", f"{components['research_volume']:.1f}/25")
            with col2:
                st.metric("Crescimento", f"{components['research_growth']:.1f}/25")
            with col3:
                st.metric("Densidade de Patentes", f"{components['patent_density']:.1f}/25")
            with col4:
                st.metric("Potencial de Mercado", f"{components['market_potential']:.1f}/25")
            
            # Recomendações
            st.markdown("#### 💡 Recomendações da IA:")
            for rec in innovation_score['recommendations']:
                st.write(f"• {rec}")
            
            # Visualização radar
            categories = list(components.keys())
            values = list(components.values())
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Score de Inovação'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 25]
                    )),
                showlegend=True,
                title="Radar de Componentes do Score"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        return True
    
    def _step_6_recommendations(self):
        """Passo 6: Recomendações finais"""
        st.subheader("🎯 Passo 6: Recomendações Estratégicas")
        
        insights = st.session_state.journey_state.get('insights_generated', {})
        
        if insights:
            # Consolidar todas as recomendações
            all_recommendations = []
            
            if 'innovation_score' in insights:
                all_recommendations.extend(insights['innovation_score']['recommendations'])
            
            if 'patent_analysis' in insights:
                gaps = insights['patent_analysis'].get('technology_gaps', [])
                for gap in gaps:
                    all_recommendations.append(f"🎯 Explorar: {gap}")
            
            # Priorizar recomendações
            priority_recommendations = self._prioritize_recommendations(all_recommendations)
            
            st.markdown("#### 🎯 Recomendações Priorizadas:")
            for i, rec in enumerate(priority_recommendations[:5], 1):
                st.markdown(f"**{i}.** {rec}")
            
            # Matriz de priorização
            st.markdown("#### 📊 Matriz de Priorização:")
            
            fig = px.scatter(
                x=[0.8, 0.6, 0.7, 0.9, 0.5],
                y=[0.7, 0.8, 0.6, 0.8, 0.4],
                text=['Rec 1', 'Rec 2', 'Rec 3', 'Rec 4', 'Rec 5'],
                labels={'x': 'Viabilidade', 'y': 'Impacto'},
                title="Matriz Impacto vs Viabilidade"
            )
            
            fig.add_hline(y=0.5, line_dash="dash", line_color="gray")
            fig.add_vline(x=0.5, line_dash="dash", line_color="gray")
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.warning("⚠️ Execute os passos anteriores para gerar recomendações.")
        
        return True
    
    def _step_7_action_plan(self):
        """Passo 7: Plano de ação"""
        st.subheader("📋 Passo 7: Plano de Ação")
        
        topic = st.session_state.journey_state['topic']
        user_prefs = st.session_state.journey_state.get('user_preferences', {})
        
        # Gerar plano de ação baseado no timeline
        timeline = user_prefs.get('timeline', 'Médio prazo (3-5 anos)')
        
        action_plans = {
            'Curto prazo (1-2 anos)': [
                "📚 Revisar literatura científica atual",
                "🤝 Identificar parceiros de pesquisa",
                "💰 Buscar financiamento inicial",
                "🔬 Desenvolver prova de conceito"
            ],
            'Médio prazo (3-5 anos)': [
                "🧪 Realizar estudos pré-clínicos",
                "📋 Submeter pedidos de patente",
                "🏢 Estabelecer parcerias industriais",
                "🎯 Definir estratégia de comercialização"
            ],
            'Longo prazo (5+ anos)': [
                "🏥 Conduzir ensaios clínicos",
                "📊 Análise de mercado detalhada",
                "🚀 Lançamento comercial",
                "🌍 Expansão internacional"
            ]
        }
        
        st.markdown(f"#### 📅 Plano para {timeline}:")
        plan = action_plans.get(timeline, action_plans['Médio prazo (3-5 anos)'])
        
        for i, action in enumerate(plan, 1):
            st.markdown(f"**{i}.** {action}")
        
        # Timeline visual
        fig = go.Figure()
        
        months = list(range(1, 25))
        milestones = [6, 12, 18, 24]
        
        fig.add_trace(go.Scatter(
            x=months,
            y=[1]*len(months),
            mode='lines',
            name='Timeline',
            line=dict(color='lightblue', width=10)
        ))
        
        fig.add_trace(go.Scatter(
            x=milestones,
            y=[1]*len(milestones),
            mode='markers+text',
            text=['Marco 1', 'Marco 2', 'Marco 3', 'Marco 4'],
            textposition="top center",
            marker=dict(size=15, color='red'),
            name='Marcos'
        ))
        
        fig.update_layout(
            title='Timeline de Execução',
            xaxis_title='Meses',
            yaxis=dict(showticklabels=False),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Botão para finalizar jornada
        if st.button("🎯 Finalizar Jornada", type="primary"):
            self._finalize_journey()
        
        return True
    
    def _finalize_journey(self):
        """Finaliza a jornada e gera relatório"""
        topic = st.session_state.journey_state['topic']
        
        # Gerar relatório final
        report = self.analytics_engine.export_analysis_report(
            topic,
            st.session_state.journey_state
        )
        
        # Registrar conclusão
        self.db_manager.log_interaction(
            user_query=topic,
            interaction_type="journey_complete",
            response_data=report
        )
        
        st.success("🎉 Jornada concluída com sucesso!")
        st.balloons()
        
        # Oferecer download do relatório
        st.download_button(
            label="📄 Baixar Relatório Completo",
            data=json.dumps(report, indent=2, ensure_ascii=False),
            file_name=f"relatorio_inovacao_{topic.replace(' ', '_')}.json",
            mime="application/json"
        )
    
    # Métodos auxiliares
    def _categorize_topic(self, topic):
        """Categoriza o tópico de pesquisa"""
        categories = {
            'diabetes': 'Endocrinologia',
            'cancer': 'Oncologia', 
            'covid': 'Infectologia',
            'heart': 'Cardiologia',
            'brain': 'Neurologia'
        }
        
        for key, category in categories.items():
            if key in topic.lower():
                return category
        
        return 'Medicina Geral'
    
    def _assess_complexity(self, topic):
        """Avalia complexidade do tópico"""
        complexity_indicators = ['ai', 'nano', 'genetic', 'quantum']
        
        for indicator in complexity_indicators:
            if indicator in topic.lower():
                return 'Alta'
        
        return 'Moderada'
    
    def _assess_market_relevance(self, topic):
        """Avalia relevância de mercado"""
        return round(7 + (hash(topic) % 4) * 0.5, 1)
    
    def _assess_research_maturity(self, topic):
        """Avalia maturidade da pesquisa"""
        maturity_levels = ['Emergente', 'Desenvolvimento', 'Madura']
        return maturity_levels[hash(topic) % 3]
    
    def _prioritize_recommendations(self, recommendations):
        """Prioriza recomendações"""
        # Simples ordenação aleatória para demonstração
        import random
        random.shuffle(recommendations)
        return recommendations

@st.cache_resource
def get_innovation_journey():
    return InnovationJourney()
