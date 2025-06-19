import os
import zipfile
import shutil
import pandas as pd
import gradio as gr
import traceback
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# Importa a chave de API do arquivo de configuração
try:
    from config import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = None

# Diretório para extrair os arquivos
EXTRACT_DIR = "uploaded_data"
# Dicionário global para armazenar os DataFrames
global_dfs = {}

def get_clean_df_name(filename):
    """Cria um nome de variável Python válido a partir de um nome de arquivo."""
    base_name = os.path.splitext(filename)[0]
    if 'Cabecalho' in base_name:
        return 'df_cabecalho'
    if 'Itens' in base_name:
        return 'df_itens'
    clean_name = ''.join(c if c.isalnum() else '_' for c in base_name)
    return f"df_{clean_name.lower()}"

def process_files(files):
    """Processa uma lista de arquivos enviados (.zip, .csv, .xlsx)."""
    global global_dfs
    global_dfs = {}
    if os.path.exists(EXTRACT_DIR):
        shutil.rmtree(EXTRACT_DIR)
    os.makedirs(EXTRACT_DIR, exist_ok=True)

    loaded_files_status = []
    data_files_to_load = []
    
    if not files:
        return "Nenhum arquivo enviado."

    for file_obj in files:
        file_path = file_obj.name
        if file_path.endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(EXTRACT_DIR)
            for root, _, extracted_files in os.walk(EXTRACT_DIR):
                for f in extracted_files:
                    data_files_to_load.append(os.path.join(root, f))
        else:
            data_files_to_load.append(file_path)

    for data_file_path in data_files_to_load:
        try:
            filename = os.path.basename(data_file_path)
            if filename.endswith(".csv"):
                df = pd.read_csv(data_file_path, on_bad_lines='skip')
            elif filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(data_file_path)
            else:
                continue
            
            df_name = get_clean_df_name(filename)
            global_dfs[df_name] = df
            loaded_files_status.append(f"✅ {filename} (carregado como `{df_name}`)")

        except Exception as e:
            loaded_files_status.append(f"❌ Erro ao ler {os.path.basename(data_file_path)}: {e}")
    
    if not global_dfs:
        return "Nenhum arquivo de dados (CSV/Excel) válido foi encontrado."
        
    return f"{len(global_dfs)} tabelas de dados carregadas:\n" + "\n".join(loaded_files_status)

def ask_question(question):
    """Usa o Agente de DataFrames do LangChain para responder a uma pergunta."""
    if not global_dfs:
        return "Nenhum dado foi carregado. Por favor, processe um arquivo primeiro."
    if not OPENAI_API_KEY or OPENAI_API_KEY == "SUA_CHAVE_DE_API_OPENAI_AQUI":
        return "A chave de API da OpenAI não foi configurada. Por favor, edite o arquivo `config.py`."

    try:
        llm = ChatOpenAI(
            temperature=0, 
            model="gpt-4.1-mini", 
            api_key=OPENAI_API_KEY
        )

        # A lista de dataframes que o agente vai usar
        df_list = list(global_dfs.values())
        
        # O agente do LangChain
        agent = create_pandas_dataframe_agent(
            llm,
            df_list, # Passa a LISTA de dataframes
            verbose=True,
            allow_dangerous_code=True
        )

        # Instrução para o agente saber qual dataframe é qual
        # Ele se refere a eles como df1, df2, etc., na ordem da lista.
        df_names_ordered = list(global_dfs.keys())
        instruction_prefix = "Você tem acesso a múltiplos dataframes.\n"
        for i, name in enumerate(df_names_ordered):
            instruction_prefix += f"O dataframe `df{i+1}` corresponde à tabela '{name}'.\n"
        
        # Monta o prompt final
        final_prompt = f"{instruction_prefix}\nUsando esses dataframes, responda à seguinte pergunta: {question}"

        # Invoca o agente
        result = agent.invoke({"input": final_prompt})
        
        return result['output']

    except Exception as e:
        return f"Ocorreu um erro ao processar a pergunta: {e}\n{traceback.format_exc()}"

# --- Interface Gradio ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🧠 ProcessON - I2A2 (Versão com Agente Estável)")
    gr.Markdown("Faça upload de arquivos `.zip`, `.csv` ou `.xlsx`. O agente analisará o conteúdo completo para responder suas perguntas.")
    
    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(
                label="Faça upload de seus arquivos de dados", 
                file_types=[".zip", ".csv", ".xlsx"],
                file_count="multiple"
            )
            process_btn = gr.Button("Processar Arquivos", variant="primary")
            status_box = gr.Textbox(label="Status do Processamento", lines=4, interactive=False)

        with gr.Column(scale=2):
            question_box = gr.Textbox(label="Faça sua pergunta sobre os dados")
            answer_box = gr.Textbox(label="Resposta da IA", lines=8, interactive=False)

    process_btn.click(fn=process_files, inputs=[file_input], outputs=[status_box])
    question_box.submit(fn=ask_question, inputs=[question_box], outputs=[answer_box])

demo.launch(share=True, debug=True)