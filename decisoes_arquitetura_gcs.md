# Registro de Decisões de Arquitetura & Entrevista Técnica (Grill-Me)

Este documento registra todas as perguntas, análises de trade-offs, recomendações e decisões tomadas durante a entrevista de alinhamento técnico para a substituição do `EnvironmentToolset` pelo `GCSToolset` no **agente-estudos**.

---

## Pergunta 1: Definição e Gerenciamento do Bucket GCS
* **Contexto:** Ao interagir com o Google Cloud Storage via `GCSToolset`, as ferramentas de leitura e escrita precisam saber em qual bucket operar.
* **Opções avaliadas:**
  1. *(Recomendada)* Ler o nome do bucket via variável de ambiente (`GCS_BUCKET_NAME`), com fallback e configurável via `.env`.
  2. Criar o bucket automaticamente via código/script caso ele não exista.
  3. Informar um bucket fixo e pré-existente no código.
* **Decisão:** Configurar via variável de ambiente `GCS_BUCKET_NAME` no arquivo `.env` (com padrão `agente-estudos-planos`). O agente é orientado via instrução do sistema a usar esse bucket.
* **Justificativa:** Flexibilidade total entre ambientes (desenvolvimento local, testes, produção no Cloud Shell ou Cloud Run), sem acoplar credenciais ou nomes fixos no código-fonte.

---

## Pergunta 2: Ferramentas do GCSToolset a serem Expostas
* **Contexto:** O `GCSToolset` com capacidades de leitura e escrita expõe por padrão 5 ferramentas (`create_object`, `get_object_data`, `get_object_metadata`, `list_objects`, `delete_objects`).
* **Opções avaliadas:**
  1. *(Recomendada)* Expor apenas `create_object` e `get_object_data` usando o parâmetro `tool_filter`.
  2. Incluir também `list_objects`.
  3. Expor todas as 5 ferramentas.
* **Decisão:** Expor **apenas** `create_object` e `get_object_data`.
* **Justificativa:** Princípio do menor privilégio (*least privilege*). Garante paridade estrita com o comportamento anterior (`WriteFile` e `ReadFile`), impedindo que o agente execute operações destrutivas (`delete_objects`) ou se disperse listando o bucket desnecessariamente.

---

## Pergunta 3: Nomenclatura e Estrutura dos Arquivos no Bucket
* **Contexto:** Como o arquivo CSV deve ser salvo e localizado dentro do bucket.
* **Opções avaliadas:**
  1. *(Recomendada)* Salvar na raiz com o nome fixo `plano-de-estudos.csv`.
  2. Salvar com prefixo de tópico (ex: `plano-de-estudos-{topico}.csv`).
  3. Salvar em pastas por usuário (ex: `users/{user_id}/plano-de-estudos.csv`).
* **Decisão:** Salvar fixo na raiz como `plano-de-estudos.csv`.
* **Justificativa:** Mantém compatibilidade direta e descomplicada com a skill `plano-de-estudos`. Durante o replanejamento, o agente sabe exatamente qual arquivo sobrescrever, sem necessidade de lógica de resolução de caminhos dinâmicos.

---

## Pergunta 4: Resiliência e Fallback em Caso de Falha no GCS
* **Contexto:** Se a API do GCS falhar (ex: bucket inexistente, falta de permissão IAM ou falha de rede), qual deve ser a postura do agente frente ao usuário?
* **Opções avaliadas:**
  1. *(Recomendada)* Fallback gracioso: emitir uma breve mensagem sobre a falha no armazenamento em nuvem e exibir o conteúdo do CSV completo diretamente em um bloco Markdown (```` ```csv ````).
  2. Erro rígido: interromper a resposta informando a falha de armazenamento sem entregar o CSV.
* **Decisão:** Fallback gracioso com exibição do CSV em Markdown na resposta.
* **Justificativa:** O valor principal entregue ao estudante é o plano de estudos. O estudante não deve perder o cronograma gerado caso ocorra uma instabilidade transitória de infraestrutura de nuvem.

---

## Pergunta 5: Tratamento do Diretório Local `planos/`
* **Contexto:** O `EnvironmentToolset` exigia um diretório local com caminho absoluto (`agente-estudos/planos/`) para gravar os arquivos. Com a migração para nuvem (GCS), o armazenamento local torna-se obsoleto.
* **Opções avaliadas:**
  1. *(Recomendada)* Manter `planos/` no `.gitignore` para segurança de dados pessoais legados, mas remover a obrigatoriedade da sua criação no código (`agent.py`).
  2. Deletar a pasta e sua referência no `.gitignore`.
  3. Manter gravação dupla (local + GCS).
* **Decisão:** Manter no `.gitignore` como proteção preventiva, mas desacoplar o código de qualquer dependência de sistema de arquivos local.
* **Justificativa:** Limpeza de código e independência de disco local (o que facilita imensamente o deploy futuro em contêineres e serverless onde o sistema de arquivos é efêmero).
