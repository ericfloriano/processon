# 🧠 ProcessON - I2A2 | Consulta de Dados CSV por Agente

Este projeto oferece uma interface interativa para processar e consultar dados de múltiplos arquivos CSV e XLSX, incluindo aqueles contidos em arquivos ZIP. Ele aproveita o poder dos Modelos de Linguagem Grandes (LLMs) via biblioteca `langchain` e `Gradio` para uma interface web amigável, permitindo responder a perguntas em linguagem natural sobre os dados carregados de forma mais robusta e completa, utilizando um agente de DataFrames do LangChain.

---

## 🎯 Contexto do Desafio I2A2

Esta atividade faz parte do curso I2A2 e tem como objetivo principal **criar um ou mais agentes que permitam a um usuário realizar perguntas sobre arquivos CSV e/ou XLSX disponibilizados**.

Por exemplo, os usuários podem perguntar:
* "Qual é o fornecedor que teve maior montante recebido?"
* "Qual item teve maior volume entregue (em quantidade)?"
* "Qual o valor total gasto pelo 'MINISTERIO DA SAUDE'?"
* "Em qual dia da semana (segunda, terça, etc.) a maioria das notas fiscais foi emitida?"
* "Qual empresa vendeu mais livros?"
* "Para cada estado de destino (UF DESTINATÁRIO), qual foi o valor total comprado e o número total de itens únicos adquiridos?"
* E assim por diante, explorando os dados de forma conversacional e complexa.

### Recursos Utilizados

Para este desafio, é fornecido um arquivo de exemplo chamado `202401_NFs.zip`. Este arquivo contém:

* **`202401_NFs_Cabecalho.csv`**: O cabeçalho de 100 notas fiscais selecionadas aleatoriamente do arquivo de notas fiscais do mês de janeiro/2024, disponibilizado pelo Tribunal de Contas da União.
* **`202401_NFs_Itens.csv`**: Os itens correspondentes das 100 notas fiscais selecionadas.

Ambos os arquivos estão em formato CSV. Os campos estão separados por vírgulas e o separador de casas decimais dos valores numéricos é ponto. As datas estão no formato AAAA-MM-DD HH:MN:SS.

---

## 🚀 Primeiros Passos

Siga estas instruções para configurar e executar o projeto localmente.

### Pré-requisitos

Antes de começar, certifique-se de ter o seguinte instalado:

* **Python 3.8+**
* **pip** (instalador de pacotes Python)

### Instalação

1.  **Clone o repositório (ou salve o código):**
    Se o seu código estiver em um arquivo, salve-o como `main.py`. Se for parte de um repositório Git, clone-o:
    ```bash
    git clone <url_do_seu_repositorio>
    cd <diretorio_do_seu_repositorio>
    ```

2.  **Crie o arquivo `config.py`:**
    Crie um arquivo chamado `config.py` no mesmo diretório do seu script `main.py` com o seguinte conteúdo:
    ```python
    # config.py
    # Substitua a string abaixo pela sua chave de API da OpenAI.
    OPENAI_API_KEY = "SUA_CHAVE_DE_API_OPENAI_AQUI"
    ```

3.  **Instale os pacotes Python necessários:**
    Crie um arquivo `requirements.txt` no mesmo diretório do seu script Python com o seguinte conteúdo:

    ```
    gradio
    pandas
    langchain-openai
    langchain-experimental
    tabulate
    openpyxl
    ```

    Em seguida, instale-os usando pip:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure sua Chave de API OpenAI:**
    A aplicação requer uma chave de API OpenAI para interagir com o modelo GPT.
    Você precisa definir a variável `OPENAI_API_KEY` no arquivo `config.py` conforme instruído no passo 2.

    **Importante:** Para ambientes de produção, é altamente recomendável usar variáveis de ambiente para armazenar sua chave de API por motivos de segurança (por exemplo, `os.environ.get("OPENAI_API_KEY")`).

---

## 🛠️ Como Usar

1.  **Execute a aplicação:**
    Abra seu terminal ou prompt de comando, navegue até o diretório do projeto e execute o script Python:
    ```bash
    python main.py
    ```

2.  **Acesse a interface web:**
    Você pode acessar a interface do Gradio localmente (o link será exibido no seu terminal, geralmente `http://127.0.0.1:7860`) ou através de um link de compartilhamento público (como `https://42d389f99c5f2f062f.gradio.live/` exemplificado nos logs, que expira em 1 semana).

3.  **Envie seus arquivos:**
    Na interface do Gradio, clique no componente "Faça upload de seus arquivos de dados" e selecione um ou mais arquivos `.zip`, `.csv` ou `.xlsx`.

4.  **Processar os arquivos:**
    Clique no botão "Processar Arquivos". A aplicação extrairá os arquivos (se for um ZIP) e os carregará em DataFrames do pandas. A caixa de texto "Status do Processamento" mostrará quais arquivos foram carregados.

