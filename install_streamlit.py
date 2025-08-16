"""
Script para instalar apenas o Streamlit
"""

import subprocess
import sys

def install_streamlit():
    """Instala o Streamlit"""
    try:
        print("Instalando Streamlit...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "streamlit"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Streamlit instalado com sucesso!")
            return True
        else:
            print(f"❌ Erro: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro na instalação: {e}")
        return False

def run_app():
    """Executa a aplicação"""
    try:
        print("Executando aplicação...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")

if __name__ == "__main__":
    print("INSTALACAO RAPIDA DO STREAMLIT")
    print("=" * 40)
    
    if install_streamlit():
        print("\nPressione Enter para executar a aplicação...")
        input()
        run_app()
    else:
        print("Falha na instalação. Tente manualmente:")
        print("pip install streamlit")
