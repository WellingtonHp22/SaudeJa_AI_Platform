"""
Script de instalação automática das dependências do projeto SaudeJá
Versão melhorada com tratamento de erros e cancelamento
"""

import subprocess
import sys
import os
import time

def print_header():
    """Exibe cabeçalho do instalador"""
    print("=" * 60)
    print("SAUDEJA - INSTALACAO DE DEPENDENCIAS")
    print("=" * 60)
    print()

def install_package(package, timeout=120):
    """Instala um pacote usando pip com timeout"""
    try:
        print(f"[INSTALANDO] {package}...")
        
        # Executar com timeout para evitar travamento
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package, "--quiet"],
            timeout=timeout,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"[OK] {package} instalado com sucesso")
            return True
        else:
            print(f"[ERRO] Erro ao instalar {package}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Timeout ao instalar {package} (mais de {timeout}s)")
        return False
    except KeyboardInterrupt:
        print(f"\n[CANCELADO] Instalacao cancelada pelo usuario")
        return False
    except Exception as e:
        print(f"[ERRO] Erro inesperado ao instalar {package}: {e}")
        return False

def check_package(package_name):
    """Verifica se um pacote já está instalado"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_streamlit_only():
    """Instala apenas o Streamlit para teste rápido"""
    print("INSTALACAO RAPIDA - APENAS STREAMLIT")
    print("-" * 40)
    
    if check_package('streamlit'):
        print("[OK] Streamlit ja esta instalado!")
        return True
    
    success = install_package("streamlit")
    
    if success:
        print("\n[SUCESSO] Instalacao rapida concluida!")
        print("Para executar: streamlit run app.py")
        return True
    else:
        print("\n[FALHA] Falha na instalacao rapida")
        return False

def install_all_packages():
    """Instala todos os pacotes necessários"""
    print("INSTALACAO COMPLETA - TODOS OS PACOTES")
    print("-" * 40)
    
    # Pacotes essenciais (ordem de prioridade)
    essential_packages = [
        "streamlit",
        "pandas", 
        "plotly",
        "requests"
    ]
    
    # Pacotes adicionais
    additional_packages = [
        "matplotlib",
        "seaborn",
        "sqlalchemy",
        "python-dotenv",
        "beautifulsoup4",
        "numpy",
        "scikit-learn"
    ]
    
    all_packages = essential_packages + additional_packages
    failed_packages = []
    installed_count = 0
    
    print(f"Instalando {len(all_packages)} pacotes...")
    print()
    
    # Atualizar pip primeiro
    try:
        print("[ATUALIZANDO] pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"], 
                      timeout=60, check=True)
        print("[OK] pip atualizado")
    except:
        print("[AVISO] Nao foi possivel atualizar o pip, continuando...")
    
    print()
    
    # Instalar pacotes essenciais primeiro
    for package in essential_packages:
        if install_package(package):
            installed_count += 1
        else:
            failed_packages.append(package)
            if package == "streamlit":
                print("[ERRO CRITICO] Streamlit nao pode ser instalado!")
                print("Tente instalar manualmente: pip install streamlit")
                return False
    
    print(f"\n[OK] Pacotes essenciais: {len(essential_packages) - len([p for p in failed_packages if p in essential_packages])}/{len(essential_packages)}")
    
    # Instalar pacotes adicionais
    print("\n[INSTALANDO] pacotes adicionais...")
    for package in additional_packages:
        if install_package(package):
            installed_count += 1
        else:
            failed_packages.append(package)
    
    # Resultado final
    print("\n" + "=" * 60)
    print(f"[RESULTADO] Instalados: {installed_count}/{len(all_packages)} pacotes")
    
    if failed_packages:
        print(f"[FALHAS] Falharam: {len(failed_packages)} pacotes")
        print("Pacotes que falharam:")
        for package in failed_packages:
            print(f"   - {package}")
        print("\nVoce pode tentar instala-los manualmente depois:")
        print(f"pip install {' '.join(failed_packages)}")
    else:
        print("[SUCESSO] Todos os pacotes foram instalados com sucesso!")
    
    print("\nPara executar a aplicacao:")
    print("streamlit run app.py")
    
    return installed_count >= len(essential_packages)

def main():
    """Função principal com menu de opções"""
    print_header()
    
    print("Escolha uma opcao de instalacao:")
    print("1. INSTALACAO RAPIDA (apenas Streamlit)")
    print("2. INSTALACAO COMPLETA (todos os pacotes)")
    print("3. SAIR")
    print()
    
    try:
        choice = input("Digite sua escolha (1-3): ").strip()
        
        if choice == "1":
            print()
            install_streamlit_only()
        elif choice == "2":
            print()
            install_all_packages()
        elif choice == "3":
            print("Instalacao cancelada pelo usuario")
            return
        else:
            print("[ERRO] Opcao invalida!")
            
    except KeyboardInterrupt:
        print("\n\n[CANCELADO] Instalacao cancelada pelo usuario")
        print("Voce pode executar este script novamente a qualquer momento")
    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {e}")
    
    print("\nConsulte o README.md para mais informacoes")
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()
