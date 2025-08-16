"""
Script para baixar e manter atualizados os dados COVID-19 do NY Times
"""

import requests
import os
import pandas as pd
from datetime import datetime
import sys

def download_all_covid_data():
    """Baixa todos os datasets COVID-19 do NY Times"""
    
    base_url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master"
    
    datasets = {
        'us': 'us.csv',
        'us-states': 'us-states.csv', 
        'us-counties': 'us-counties.csv',
        'us-counties-2020': 'us-counties-2020.csv',
        'us-counties-2021': 'us-counties-2021.csv',
        'us-counties-2022': 'us-counties-2022.csv',
        'us-counties-2023': 'us-counties-2023.csv',
        'us-counties-recent': 'us-counties-recent.csv'
    }
    
    data_dir = r"c:\Users\welli\OneDrive\Documents\Banco_Dados\data"
    
    # Criar diretório se não existir
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    print("SaudeJa - Download de Dados COVID-19")
    print("=" * 50)
    
    for name, filename in datasets.items():
        try:
            print(f"Baixando {name} ({filename})...")
            
            url = f"{base_url}/{filename}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Salvar arquivo
            filepath = os.path.join(data_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Verificar dados
            df = pd.read_csv(filepath)
            print(f"OK {name}: {len(df)} registros baixados")
            
        except Exception as e:
            print(f"ERRO ao baixar {name}: {e}")
    
    print("\n" + "=" * 50)
    print("Download concluido!")
    print(f"Dados salvos em: {data_dir}")
    
    # Verificar se dados foram salvos corretamente
    saved_files = []
    for filename in datasets.values():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            saved_files.append(f"{filename}: {size/1024:.1f} KB")
    
    if saved_files:
        print("\nArquivos salvos:")
        for file_info in saved_files:
            print(f"  - {file_info}")
    
    return len(saved_files)

if __name__ == "__main__":
    try:
        files_downloaded = download_all_covid_data()
        print(f"\nSucesso! {files_downloaded} arquivos baixados.")
    except Exception as e:
        print(f"Erro geral: {e}")
        sys.exit(1)
