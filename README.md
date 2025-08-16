# SaudeJá - Plataforma de IA para Inovação em Saúde 🏥

## 📋 Descrição
Plataforma completa para análise de dados de saúde, pesquisa científica e identificação de oportunidades de inovação usando Inteligência Artificial.

## 🚀 Funcionalidades
- 📊 **Análise COVID-19**: Dados reais do NY Times
- 📚 **Pesquisa Científica**: Simulação de dados PubMed
- ⚗️ **Análise de Patentes**: Panorama de propriedade intelectual
- 🤖 **IA Recomendações**: Sistema inteligente de sugestões
- 📈 **Analytics**: Dashboard completo de métricas

## 🛠️ Instalação

### Pré-requisitos
- Python 3.7+
- pip

### Instalação Rápida
```bash
# Clone o repositório
git clone https://github.com/WellingtonHp22/SaudeJa_AI_Platform.git
cd SaudeJa_AI_Platform

# Execute o instalador
python simple_install.py
```

### Instalação Manual
```bash
pip install streamlit pandas plotly requests numpy sqlalchemy
python -m streamlit run app.py
```

## 🎯 Como Usar
1. Execute `python simple_install.py`
2. Acesse `http://localhost:8501`
3. Explore as diferentes funcionalidades no menu lateral

## 📁 Estrutura do Projeto
```
SaudeJa_AI_Platform/
├── app.py              # Aplicação principal
├── simple_install.py   # Instalador automático
├── data_sources.py     # Gerenciadores de dados
├── database.py         # Sistema de banco de dados
├── analytics.py        # Motor de analytics
├── git_deploy.py       # Script de deploy
└── README.md          # Documentação
```

## 🔧 Dependências
- streamlit>=1.28.0
- pandas>=1.5.0
- plotly>=5.0.0
- requests>=2.25.0
- numpy>=1.21.0
- sqlalchemy>=1.4.0

## 🤝 Contribuição
1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença
Este projeto está sob a licença MIT.

## 👨‍💻 Autor
Wellington HP - [GitHub](https://github.com/WellingtonHp22)

## 🌟 Demonstração
Acesse a aplicação em: [SaudeJá Platform](https://saudeja-ai-platform.streamlit.app)
