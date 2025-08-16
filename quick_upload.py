"""
Upload rápido apenas dos arquivos essenciais
"""

import subprocess
import os

def run_cmd(command):
    """Executa comando simples"""
    print(f"▶️ {command}")
    try:
        result = subprocess.run(command, shell=True, text=True)
        return result.returncode == 0
    except:
        return False

def main():
    print("🚀 UPLOAD RÁPIDO - APENAS ARQUIVOS ESSENCIAIS")
    print("=" * 50)
    
    # Limpar staging area
    run_cmd("git reset")
    
    # Arquivos essenciais
    essential_files = [
        "app.py",
        "simple_install.py",
        "database.py", 
        "analytics.py",
        "data_sources.py"
    ]
    
    print("📁 Adicionando apenas arquivos essenciais...")
    
    # Adicionar um por vez
    for file in essential_files:
        if os.path.exists(file):
            run_cmd(f"git add {file}")
            print(f"✅ {file}")
        else:
            print(f"❌ {file} não encontrado")
    
    # Commit e push
    commands = [
        "git commit -m 'feat: Essential SaudeJá files'",
        "git push --force-with-lease origin main"
    ]
    
    for cmd in commands:
        if run_cmd(cmd):
            print(f"✅ Sucesso: {cmd}")
        else:
            print(f"❌ Falha: {cmd}")
            break
    
    print("\n🎉 Upload rápido concluído!")
    print("🌐 Verifique: https://github.com/WellingtonHp22/SaudeJa_AI_Platform")

if __name__ == "__main__":
    main()
