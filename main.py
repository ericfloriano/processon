import os
import zipfile
import shutil
import openai
import pandas as pd
import gradio as gr
import dspy
from dspy import LM, configure, Module

openai.api_key = 

# Modelo
dspy.configure(
    lm=LM(

        model="gpt-4.1-mini",
        api_key=openai.api_key,
        temperature=0.0,
        max_tokens=20000
    )
)

EXTRACT_DIR = "uploaded_data"
global_dataframes = []

# Carregar CSVs do ZIP
def process_zip(zip_file):
    global global_dataframes
    if os.path.exists(EXTRACT_DIR):
        shutil.rmtree(EXTRACT_DIR)
    os.makedirs(EXTRACT_DIR, exist_ok=True)

    zip_path = os.path.join(EXTRACT_DIR, "uploaded.zip")
    shutil.copy(zip_file.name, zip_path)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)

    dfs = []
    for root, _, files in os.walk(EXTRACT_DIR):
        for file in files:
            if file.endswith(".csv"):
                try:
                    df = pd.read_csv(os.path.join(root, file))
                    df['__source_file'] = file
                    dfs.append(df)
                except Exception as e:
                    print(f"Erro lendo {file}: {e}")
    global_dataframes = dfs
    return f"{len(dfs)} arquivos CSV carregados."

# Define DSPy
class AskCSV(dspy.Signature):
    question = dspy.InputField()
    context = dspy.InputField()
    answer = dspy.OutputField()

# Define chamada ao DSPy
class AskCSVModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(AskCSV)

    def forward(self, question, context):
        return self.predict(question=question, context=context)

ask_module = AskCSVModule()

# Responder a pergunta usando o DSPy
def ask_question(question):
    if not global_dataframes:
        return "Nenhum CSV foi carregado ainda."
    context = "\n\n".join(df.head(10).to_string(index=False) for df in global_dataframes)
    result = ask_module(question=question, context=context)
    return result.answer

# Interface Gradio
with gr.Blocks() as demo:
    gr.Markdown("## 🧠 ProcessON - I2A2")
    file = gr.File(label="Faça upload do arquivo ZIP", file_types=[".zip"])
    status = gr.Textbox(label="Status")
    process_btn = gr.Button("Processar ZIP")

    question = gr.Textbox(label="Pergunta sobre os dados")
    answer = gr.Textbox(label="Resposta IA")

    process_btn.click(fn=process_zip, inputs=[file], outputs=[status])
    question.submit(fn=ask_question, inputs=[question], outputs=[answer])

demo.launch(share=True)