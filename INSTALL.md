# 🚀 Guia de Instalação - SaudeJá

## Opção 1: Instalação Automática (Recomendado)

### Windows
1. Execute o arquivo `setup.bat`:
   ```cmd
   setup.bat
   ```

### Linux/Mac ou Windows (via Python)
1. Execute o instalador Python:
   ```bash
   python install.py
   ```

2. Inicie a aplicação:
   ```bash
   python run.py
   ```

## Opção 2: Instalação Manual

### 1. Instalar Python (se necessário)
- Download: https://www.python.org/downloads/
- Versão mínima: Python 3.8

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Executar aplicação
```bash
streamlit run app.py
```

## Opção 3: Instalação Individual

Se você preferir instalar pacote por pacote:

```bash
pip install streamlit
pip install pandas
pip install matplotlib
pip install seaborn
pip install plotly
pip install requests
pip install sqlalchemy
pip install psycopg2-binary
pip install python-dotenv
pip install beautifulsoup4
pip install numpy
pip install scikit-learn
pip install wordcloud
```

## Verificação da Instalação

1. Abra um terminal/prompt
2. Digite: `streamlit --version`
3. Se aparecer a versão, a instalação foi bem-sucedida

## Solução de Problemas

### Erro: "streamlit não é reconhecido"
- **Solução**: Execute `python -m pip install streamlit`
- **Alternativa**: Use `python -m streamlit run app.py`

### Erro de permissão no Windows
- **Solução**: Execute o prompt como administrador
- **Alternativa**: Use `pip install --user streamlit`

### Erro de SSL/certificado
- **Solução**: Execute `pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org streamlit`

### Erro de versão do Python
- **Solução**: Certifique-se de usar Python 3.8 ou superior
- **Verificação**: `python --version`

## Configuração Opcional

### Banco de Dados PostgreSQL
Se quiser usar PostgreSQL em vez de SQLite:

1. Crie um arquivo `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

### APIs Externas
Para funcionalidades avançadas, configure:

```env
OPENAI_API_KEY=sua_chave_openai
GOOGLE_API_KEY=sua_chave_google
```

## Primeira Execução

1. Abra o terminal na pasta do projeto
2. Execute: `streamlit run app.py`
3. O navegador abrirá automaticamente em `http://localhost:8501`
4. Comece explorando a jornada de inovação!

## Suporte

Se encontrar problemas:
1. Verifique o arquivo `README.md`
2. Consulte a documentação do Streamlit: https://docs.streamlit.io
3. Reporte issues no GitHub do projeto

---

**Desenvolvido para SaudeJá - Especialista em P&D na área da saúde**
