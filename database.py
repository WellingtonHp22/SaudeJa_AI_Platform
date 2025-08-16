import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json
import hashlib

# Importação condicional para evitar erros quando executado diretamente
try:
    from config import Config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    # Configurações fallback
    class FallbackConfig:
        DATABASE_URL = 'sqlite:///saudeja_local.db'
    Config = FallbackConfig()

Base = declarative_base()

class UserInteraction(Base):
    __tablename__ = 'user_interactions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False)
    user_query = Column(Text)
    interaction_type = Column(String(100))
    response_data = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_feedback = Column(Integer)  # 1-5 rating
    
class ResearchData(Base):
    __tablename__ = 'research_data'
    
    id = Column(Integer, primary_key=True)
    topic = Column(String(255))
    data_source = Column(String(100))
    content = Column(Text)
    relevance_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.Session = None
        self.initialize_database()
    
    def initialize_database(self):
        """Inicializa a conexão com o banco de dados"""
        try:
            # Para desenvolvimento local, usa SQLite se PostgreSQL não estiver disponível
            if (hasattr(Config, 'DATABASE_URL') and 
                hasattr(Config.DATABASE_URL, 'startswith') and 
                Config.DATABASE_URL.startswith('postgresql://')):
                self.engine = create_engine(Config.DATABASE_URL)
                print("[OK] Conectado ao PostgreSQL")
            else:
                # Fallback para SQLite local
                self.engine = create_engine('sqlite:///saudeja_local.db')
                print("[OK] Conectado ao SQLite local")
            
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            
            return True
        except Exception as e:
            print(f"[ERRO] Erro ao conectar com o banco de dados: {e}")
            # Criar tabelas em memória como fallback
            self.engine = create_engine('sqlite:///:memory:')
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            print("[FALLBACK] Usando banco em memoria")
            return False
    
    def get_session_id(self):
        """Gera um ID único para a sessão do usuário"""
        # Se estiver no contexto do Streamlit
        try:
            import streamlit as st
            if 'session_id' not in st.session_state:
                # Cria hash baseado no timestamp e dados da sessão
                session_data = f"{datetime.now().isoformat()}_{st.session_state}"
                st.session_state.session_id = hashlib.md5(session_data.encode()).hexdigest()[:16]
            return st.session_state.session_id
        except:
            # Se não estiver no Streamlit, gera ID baseado no timestamp
            session_data = f"{datetime.now().isoformat()}_standalone"
            return hashlib.md5(session_data.encode()).hexdigest()[:16]
    
    def log_interaction(self, user_query, interaction_type, response_data, user_feedback=None):
        """Registra interação do usuário no banco de dados"""
        try:
            session = self.Session()
            interaction = UserInteraction(
                session_id=self.get_session_id(),
                user_query=user_query,
                interaction_type=interaction_type,
                response_data=json.dumps(response_data) if isinstance(response_data, dict) else str(response_data),
                user_feedback=user_feedback
            )
            session.add(interaction)
            session.commit()
            session.close()
            print(f"[OK] Interação registrada: {interaction_type}")
            return True
        except Exception as e:
            print(f"[ERRO] Erro ao salvar interação: {e}")
            return False
    
    def save_research_data(self, topic, data_source, content, relevance_score=0.0):
        """Salva dados de pesquisa no banco"""
        try:
            session = self.Session()
            research = ResearchData(
                topic=topic,
                data_source=data_source,
                content=content,
                relevance_score=relevance_score
            )
            session.add(research)
            session.commit()
            session.close()
            print(f"[OK] Dados de pesquisa salvos: {topic}")
            return True
        except Exception as e:
            print(f"[ERRO] Erro ao salvar dados de pesquisa: {e}")
            return False
    
    def get_user_history(self, session_id=None):
        """Recupera histórico de interações do usuário"""
        try:
            session = self.Session()
            if session_id is None:
                session_id = self.get_session_id()
            
            interactions = session.query(UserInteraction)\
                .filter(UserInteraction.session_id == session_id)\
                .order_by(UserInteraction.timestamp.desc())\
                .limit(50).all()
            
            session.close()
            print(f"[OK] Histórico recuperado: {len(interactions)} interações")
            return interactions
        except Exception as e:
            print(f"[ERRO] Erro ao recuperar histórico: {e}")
            return []
    
    def get_research_by_topic(self, topic):
        """Recupera dados de pesquisa por tópico"""
        try:
            session = self.Session()
            research_data = session.query(ResearchData)\
                .filter(ResearchData.topic.like(f'%{topic}%'))\
                .order_by(ResearchData.relevance_score.desc())\
                .limit(20).all()
            
            session.close()
            print(f"[OK] Dados de pesquisa recuperados: {len(research_data)} registros")
            return research_data
        except Exception as e:
            print(f"[ERRO] Erro ao recuperar dados de pesquisa: {e}")
            return []
    
    def get_analytics(self):
        """Recupera dados para analytics"""
        try:
            session = self.Session()
            
            # Contagem de interações por tipo
            interaction_counts = session.query(
                UserInteraction.interaction_type,
                session.query(UserInteraction).filter(
                    UserInteraction.interaction_type == UserInteraction.interaction_type
                ).count()
            ).distinct().all()
            
            # Total de usuários únicos (sessões)
            unique_sessions = session.query(UserInteraction.session_id).distinct().count()
            
            # Total de interações
            total_interactions = session.query(UserInteraction).count()
            
            session.close()
            
            return {
                'interaction_counts': dict(interaction_counts) if interaction_counts else {},
                'unique_sessions': unique_sessions,
                'total_interactions': total_interactions
            }
        except Exception as e:
            print(f"[ERRO] Erro ao recuperar analytics: {e}")
            return {
                'interaction_counts': {},
                'unique_sessions': 0,
                'total_interactions': 0
            }

