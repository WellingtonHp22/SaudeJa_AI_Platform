"""
Script para fazer deploy do projeto SaudeJá no GitHub
"""

import subprocess
import os
import sys

def run_command(command, description):
    """Executa um comando e mostra o resultado"""
    print(f"\n📋 {description}")
    print(f"🔧 Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Sucesso!")
            if result.stdout:
                print(f"📝 Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} - Erro!")
            if result.stderr:
                print(f"🚨 Erro: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Exceção: {e}")
        return False

def check_git_installed():
    """Verifica se Git está instalado"""
    return run_command("git --version", "Verificando instalação do Git")

def create_gitignore():
    """Cria arquivo .gitignore"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Streamlit
.streamlit/

# Database
*.db
*.sqlite
*.sqlite3

# Data files
*.csv
data/
datasets/

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Cache
.cache/
"""
    
    try:
        with open('.gitignore', 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("✅ Arquivo .gitignore criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar .gitignore: {e}")
        return False

def create_readme():
    """Cria arquivo README.md"""
    readme_content = """# SaudeJá - Plataforma de IA para Inovação em Saúde 🏥

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
"""
    
    try:
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✅ Arquivo README.md criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar README.md: {e}")
        return False

def git_deploy():
    """Executa o processo completo de deploy"""
    print("🚀 SaudeJá - Deploy para GitHub")
    print("=" * 50)
    
    # Verificar se Git está instalado
    if not check_git_installed():
        print("❌ Git não está instalado. Instale o Git primeiro:")
        print("https://git-scm.com/downloads")
        return False
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("app.py"):
        print("❌ Arquivo app.py não encontrado!")
        print("Certifique-se de estar no diretório do projeto")
        return False
    
    # Criar arquivos necessários
    create_gitignore()
    create_readme()
    
    # Comandos Git
    commands = [
        ("git init", "Inicializando repositório Git"),
        ("git add .", "Adicionando todos os arquivos"),
        ("git commit -m 'Initial commit - SaudeJá AI Platform'", "Fazendo commit inicial"),
        ("git branch -M main", "Renomeando branch para main"),
        ("git remote add origin https://github.com/WellingtonHp22/SaudeJa_AI_Platform.git", "Adicionando repositório remoto"),
        ("git push -u origin main", "Enviando para GitHub")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"\n❌ Falha no comando: {command}")
            print("🔧 Comandos manuais:")
            print("git init")
            print("git add .")
            print("git commit -m 'Initial commit'")
            print("git branch -M main")
            print("git remote add origin https://github.com/WellingtonHp22/SaudeJa_AI_Platform.git")
            print("git push -u origin main")
            return False
    
    print("\n🎉 Deploy concluído com sucesso!")
    print("🌐 Repositório: https://github.com/WellingtonHp22/SaudeJa_AI_Platform")
    print("📱 Para deploy no Streamlit Cloud:")
    print("1. Acesse https://share.streamlit.io/")
    print("2. Conecte com GitHub")
    print("3. Selecione o repositório SaudeJa_AI_Platform")
    print("4. Arquivo principal: app.py")
    
    return True

if __name__ == "__main__":
    git_deploy()
