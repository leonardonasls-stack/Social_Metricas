# CHANGELOG

Todas as alterações notáveis deste projeto serão documentadas neste arquivo.

O formato segue as diretrizes do [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adota o [Versionamento Semântico (SemVer)](https://semver.org/lang/pt-BR/).

---

## [1.2.0] - 2026-11-12

### Commit
- `1fe5fd3` - *feat(intelligence): anti-hallucination pipelines, deterministic metric calculation and RICE legend*

### Adicionado
- **Rigor Anti-Alucinação em LLMs:** Prompt de orquestração revisado (`llm_orchestrator.py`) com proibição expressa de depoimentos falsos ou inventados; citações devem ser extraídas exclusivamente das discussões públicas mineradas mantendo formato `[origem | @autor]`.
- **Cálculo Determinístico de Incidência:** A incidência das dores (`frequency_percentage`) agora é computada no Python com base na proporção real de citações associadas em relação ao total da amostra minerada (`len(mined_comments)`), eliminando números aleatórios criados pelas IAs.
- **Higienização de Queries de Mineração:** Nova função `clean_search_term` no pré-processador (`preprocessor.py`) que remove stop-words e termos periféricos repetitivos antes de consultar as APIs do Reddit, YouTube e TikTok, garantindo foco cirúrgico no núcleo do problema.
- **Legenda e Contextualização do RICE Score:**
  - Inserção de indicador asterisco (`*`) na seção `3. Matriz de Features com RICE Score*` e no cabeçalho `RICE*`.
  - Inclusão de nota em letras miúdas no rodapé da tabela (tanto no PDF Typst nativo quanto no Dossiê Markdown) detalhando a fórmula $(R \times I \times C) / E$, criador do framework (Intercom) e significado de cada variável (*Reach*, *Impact*, *Confidence*, *Effort*).
- **Isolamento de Cache por Modo:** Query de busca no PostgreSQL atualizada para respeitar `Analysis.mode == requested_mode`, prevenindo que análises em modo `live` recuperem dados antigos gerados em modo `mock`.

### Modificado
- Terminologia nos relatórios ajustada de *"Incidência Estimada: X% das menções"* para *"Incidência Mapeada: X% das discussões qualificadas"*.
- Descrição de impacto financeiro ajustada de *"⚠️ Impacto Financeiro na Operação"* para *"⚠️ Impacto Operacional & Negócio"*, priorizando mecanismos reais de perda e conformidade em vez de cálculos matemáticos forçados.

---

## [1.1.1] - 2026-11-12

### Commit
- `60617ef` - *fix(typst): adiciona escape de caracteres < e > para evitar erro de unclosed label*

### Corrigido
- Tratamento de caracteres especiais no compilador Typst (`typst_service.py`), adicionando escape seguro para `<` e `>` para evitar que tags HTML ou menções acidentais quebrem a compilação de PDFs nativos.

---

## [1.1.0] - 2026-11-12

### Commit
- `267ab2b` - *feat: aprimora mineracao social com Reddit/TikTok, expansao de query e persistencia aprofundada*

### Adicionado
- Integração multi-plataforma real de mineração social via ScrapeCreators cobrindo Reddit, YouTube e TikTok.
- Algoritmo de expansão de busca (`expand_queries`) e cálculo de relevância/sentimento de dores em comentários públicos.
- Seção 3.1 de especificação de engenharia (User Stories, Critérios de Aceite e notas arquiteturais) nos relatórios executivos.

---

## [1.0.1] - 2026-11-11

### Commits
- `5ee7c88` - *docs: ajuste de quebra de linha no README.md*
- `379febf` - *docs: adiciona README.md completo da aplicacao seguindo melhores praticas*

### Documentação
- Criação e refinamento do `README.md` principal do repositório com arquitetura, guia de instalação, variáveis de ambiente e endpoints.

---

## [1.0.0] - 2026-11-11

### Commit
- `3606196` - *chore: wipe mock data files and clean up database*

### Inicial
- Estrutura base da API FastAPI com suporte assíncrono ao PostgreSQL e compilação de dossiês em Typst Engine.
- Interface em Vue 3 + Tailwind CSS para navegação de nichos e visualização de dores de mercado.
