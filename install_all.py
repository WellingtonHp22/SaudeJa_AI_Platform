"""
Instalador usando requirements.txt
"""

import subprocess
import sys
import os

def install_from_requirements():
    """Instala dependências do requirements.txt"""
    if os.path.exists("requirements.txt"):
        print("📦 Instalando dependências do requirements.txt...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "-r", "requirements.txt", "--upgrade"
            ])
            print("✅ Instalação concluída!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro na instalação")
            return False
    else:
        print("❌ Arquivo requirements.txt não encontrado")
        return False

def main():
    print("SaudeJá - Instalação via Requirements")
    print("=" * 40)
    
    if install_from_requirements():
        print("\n🚀 Executando aplicação...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    else:
        print("Use: python simple_install.py")

if __name__ == "__main__":
    main()