def test_database():
    """Função para testar o banco de dados quando executado diretamente"""
    print("TESTANDO DATABASE...")
    print("=" * 50)
    
    # Inicializar database manager
    db = DatabaseManager()
    
    # Testar log de interação
    print("\n[TESTE] Testando log de interacao:")
    success = db.log_interaction(
        user_query="teste diabetes",
        interaction_type="test_search",
        response_data={"test": "data", "results": 5}
    )
    print(f"Log de interacao: {'Sucesso' if success else 'Falhou'}")
    
    # Testar salvamento de dados de pesquisa
    print("\n[TESTE] Testando salvamento de dados de pesquisa:")
    success = db.save_research_data(
        topic="diabetes treatment",
        data_source="TEST_SOURCE",
        content='{"test": "research data"}',
        relevance_score=0.85
    )
    print(f"Salvamento de pesquisa: {'Sucesso' if success else 'Falhou'}")
    
    # Testar recuperação de histórico
    print("\n[TESTE] Testando recuperacao de historico:")
    history = db.get_user_history()
    print(f"Historico recuperado: {len(history)} interacoes")
    
    # Testar analytics
    print("\n[TESTE] Testando analytics:")
    analytics = db.get_analytics()
    print(f"Analytics: {analytics}")
    
    # Testar busca por tópico
    print("\n[TESTE] Testando busca por topico:")
    research = db.get_research_by_topic("diabetes")
    print(f"Dados encontrados: {len(research)} registros")
    
    print("\n[CONCLUIDO] TODOS OS TESTES DE DATABASE CONCLUIDOS!")

# Instância global do gerenciador de banco (para Streamlit)
try:
    import streamlit as st
    @st.cache_resource
    def get_database_manager():
        return DatabaseManager()
except ImportError:
    # Para execução standalone
    def get_database_manager():
        return DatabaseManager()

# Executar testes se chamado diretamente
if __name__ == "__main__":
    test_database()
