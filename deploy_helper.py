"""
Script auxiliar para deploy com comandos específicos para diferentes situações
"""

import subprocess
import sys

def run_cmd(command):
    """Executa comando simples"""
    print(f"Executando: {command}")
    try:
        result = subprocess.run(command, shell=True, text=True)
        return result.returncode == 0
    except:
        return False

def solution_powershell_policy():
    """Solução para política de execução PowerShell"""
    print("SOLUÇÃO: Política de Execução PowerShell")
    print("=" * 50)
    print("Execute no PowerShell como Administrador:")
    print("Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser")
    print("\nOu use o Git Bash: C:\\Program Files\\Git\\bin\\bash.exe")

def solution_unrelated_histories():
    """Solução para histórias não relacionadas"""
    print("SOLUÇÃO: Histórias Não Relacionadas")
    print("=" * 50)
    
    commands = [
        "git pull origin main --allow-unrelated-histories",
        "git push origin main"
    ]
    
    for cmd in commands:
        if not run_cmd(cmd):
            print(f"❌ Falhou: {cmd}")
        else:
            print(f"✅ Sucesso: {cmd}")

def solution_force_push():
    """Solução com push forçado"""
    print("SOLUÇÃO: Push Forçado (Última Opção)")
    print("=" * 50)
    print("⚠️ CUIDADO: Isso pode sobrescrever mudanças remotas!")
    
    confirm = input("Tem certeza? Digite 'CONFIRMO': ")
    if confirm == "CONFIRMO":
        return run_cmd("git push --force-with-lease origin main")
    else:
        print("Operação cancelada")
        return False

def main():
    print("SaudeJá - Deploy Helper")
    print("=" * 30)
    print("1. Política PowerShell")
    print("2. Histórias não relacionadas")
    print("3. Push forçado")
    print("4. Status atual")
    
    choice = input("Escolha (1-4): ")
    
    if choice == "1":
        solution_powershell_policy()
    elif choice == "2":
        solution_unrelated_histories()
    elif choice == "3":
        solution_force_push()
    elif choice == "4":
        run_cmd("git status")
        run_cmd("git log --oneline -5")
    else:
        print("Opção inválida")

if __name__ == "__main__":
    main()
