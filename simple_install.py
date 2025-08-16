"""
Instalador completo do SaudeJá com todas as dependências
"""

import subprocess
import sys
import os

def check_package(package):
    """Verifica se um pacote está instalado"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def install_packages():
    """Instala todas as dependências necessárias"""
    packages = [
        "streamlit",
        "pandas", 
        "plotly",
        "requests",
        "numpy",
        "sqlalchemy"
    ]
    
    print("Verificando dependências...")
    missing = []
    
    for package in packages:
        if not check_package(package):
            missing.append(package)
        else:
            print(f"✅ {package} já instalado")
    
    if missing:
        print(f"\nInstalando {len(missing)} pacotes: {', '.join(missing)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--upgrade", "--quiet"
            ] + missing)
            print("✅ Todas as dependências instaladas!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro na instalação: {e}")
            return False
    else:
        print("✅ Todas as dependências já estão instaladas!")
        return True

def check_app_file():
    """Verifica se o arquivo app.py existe"""
    if not os.path.exists("app.py"):
        print("❌ Arquivo app.py não encontrado!")
        print("Certifique-se de estar no diretório correto")
        return False
    return True

def run_app():
    """Executa a aplicação"""
    print("\n🚀 Iniciando SaudeJá...")
    print("🌐 A aplicação abrirá em: http://localhost:8501")
    print("⏹️ Para parar: Ctrl+C no terminal")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")
        print("\n🔧 Comandos alternativos:")
        print("streamlit run app.py")
        print("python -m streamlit run app.py")

def main():
    print("=" * 50)
    print("🏥 SaudeJá - Instalador Completo")
    print("=" * 50)
    
    # Verificar arquivo
    if not check_app_file():
        input("\nPressione Enter para sair...")
        return
    
    # Instalar dependências
    if not install_packages():
        print("\n❌ Falha na instalação das dependências")
        input("Pressione Enter para sair...")
        return
    
    # Opção para deploy no GitHub
    deploy_choice = input("\n🌐 Deseja fazer deploy no GitHub? (s/n): ").lower()
    if deploy_choice in ['s', 'sim', 'y', 'yes']:
        os.system("python git_deploy.py")
        return
    
    # Executar aplicação
    print("\n" + "=" * 50)
    print("🎯 Tudo pronto! Iniciando aplicação...")
    run_app()

if __name__ == "__main__":
    main()
