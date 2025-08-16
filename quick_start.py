"""
Script de início rápido - instala apenas o essencial e executa a aplicação
"""

import subprocess
import sys
import os
from pathlib import Path

def quick_install():
    """Instalação super rápida apenas do Streamlit"""
    print("SAUDEJA - INICIO RAPIDO")
    print("=" * 30)
    
    # Verificar se streamlit já está instalado
    try:
        import streamlit
        print("[OK] Streamlit ja esta instalado!")
        return True
    except ImportError:
        pass
    
    print("[INSTALANDO] Streamlit...")
    
    try:
        # Instalar streamlit de forma simples
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "streamlit", "--quiet"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("[OK] Streamlit instalado com sucesso!")
            return True
        else:
            print(f"[ERRO] {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro na instalacao: {e}")
        return False

def run_app():
    """Executa a aplicação"""
    print("\n[INICIANDO] SaudeJa...")
    
    if not Path("app.py").exists():
        print("[ERRO] Arquivo app.py nao encontrado!")
        return False
    
    try:
        # Executar a aplicação
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
        return True
    except KeyboardInterrupt:
        print("\n[ENCERRADO] Aplicacao encerrada")
        return True
    except Exception as e:
        print(f"[ERRO] Erro ao executar: {e}")
        return False

def main():
    """Função principal"""
    try:
        # Instalar e executar
        if quick_install():
            print("\n" + "="*50)
            print("[PRONTO] A aplicacao sera iniciada agora...")
            print("[NAVEGADOR] O navegador abrira automaticamente")
            print("[PARAR] Para parar: Ctrl+C no terminal")
            print("="*50)
            
            input("\nPressione Enter para continuar...")
            run_app()
        else:
            print("\n[FALHA] Nao foi possivel instalar as dependencias")
            print("Tente: pip install streamlit")
    
    except KeyboardInterrupt:
        print("\n\n[CANCELADO] Cancelado pelo usuario")
    except Exception as e:
        print(f"\n[ERRO] Erro: {e}")
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()
