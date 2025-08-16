import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configurações do banco de dados - Suporte completo conforme requisitos
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///saudeja.db')
    
    # Opções de banco suportadas (conforme texto):
    # - Aiven PostgreSQL: postgresql://user:pass@host:port/db
    # - Supabase: postgresql://postgres:pass@host:port/postgres
    # - Neon: postgresql://user:pass@host:port/db
    # - MongoDB Atlas: mongodb+srv://user:pass@cluster/db
    # - Firebase: configurado via GOOGLE_APPLICATION_CREDENTIALS

    # APIs conforme requisitos do texto
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Free-tier para resumos
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')  # Patents API
    PUBMED_API_KEY = os.getenv('PUBMED_API_KEY')  # PubMed API

    # BigQuery para estudantes (conforme texto)
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    # Configurações da aplicação
    APP_NAME = os.getenv('APP_NAME', 'SaudeJá - Jornada de Inovação')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Fontes de dados conforme requisitos
    COVID_DATA_URL = "https://github.com/nytimes/covid-19-data"  # Fonte principal
    PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    PATENTS_API_URL = "https://www.patentsview.org/api"

    # Configurações de segurança e LGPD
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    ANONYMIZE_DATA = os.getenv('ANONYMIZE_DATA', 'True').lower() == 'true'
    DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', '365'))

    # Rate limiting para APIs (ética conforme texto)
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', '100'))  # req/hour
    CRAWL_DELAY = float(os.getenv('CRAWL_DELAY', '1.0'))  # segundos

    @staticmethod
    def validate_config():
        """Valida configurações essenciais conforme requisitos"""
        required_vars = ['DATABASE_URL']
        missing_vars = [var for var in required_vars if not getattr(Config, var)]
        
        if missing_vars:
            print(f"⚠️ Variáveis obrigatórias faltando: {missing_vars}")
            print("📝 Configure no arquivo .env ou variáveis de ambiente")

        # Validações específicas do texto
        db_url = Config.DATABASE_URL
        if db_url.startswith('postgresql://'):
            print("✅ PostgreSQL configurado (Aiven/Supabase/Neon)")
        elif db_url.startswith('mongodb://'):
            print("✅ MongoDB configurado (Atlas)")
        elif db_url.startswith('sqlite://'):
            print("⚠️ SQLite local - considere PostgreSQL para produção")

        return len(missing_vars) == 0

    @staticmethod
    def get_database_type():
        """Retorna tipo do banco configurado"""
        url = Config.DATABASE_URL
        if url.startswith('postgresql://'):
            return 'postgresql'
        elif url.startswith('mongodb://'):
            return 'mongodb'
        elif url.startswith('sqlite://'):
            return 'sqlite'
        else:
            return 'unknown'
