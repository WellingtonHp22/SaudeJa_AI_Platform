"""
Script para executar a aplicação SaudeJá com verificação de dependências
"""

import subprocess
import sys
import os
from pathlib import Path

def check_streamlit():
    """Verifica se o Streamlit está instalado"""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def install_streamlit():
    """Instala o Streamlit"""
    try:
        print("[INSTALANDO] Streamlit...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
        return True
    except subprocess.CalledProcessError:
        return False

def run_app():
    """Executa a aplicação Streamlit"""
    try:
        # Verificar se o arquivo app.py existe
        if not Path("app.py").exists():
            print("[ERRO] Arquivo app.py nao encontrado!")
            return False
        
        # Executar streamlit
        print("[INICIANDO] Aplicacao SaudeJa...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
        return True
        
    except KeyboardInterrupt:
        print("\n[ENCERRADO] Aplicacao encerrada pelo usuario")
        return True
    except Exception as e:
        print(f"[ERRO] Erro ao executar aplicacao: {e}")
        return False

def main():
    """Função principal"""
    print("SAUDEJA - JORNADA DE INOVACAO EM SAUDE")
    print("=" * 50)
    
    # Verificar se Streamlit está instalado
    if not check_streamlit():
        print("[AVISO] Streamlit nao encontrado!")
        response = input("Deseja instalar automaticamente? (y/n): ")
        
        if response.lower() in ['y', 'yes', 's', 'sim']:
            if install_streamlit():
                print("[OK] Streamlit instalado com sucesso!")
            else:
                print("[ERRO] Falha na instalacao do Streamlit")
                print("Tente manualmente: pip install streamlit")
                return
        else:
            print("Para instalar manualmente: pip install streamlit")
            return
    
    # Executar a aplicação
    run_app()

if __name__ == "__main__":
    main()
