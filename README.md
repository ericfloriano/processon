# 🧠 ProcessON - I2A2

Este projeto oferece uma interface interativa para processar e consultar dados de múltiplos arquivos CSV contidos em um arquivo ZIP. Ele aproveita o poder dos Modelos de Linguagem Grandes (LLMs) via biblioteca `dspy` para responder a perguntas em linguagem natural sobre os dados carregados, e `Gradio` para uma interface web amigável.

---

## 🎯 Contexto do Desafio I2A2

Esta atividade faz parte do curso I2A2 e tem como objetivo principal **criar um ou mais agentes que permitam a um usuário realizar perguntas sobre arquivos CSV disponibilizados**.

Por exemplo, os usuários podem perguntar:
* "Qual é o fornecedor que teve maior montante recebido?"
* "Qual item teve maior volume entregue (em quantidade)?"
* E assim por diante, explorando os dados de forma conversacional.

### Recursos Utilizados

Para este desafio, é fornecido um arquivo chamado `202401_NFs.zip`. Este arquivo contém:

* **`202401_NFs_Cabecalho.csv`**: O cabeçalho de 100 notas fiscais selecionadas aleatoriamente do arquivo de notas fiscais do mês de janeiro/2024, disponibilizado pelo Tribunal de Contas da União.
* **`202401_NFs_Itens.csv`**: Os itens correspondentes das 100 notas fiscais selecionadas.

---

## 🚀 Primeiros Passos

Siga estas instruções para configurar e executar o projeto localmente.

### Pré-requisitos

Antes de começar, certifique-se de ter o seguinte instalado:

* **Python 3.8+**
* **pip** (instalador de pacotes Python)

### Instalação

1.  **Clone o repositório (ou salve o código):**
    Se o seu código estiver em um arquivo, salve-o como `app.py` (ou qualquer outra extensão `.py`). Se for parte de um repositório Git, clone-o:
    ```bash
    git clone <url_do_seu_repositorio>
    cd <diretorio_do_seu_repositorio>
    ```

2.  **Instale os pacotes Python necessários:**
    Crie um arquivo `requirements.txt` no mesmo diretório do seu script Python com o seguinte conteúdo:

    ```
    openai
    pandas
    gradio
    dspy-ai
    ```

    Em seguida, instale-os usando pip:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure sua Chave de API OpenAI:**
    A aplicação requer uma chave de API OpenAI para interagir com o modelo GPT.
    Você precisa definir a variável `openai.api_key` em seu código. **Substitua o placeholder pela sua chave de API real:**

    ```python
    openai.api_key = "SUA_CHAVE_DE_API_OPENAI_AQUI"
    ```
    **Importante:** Para ambientes de produção, é altamente recomendável usar variáveis de ambiente para armazenar sua chave de API por motivos de segurança (por exemplo, `os.environ.get("OPENAI_API_KEY")`).

---

## 🛠️ Como Usar

1.  **Execute a aplicação:**
    Abra seu terminal ou prompt de comando, navegue até o diretório do projeto e execute o script Python:
    ```bash
    python app.py
    ```

2.  **Acesse a interface web:**
    Você pode acessar a interface do Gradio localmente (o link será exibido no seu terminal, geralmente `http://127.0.0.1:7860`) ou através do link de compartilhamento público fornecido abaixo.

    ---
    **Link para acessar a interface do Gradio e fazer perguntas a respeito dos dados carregados:**
    [https://9cd92c0aa2a947883d.gradio.live/](https://9cd92c0aa2a947883d.gradio.live/)
    ---

3.  **Envie seu arquivo ZIP:**
    Na interface do Gradio, clique no componente "Faça upload do arquivo ZIP" e selecione um arquivo `.zip` contendo um ou mais arquivos CSV (como o `202401_NFs.zip` mencionado no contexto do desafio).

4.  **Processe o arquivo ZIP:**
    Clique no botão "Processar ZIP". A aplicação extrairá os CSVs e os carregará em DataFrames do pandas. A caixa de texto "Status" mostrará quantos arquivos CSV foram carregados.

5.  **Faça perguntas:**
    Depois que os CSVs forem carregados, você pode digitar suas perguntas sobre os dados na caixa de texto "Pergunta sobre os dados" e pressionar Enter (ou clicar fora da caixa de texto). A IA fornecerá uma resposta na caixa de texto "Resposta IA", utilizando os dados carregados como contexto.

---

## ⚙️ Como Funciona

A aplicação combina várias bibliotecas poderosas para alcançar sua funcionalidade:

* **`zipfile` e `shutil`:** Usados para manipulação de arquivos ZIP, extração e gerenciamento de diretórios temporários.
* **`pandas`:** Essencial para ler e manipular dados CSV, armazenando-os em DataFrames.
* **`openai` e `dspy`:**
    * `openai` fornece a interface direta para a API da OpenAI.
    * `dspy` (Declarative Self-improving Language Programs) é usado para estruturar a engenharia de prompt e a interação com o LLM. Ele define uma `Signature` (`AskCSV`) que especifica claramente as entradas (`question`, `context`) e a saída (`answer`), tornando a tarefa do LLM bem definida.
    * O `AskCSVModule` encapsula essa `Signature` para fácil invocação.
    * O modelo `gpt-4.1-mini` é configurado com uma `temperature` baixa (0.0) para respostas mais determinísticas e factuais, e um `max_tokens` alto (20000) para permitir respostas abrangentes.
* **`gradio`:** Fornece a interface web amigável. Ele simplifica a criação de componentes interativos para upload de arquivos, entradas de texto e botões, conectando-os às funções Python de backend.

### Lógica Central

1.  **Upload e Processamento de Arquivos (`process_zip`):**
    * Quando um usuário faz upload de um arquivo ZIP, ele é salvo temporariamente e extraído para o diretório `uploaded_data`.
    * A função então percorre os arquivos extraídos, identificando e lendo todos os arquivos `.csv` em DataFrames do pandas.
    * Uma coluna `__source_file` é adicionada a cada DataFrame para rastrear sua origem.
    * Esses DataFrames são armazenados globalmente em `global_dataframes`.

2.  **Resposta a Perguntas (`ask_question`):**
    * Quando um usuário envia uma pergunta, a função primeiro verifica se algum CSV foi carregado.
    * Em seguida, ela constrói um `context` pegando as 10 primeiras linhas de cada DataFrame carregado e convertendo-as em representações de string. Este contexto é fornecido ao LLM.
    * O módulo `dspy` (`ask_module`) é invocado com a `question` do usuário e o `context` gerado.
    * O LLM processa essas informações e gera uma `answer`, que é então exibida na interface do Gradio.

---

## 🛑 Limitações

* **Context Window Limit:** Embora `gpt-4.1-mini` tenha uma grande janela de contexto, alimentar o conteúdo inteiro de CSVs muito grandes pode excedê-la. Atualmente, apenas as 10 primeiras linhas de cada DataFrame são usadas como contexto. Para conjuntos de dados maiores, seria necessária uma recuperação de contexto mais sofisticada (por exemplo, usando embeddings e bancos de dados vetoriais).
* **Interpretação de Dados:** A qualidade da resposta da IA depende muito da clareza da pergunta e da representatividade do contexto fornecido.
* **Segurança:** Armazenar chaves de API diretamente no código não é recomendado para ambientes de produção.

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

Este projeto é de código aberto e está disponível sob a [Licença MIT](LICENSE) (se você tiver uma, caso contrário, remova esta seção).