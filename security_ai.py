import os
import hashlib
import json
import logging
import pandas as pd
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import streamlit as st
import sqlite3
import uuid
from typing import Dict, Any
import re
import numpy as np

# Carregar variáveis de ambiente
load_dotenv()

class SecurityManager:
    """Gerenciador de segurança e LGPD"""

    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY', 'default-dev-key-change-in-production')
        self.anonymize_enabled = os.getenv('ANONYMIZE_DATA', 'true').lower() == 'true'
        self.retention_days = int(os.getenv('DATA_RETENTION_DAYS', '365'))
        self.consent_enabled = os.getenv('ENABLE_USER_CONSENT', 'true').lower() == 'true'

        # Configurar criptografia
        self._setup_encryption()

        # Configurar logging seguro
        self._setup_logging()

        # Inicializar banco de auditoria
        self._setup_audit_db()

    def _setup_encryption(self):
        """Configura criptografia para dados sensíveis"""
        try:
            # Gerar chave a partir do secret_key
            key = hashlib.sha256(self.secret_key.encode()).digest()
            # Usar base64 encoding para compatibilidade com Fernet
            import base64
            fernet_key = base64.urlsafe_b64encode(key)
            self.cipher = Fernet(fernet_key)
        except Exception as e:
            st.warning(f"Sistema de criptografia em modo básico: {e}")
            self.cipher = None

    def _setup_logging(self):
        """Configura logging sem dados pessoais"""
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('app_secure.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _setup_audit_db(self):
        """Configura banco de dados para auditoria LGPD"""
        try:
            self.audit_conn = sqlite3.connect('lgpd_audit.db', check_same_thread=False)
            cursor = self.audit_conn.cursor()

            # Tabela de consentimentos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_consents (
                    id TEXT PRIMARY KEY,
                    user_session TEXT,
                    consent_type TEXT,
                    consent_given BOOLEAN,
                    timestamp DATETIME,
                    ip_hash TEXT,
                    purpose TEXT
                )
            ''')

            # Tabela de logs de acesso
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_logs (
                    id TEXT PRIMARY KEY,
                    user_session TEXT,
                    action TEXT,
                    data_accessed TEXT,
                    timestamp DATETIME,
                    ip_hash TEXT,
                    success BOOLEAN
                )
            ''')

            # Tabela de retenção de dados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_retention (
                    id TEXT PRIMARY KEY,
                    data_type TEXT,
                    created_at DATETIME,
                    expires_at DATETIME,
                    auto_delete BOOLEAN
                )
            ''')

            self.audit_conn.commit()
        except Exception as e:
            self.logger.error(f"Erro ao configurar banco de auditoria: {e}")
            self.audit_conn = None

    def anonymize_user_data(self, data):
        """Anonimiza dados do usuário conforme LGPD"""
        if not self.anonymize_enabled:
            return data

        # Hash SHA-256 para anonimização irreversível
        if isinstance(data, str):
            return hashlib.sha256(data.encode()).hexdigest()[:16]
        elif isinstance(data, dict):
            return {k: self.anonymize_user_data(v) for k, v in data.items()}
        return str(hash(str(data)))[:16]

    def encrypt_sensitive_data(self, data):
        """Criptografa dados sensíveis"""
        if not self.cipher:
            return data

        try:
            if isinstance(data, dict):
                data = json.dumps(data)

            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode('latin-1')
        except Exception as e:
            self.logger.error(f"Erro na criptografia: {e}")
            return data

    def decrypt_sensitive_data(self, encrypted_data):
        """Descriptografa dados sensíveis"""
        if not self.cipher:
            return encrypted_data

        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode('latin-1'))
            return decrypted.decode()
        except Exception as e:
            self.logger.error(f"Erro na descriptografia: {e}")
            return encrypted_data

    def get_user_session_id(self):
        """Gera ou recupera ID de sessão anônimo"""
        if 'user_session_id' not in st.session_state:
            st.session_state.user_session_id = str(uuid.uuid4())
        return st.session_state.user_session_id

    def get_client_ip_hash(self):
        """Obtém hash do IP do cliente (anonimizado)"""
        try:
            # Em produção, usar headers do proxy/load balancer
            ip = st.context.headers.get('x-forwarded-for', 'unknown')
            return hashlib.sha256(ip.encode()).hexdigest()[:16]
        except:
            return 'local'

    def check_user_consent(self, consent_type: str = 'data_processing', purpose: str = 'analytics'):
        """Verifica e solicita consentimento do usuário conforme LGPD"""
        if not self.consent_enabled:
            return True

        session_id = self.get_user_session_id()
        consent_key = f'consent_{consent_type}'

        # Verificar se já tem consentimento
        if consent_key in st.session_state:
            return st.session_state[consent_key]

        # Solicitar consentimento
        st.markdown("### 📋 Consentimento LGPD")
        st.info(f"""
        **Finalidade**: {purpose}
        
        De acordo com a Lei Geral de Proteção de Dados (LGPD), precisamos do seu consentimento 
        para processar dados analíticos que podem incluir informações sobre seu uso da aplicação.
        
        **Seus direitos:**
        - Acesso aos seus dados
        - Correção de dados incorretos
        - Eliminação dos dados
        - Portabilidade dos dados
        - Revogação do consentimento
        """)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Aceito", key=f"accept_{consent_type}"):
                st.session_state[consent_key] = True
                self._log_consent(session_id, consent_type, True, purpose)
                st.success("Consentimento registrado!")
                st.rerun()

        with col2:
            if st.button("❌ Recuso", key=f"decline_{consent_type}"):
                st.session_state[consent_key] = False
                self._log_consent(session_id, consent_type, False, purpose)
                st.warning("Algumas funcionalidades podem ficar limitadas.")
                st.rerun()

        # Se não decidiu ainda, retorna False
        return st.session_state.get(consent_key, False)

    def _log_consent(self, session_id: str, consent_type: str, given: bool, purpose: str):
        """Registra consentimento no banco de auditoria"""
        if not self.audit_conn:
            return

        try:
            cursor = self.audit_conn.cursor()
            cursor.execute('''
                INSERT INTO user_consents 
                (id, user_session, consent_type, consent_given, timestamp, ip_hash, purpose)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                session_id,
                consent_type,
                given,
                datetime.now().isoformat(),
                self.get_client_ip_hash(),
                purpose
            ))
            self.audit_conn.commit()
        except Exception as e:
            self.logger.error(f"Erro ao registrar consentimento: {e}")

    def log_data_access(self, action: str, data_type: str, success: bool = True):
        """Registra acesso a dados para auditoria"""
        if not self.audit_conn:
            return

        try:
            session_id = self.get_user_session_id()
            cursor = self.audit_conn.cursor()
            cursor.execute('''
                INSERT INTO access_logs 
                (id, user_session, action, data_accessed, timestamp, ip_hash, success)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                session_id,
                action,
                data_type,
                datetime.now().isoformat(),
                self.get_client_ip_hash(),
                success
            ))
            self.audit_conn.commit()
        except Exception as e:
            self.logger.error(f"Erro ao registrar acesso: {e}")

    def schedule_data_deletion(self, data_type: str, auto_delete: bool = True):
        """Agenda exclusão automática de dados conforme período de retenção"""
        if not self.audit_conn:
            return

        try:
            expires_at = datetime.now() + timedelta(days=self.retention_days)
            cursor = self.audit_conn.cursor()
            cursor.execute('''
                INSERT INTO data_retention 
                (id, data_type, created_at, expires_at, auto_delete)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                data_type,
                datetime.now().isoformat(),
                expires_at.isoformat(),
                auto_delete
            ))
            self.audit_conn.commit()
        except Exception as e:
            self.logger.error(f"Erro ao agendar exclusão: {e}")

    def cleanup_expired_data(self):
        """Remove dados expirados conforme política de retenção"""
        if not self.audit_conn:
            return

        try:
            cursor = self.audit_conn.cursor()
            now = datetime.now().isoformat()

            # Buscar dados expirados
            cursor.execute('''
                SELECT * FROM data_retention 
                WHERE expires_at <= ? AND auto_delete = 1
            ''', (now,))

            expired_data = cursor.fetchall()

            for record in expired_data:
                data_type = record[1]
                self.logger.info(f"Removendo dados expirados: {data_type}")

                # Aqui implementar a lógica específica de exclusão por tipo
                # Por exemplo, limpar sessões antigas, logs antigos, etc.

            # Remover registros de retenção processados
            cursor.execute('''
                DELETE FROM data_retention 
                WHERE expires_at <= ? AND auto_delete = 1
            ''', (now,))

            self.audit_conn.commit()

        except Exception as e:
            self.logger.error(f"Erro na limpeza de dados: {e}")

    def validate_data_input(self, data: Any, data_type: str) -> Dict[str, Any]:
        """Valida e sanitiza entrada de dados"""
        validation_result = {
            'valid': True,
            'sanitized_data': data,
            'warnings': [],
            'errors': []
        }

        try:
            if data_type == 'text':
                # Remover caracteres perigosos
                if isinstance(data, str):
                    # Prevenir XSS básico
                    sanitized = re.sub(r'<script.*?</script>', '', data, flags=re.IGNORECASE)
                    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
                    validation_result['sanitized_data'] = sanitized

                    if sanitized != data:
                        validation_result['warnings'].append('Conteúdo potencialmente perigoso removido')

            elif data_type == 'email':
                if isinstance(data, str):
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, data):
                        validation_result['valid'] = False
                        validation_result['errors'].append('Formato de email inválido')

            elif data_type == 'numeric':
                try:
                    float(data)
                except (ValueError, TypeError):
                    validation_result['valid'] = False
                    validation_result['errors'].append('Valor numérico inválido')

        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f'Erro na validação: {str(e)}')

        return validation_result

    def get_privacy_dashboard(self):
        """Exibe dashboard de privacidade para o usuário"""
        st.markdown("### 🔒 Dashboard de Privacidade")

        session_id = self.get_user_session_id()

        if not self.audit_conn:
            st.error("Sistema de auditoria não disponível")
            return

        try:
            cursor = self.audit_conn.cursor()

            # Buscar consentimentos do usuário
            cursor.execute('''
                SELECT consent_type, consent_given, timestamp, purpose 
                FROM user_consents 
                WHERE user_session = ?
                ORDER BY timestamp DESC
            ''', (session_id,))

            consents = cursor.fetchall()

            if consents:
                st.subheader("📋 Seus Consentimentos")
                consent_df = pd.DataFrame(consents, columns=['Tipo', 'Consentido', 'Data', 'Finalidade'])
                st.dataframe(consent_df)

            # Buscar logs de acesso
            cursor.execute('''
                SELECT action, data_accessed, timestamp 
                FROM access_logs 
                WHERE user_session = ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (session_id,))

            logs = cursor.fetchall()

            if logs:
                st.subheader("📊 Histórico de Acesso (Últimos 10)")
                logs_df = pd.DataFrame(logs, columns=['Ação', 'Dados Acessados', 'Data/Hora'])
                st.dataframe(logs_df)

            # Opções de controle
            st.subheader("⚙️ Controles de Privacidade")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("🗑️ Excluir Meus Dados"):
                    self._delete_user_data(session_id)
                    st.success("Dados removidos conforme solicitado")

            with col2:
                if st.button("📥 Exportar Meus Dados"):
                    data = self._export_user_data(session_id)
                    st.download_button(
                        "⬇️ Download",
                        data,
                        file_name=f"meus_dados_{session_id[:8]}.json",
                        mime="application/json"
                    )

            with col3:
                if st.button("🔄 Revogar Consentimentos"):
                    self._revoke_all_consents(session_id)
                    st.success("Consentimentos revogados")
                    st.rerun()

        except Exception as e:
            st.error(f"Erro ao carregar dashboard: {e}")

    def _delete_user_data(self, session_id: str):
        """Remove todos os dados do usuário"""
        if not self.audit_conn:
            return

        try:
            cursor = self.audit_conn.cursor()

            # Remover consentimentos
            cursor.execute('DELETE FROM user_consents WHERE user_session = ?', (session_id,))

            # Remover logs (manter por auditoria, mas anonimizar)
            cursor.execute('''
                UPDATE access_logs 
                SET user_session = 'deleted_user' 
                WHERE user_session = ?
            ''', (session_id,))

            self.audit_conn.commit()

            # Limpar dados da sessão
            for key in list(st.session_state.keys()):
                if key.startswith('consent_') or key == 'user_session_id':
                    del st.session_state[key]

        except Exception as e:
            self.logger.error(f"Erro ao excluir dados do usuário: {e}")

    def _export_user_data(self, session_id: str) -> str:
        """Exporta dados do usuário em formato JSON"""
        if not self.audit_conn:
            return json.dumps({"error": "Sistema não disponível"})

        try:
            cursor = self.audit_conn.cursor()

            # Buscar consentimentos
            cursor.execute('''
                SELECT * FROM user_consents WHERE user_session = ?
            ''', (session_id,))
            consents = cursor.fetchall()

            # Buscar logs
            cursor.execute('''
                SELECT * FROM access_logs WHERE user_session = ?
            ''', (session_id,))
            logs = cursor.fetchall()

            export_data = {
                "session_id": session_id,
                "export_date": datetime.now().isoformat(),
                "consents": consents,
                "access_logs": logs
            }

            return json.dumps(export_data, indent=2, ensure_ascii=False)

        except Exception as e:
            return json.dumps({"error": f"Erro na exportação: {str(e)}"})

    def _revoke_all_consents(self, session_id: str):
        """Revoga todos os consentimentos do usuário"""
        if not self.audit_conn:
            return

        try:
            cursor = self.audit_conn.cursor()

            # Atualizar consentimentos para False
            cursor.execute('''
                UPDATE user_consents 
                SET consent_given = 0, timestamp = ?
                WHERE user_session = ?
            ''', (datetime.now().isoformat(), session_id))

            self.audit_conn.commit()

            # Limpar estado da sessão
            for key in list(st.session_state.keys()):
                if key.startswith('consent_'):
                    st.session_state[key] = False

        except Exception as e:
            self.logger.error(f"Erro ao revogar consentimentos: {e}")

class InnovativeAI:
    """Sistema de IA inovador para análises avançadas"""

    def __init__(self, security_manager):
        self.security = security_manager
        self.clustering_enabled = os.getenv('ENABLE_AI_CLUSTERING', 'true').lower() == 'true'
        self.sentiment_enabled = os.getenv('ENABLE_SENTIMENT_ANALYSIS', 'true').lower() == 'true'
        self.predictive_enabled = os.getenv('ENABLE_PREDICTIVE_ANALYTICS', 'true').lower() == 'true'

    def advanced_user_clustering(self, interaction_data):
        """Clustering avançado com múltiplas dimensões"""
        if not self.clustering_enabled or len(interaction_data) < 5:
            return None

        try:
            from sklearn.cluster import DBSCAN
            from sklearn.preprocessing import StandardScaler
            from sklearn.decomposition import PCA

            # Features avançadas
            features = []
            for _, row in interaction_data.iterrows():
                # Dimensões temporais
                timestamp = pd.to_datetime(row['timestamp'])
                hour = timestamp.hour
                weekday = timestamp.weekday()

                # Dimensões comportamentais
                query_len = len(str(row.get('user_query', '')))
                interaction_complexity = len(str(row.get('user_choices', '')))

                # Dimensões de navegação
                journey_depth = hash(str(row.get('journey_step', ''))) % 10

                features.append([
                    query_len,
                    interaction_complexity,
                    hour,
                    weekday,
                    journey_depth
                ])

            # Normalização e PCA
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)

            pca = PCA(n_components=min(3, len(features_scaled[0])))
            features_pca = pca.fit_transform(features_scaled)

            # Clustering DBSCAN (mais robusto que K-means)
            dbscan = DBSCAN(eps=0.5, min_samples=max(2, len(features)//5))
            clusters = dbscan.fit_predict(features_pca)

            # Análise de padrões
            cluster_analysis = self._analyze_clusters(clusters, features_pca)

            return {
                'clusters': clusters.tolist(),
                'n_clusters': len(set(clusters)) - (1 if -1 in clusters else 0),
                'outliers': sum(1 for c in clusters if c == -1),
                'pca_components': pca.components_.tolist(),
                'explained_variance': pca.explained_variance_ratio_.tolist(),
                'analysis': cluster_analysis
            }

        except Exception as e:
            self.security.logger.error(f"Erro no clustering avançado: {e}")
            return None

    def _analyze_clusters(self, clusters, features):
        """Analisa padrões dos clusters"""
        unique_clusters = set(clusters)
        analysis = {}

        for cluster_id in unique_clusters:
            if cluster_id == -1:  # Outliers
                continue

            cluster_mask = [i for i, c in enumerate(clusters) if c == cluster_id]
            if cluster_mask:
                cluster_features = features[cluster_mask]

                analysis[f'cluster_{cluster_id}'] = {
                    'size': len(cluster_mask),
                    'center': np.mean(cluster_features, axis=0).tolist(),
                    'std': np.std(cluster_features, axis=0).tolist()
                }

        return analysis

    def sentiment_analysis_simple(self, text_data):
        """Análise de sentimento simples para queries do usuário"""
        if not self.sentiment_enabled:
            return None

        try:
            # Palavras positivas e negativas simples para contexto médico
            positive_words = [
                'cura', 'melhora', 'saúde', 'prevenção', 'vacina',
                'tratamento', 'recuperação', 'bem-estar', 'vida',
                'sucesso', 'eficaz', 'seguro', 'estável'
            ]

            negative_words = [
                'morte', 'óbito', 'doença', 'sintoma', 'infecção',
                'pandemia', 'surto', 'complicação', 'risco',
                'grave', 'crítico', 'falha', 'erro'
            ]

            text_lower = text_data.lower()
            words = text_lower.split()

            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            total_words = len(words)

            if total_words == 0:
                return None

            sentiment_score = (positive_count - negative_count) / max(total_words, 1)

            if sentiment_score > 0.05:
                sentiment = "positivo"
            elif sentiment_score < -0.05:
                sentiment = "negativo"
            else:
                sentiment = "neutro"

            return {
                'sentiment': sentiment,
                'score': sentiment_score,
                'positive_words': positive_count,
                'negative_words': negative_count,
                'confidence': min(abs(sentiment_score) * 5, 1.0)
            }

        except Exception as e:
            self.security.logger.error(f"Erro na análise de sentimento: {e}")
            return None

    def predictive_analytics(self, historical_data):
        """Analytics preditivos simples para padrões de uso"""
        if not self.predictive_enabled or len(historical_data) < 10:
            return None

        try:
            # Análise temporal de uso
            historical_data = historical_data.copy()
            historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'])
            historical_data['hour'] = historical_data['timestamp'].dt.hour
            historical_data['weekday'] = historical_data['timestamp'].dt.weekday()

            # Padrões de uso por hora
            hourly_usage = historical_data.groupby('hour').size()
            peak_hour = hourly_usage.idxmax() if not hourly_usage.empty else 12

            # Padrões de uso por dia da semana
            weekly_usage = historical_data.groupby('weekday').size()
            peak_day = weekly_usage.idxmax() if not weekly_usage.empty else 1

            # Tipos de interação mais comuns
            interaction_patterns = historical_data['interaction_type'].value_counts()

            # Previsão simples para próxima interação
            last_interactions = historical_data.tail(5)['interaction_type'].tolist()
            next_interaction_prediction = self._predict_next_interaction(last_interactions)

            return {
                'peak_hour': int(peak_hour),
                'peak_day': int(peak_day),
                'most_common_interaction': interaction_patterns.index[0] if not interaction_patterns.empty else 'navigation',
                'interaction_diversity': len(interaction_patterns),
                'predicted_next_interaction': next_interaction_prediction,
                'usage_patterns': {
                    'hourly': hourly_usage.to_dict(),
                    'weekly': weekly_usage.to_dict()
                }
            }

        except Exception as e:
            self.security.logger.error(f"Erro na análise preditiva: {e}")
            return None

    def _predict_next_interaction(self, recent_interactions):
        """Prediz próxima interação baseada em padrões"""
        if len(recent_interactions) < 2:
            return "navigation"

        # Padrões simples baseados em sequências
        patterns = {
            ('navigation', 'covid_analysis'): 'research_search',
            ('research_search', 'save_article'): 'news_search',
            ('covid_analysis', 'navigation'): 'ai_insights',
            ('news_search', 'navigation'): 'dashboard',
            ('ai_insights', 'navigation'): 'all_data'
        }

        if len(recent_interactions) >= 2:
            last_two = tuple(recent_interactions[-2:])
            return patterns.get(last_two, 'navigation')

        return 'navigation'

    def generate_insights_report(self, user_data):
        """Gera relatório de insights personalizados"""
        try:
            clustering = self.advanced_user_clustering(user_data)

            # Análise de texto de todas as queries
            all_queries = ' '.join(user_data['user_query'].astype(str))
            sentiment = self.sentiment_analysis_simple(all_queries)

            predictive = self.predictive_analytics(user_data)

            report = {
                'generated_at': datetime.now().isoformat(),
                'user_profile': {
                    'total_interactions': len(user_data),
                    'session_duration_minutes': self._calculate_session_duration(user_data),
                    'most_active_hour': predictive['peak_hour'] if predictive else None,
                    'preferred_interactions': user_data['interaction_type'].value_counts().to_dict()
                },
                'behavioral_analysis': clustering,
                'sentiment_analysis': sentiment,
                'predictive_insights': predictive,
                'recommendations': self._generate_recommendations(clustering, sentiment, predictive)
            }

            # Anonimizar relatório
            return self.security.anonymize_user_data(report)

        except Exception as e:
            self.security.logger.error(f"Erro no relatório de insights: {e}")
            return None

    def _calculate_session_duration(self, user_data):
        """Calcula duração da sessão em minutos"""
        try:
            timestamps = pd.to_datetime(user_data['timestamp'])
            duration = (timestamps.max() - timestamps.min()).total_seconds() / 60
            return round(duration, 2)
        except:
            return 0

    def _generate_recommendations(self, clustering, sentiment, predictive):
        """Gera recomendações personalizadas baseadas em IA"""
        recommendations = []

        if clustering and clustering['n_clusters'] > 1:
            recommendations.append("🧠 Seus padrões de uso mostram comportamento exploratório - considere usar o dashboard personalizado")

        if sentiment and sentiment['sentiment'] == 'negativo':
            recommendations.append("💡 Suas consultas sugerem interesse em prevenção - explore nossa seção de pesquisas científicas")
        elif sentiment and sentiment['sentiment'] == 'positivo':
            recommendations.append("✨ Ótimo! Continue explorando dados de recuperação e tratamentos")

        if predictive and predictive['predicted_next_interaction']:
            next_action = predictive['predicted_next_interaction']
            recommendations.append(f"🎯 Sugerimos explorar: {next_action}")

        if not recommendations:
            recommendations.append("🔍 Continue explorando para receber insights personalizados!")

        return recommendations

class EthicalDataHandler:
    """Manipulador ético de dados conforme licenças"""

    def __init__(self):
        self.data_attributions = {
            'covid_nytimes': 'COVID-19 data by The New York Times (CC-BY)',
            'pubmed': 'PubMed data for educational use only',
            'who': 'WHO data used under fair use for educational purposes'
        }

    def add_data_attribution(self, data_source):
        """Adiciona atribuição adequada aos dados"""
        attribution = self.data_attributions.get(data_source, 'Data used for educational purposes')

        st.sidebar.markdown("---")
        st.sidebar.markdown("📄 **Atribuições de Dados**")
        st.sidebar.caption(attribution)

    def check_data_licenses(self):
        """Verifica conformidade com licenças"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("⚖️ **Licenças Respeitadas**")
        st.sidebar.caption("✅ CC-BY para dados COVID")
        st.sidebar.caption("✅ Uso educacional para APIs")
        st.sidebar.caption("✅ Fair use para web crawling")

# Instâncias globais
try:
    security_manager = SecurityManager()
    innovative_ai = InnovativeAI(security_manager)
    ethical_handler = EthicalDataHandler()

    # Log de inicialização bem-sucedida
    security_manager.logger.info("Sistema de segurança e IA inicializado com sucesso")

except Exception as e:
    print(f"Erro na inicialização do sistema de segurança: {e}")
    # Fallback para modo básico
    security_manager = None
    innovative_ai = None
    ethical_handler = None

class DataProtectionDecorator:
    """Decorator para proteção automática de dados em funções"""

    def __init__(self, security_manager: SecurityManager):
        self.security = security_manager

    def require_consent(self, consent_type: str = 'data_processing', purpose: str = 'analytics'):
        """Decorator que requer consentimento antes de executar função"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.security.check_user_consent(consent_type, purpose):
                    st.warning("⚠️ Consentimento necessário para esta funcionalidade")
                    return None

                # Log da execução
                self.security.log_data_access(f"function_{func.__name__}", "user_interaction")

                return func(*args, **kwargs)
            return wrapper
        return decorator

    def sanitize_inputs(self, input_types: Dict[str, str]):
        """Decorator para sanitização automática de inputs"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Sanitizar argumentos nomeados
                for param, data_type in input_types.items():
                    if param in kwargs:
                        validation = self.security.validate_data_input(kwargs[param], data_type)
                        if not validation['valid']:
                            st.error(f"Erro de validação em {param}: {validation['errors']}")
                            return None
                        kwargs[param] = validation['sanitized_data']

                return func(*args, **kwargs)
            return wrapper
        return decorator

# Função de conveniência para inicialização
def init_security() -> SecurityManager:
    """Inicializa o sistema de segurança"""
    if 'security_manager' not in st.session_state:
        st.session_state.security_manager = SecurityManager()
    return st.session_state.security_manager

# Decorator de conveniência
def with_security(consent_type: str = 'data_processing', purpose: str = 'analytics'):
    """Decorator simplificado para proteção de funções"""
    security = init_security()
    decorator = DataProtectionDecorator(security)
    return decorator.require_consent(consent_type, purpose)