5.  **Faça perguntas:**
    Depois que os dados forem carregados, você pode digitar suas perguntas sobre os dados na caixa de texto "Faça sua pergunta sobre os dados" e pressionar Enter (ou clicar fora da caixa de texto). A IA, através do agente LangChain, fornecerá uma resposta na caixa de texto "Resposta da IA", utilizando os dados carregados como contexto.

---

## ⚙️ Como Funciona

A aplicação combina várias bibliotecas poderosas para alcançar sua funcionalidade:

* **`zipfile` e `shutil`:** Usados para manipulação de arquivos ZIP, extração e gerenciamento de diretórios temporários.
* **`pandas`:** Essencial para ler e manipular dados CSV/XLSX, armazenando-os em DataFrames.
* **`langchain_openai` e `langchain_experimental`:**
    * `ChatOpenAI`: Fornece a interface para a API da OpenAI (`gpt-4.1-mini` é o modelo utilizado).
    * `create_pandas_dataframe_agent`: Uma ferramenta poderosa do LangChain que permite que um LLM interaja com um ou múltiplos DataFrames do pandas, executando operações para responder a perguntas complexas. Ele é capaz de raciocinar sobre os dados e gerar código Python para extrair as informações necessárias.
* **`gradio`:** Fornece a interface web amigável e interativa, simplificando a criação de componentes para upload de arquivos, entradas de texto e botões, conectando-os às funções Python de backend.

### Lógica Central

1.  **Upload e Processamento de Arquivos (`process_files`):**
    * Quando o usuário faz upload de arquivos (ZIP, CSV ou XLSX), eles são salvos temporariamente.
    * Se for um arquivo ZIP, seu conteúdo é extraído para o diretório `uploaded_data`.
    * Todos os arquivos `.csv` e `.xlsx` encontrados (seja diretamente ou dentro do ZIP) são lidos em DataFrames do pandas.
    * Esses DataFrames são armazenados em um dicionário global (`global_dfs`), com nomes limpos (`df_cabecalho`, `df_itens`, etc.) para fácil referência pelo agente.

2.  **Resposta a Perguntas (`ask_question`):**
    * Verifica se os dados foram carregados e se a chave de API da OpenAI está configurada.
    * Inicializa o modelo `ChatOpenAI` com `temperature=0` para respostas mais determinísticas e factuais.
    * Cria um `create_pandas_dataframe_agent` do LangChain, passando a lista de DataFrames carregados. O agente é configurado com `verbose=True` para mostrar o raciocínio e as ações tomadas pelo LLM e `allow_dangerous_code=True` para permitir a execução de código Python gerado pelo agente.
    * Um `instruction_prefix` é construído para informar o agente sobre os nomes dos DataFrames carregados (`df_cabecalho`, `df_itens`), permitindo que ele se refira a eles corretamente (`df1`, `df2`, etc.).
    * A pergunta do usuário é combinada com o prefixo de instrução e passada para o agente via `agent.invoke()`.
    * O agente utiliza o LLM para raciocinar, gerar e executar o código Python necessário nos DataFrames para responder à pergunta.
    * A resposta gerada pelo agente é então exibida na interface do Gradio.

---

## 🛑 Limitações

* **Custos da API OpenAI:** O uso do modelo `gpt-4.1-mini` (ou qualquer outro modelo pago da OpenAI) incorre em custos. O uso excessivo pode gerar despesas significativas.
* **Token Limit (Context Window):** Embora os modelos GPT tenham janelas de contexto grandes, processar datasets muito extensos pode ainda exceder esses limites. O agente LangChain é mais eficiente em manipular grandes DataFrames internamente, mas o volume de saída do código Python e o raciocínio do LLM ainda consomem tokens.
* **Complexidade da Pergunta:** Perguntas muito ambíguas ou que exigem um raciocínio complexo demais podem desafiar a capacidade do agente de gerar o código Python correto.
* **Segurança:** Armazenar chaves de API diretamente no código ou em arquivos de configuração não é recomendado para ambientes de produção. O ideal é usar variáveis de ambiente ou serviços de gerenciamento de segredos.
* **Dependência Externa:** A funcionalidade do projeto depende da disponibilidade e do desempenho da API da OpenAI.

---

## 👥 Membros do Grupo ProcessON

* Aurilene Ribeiro
* Eduardo Orlando
* Eric Bueno
* Felipe Moura
* João Vitor
* Leonardo Santos
* Letícia Machado
* Marco Andrey
* Pascual Matheo
* Sandro Costa

---

## 🤝 Contribuição

Contribuições são bem-vindas! Se você tiver sugestões para melhorias ou novos recursos, sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.

---

## 📄 Licença

Este projeto é de código aberto e está disponível sob a [Licença MIT](LICENSE.txt).