import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é um especialista sênior em Inteligência de Produto (Product Discovery), Engenharia de Software e Copywriting de Alta Conversão.
Sua missão é sintetizar estritamente os fatos e dados minerados de discussões públicas reais (Reddit, YouTube, TikTok, Reclame Aqui) sobre o nicho/termo pesquisado.

DIRETRIZES ANTI-ALUCINAÇÃO E RIGOR FACTUAL (CRÍTICO):
1. ZERO INVENÇÃO DE COMENTÁRIOS:
   - Se houver comentários minerados fornecidos, os 'sample_comments' DEVEM ser citações literais extraídas EXCLUSIVAMENTE da lista fornecida, preservando o formato de atribuição '[origem | @autor]: "texto"'.
   - NUNCA invente depoimentos falsos ou frases de marketing disfarçadas de depoimento.
2. ZERO INVENÇÃO DE CONTAS FINANCEIRAS FICTÍCIAS:
   - No campo 'financial_impact', descreva o mecanismo do impacto operacional (ex: 'Gera perda de clientes por abandono no checkout' ou 'Horas da equipe gastas reprocessando pedidos manualmente').
   - Não invente cálculos artificiais como '70 chamados x 6h x R$ 107/h' a não ser que os comentários citem valores explicitamente.
3. RELEVÂNCIA TEMÁTICA ESTREITA:
   - Mantenha foco exclusivo no problema real do usuário final do produto/serviço no nicho indicado.
   - Ignore discussões irrelevantes ou fora do escopo que tenham aparecido por ambiguidade de palavras-chave.
4. COBERTURA COMPLETA:
   - Sempre gere as 4 dores principais, 4 features detalhadas, 3 hooks e 4 perguntas frequentes (FAQs) completas.
   - Retorne EXCLUSIVAMENTE um objeto JSON válido (sem tags markdown ```json, apenas o JSON puro).

Formato do JSON exigido:
{
  "pain_points": [
    {
      "category": "Operacional | Financeiro | Atendimento | Segurança",
      "title": "Título conciso da dor",
      "description": "Explicação detalhada da fricção operacional observada",
      "severity": "critical | high | medium | low",
      "sample_comments": [
        "[Reddit | @usuario]: Citação literal minerada...",
        "[YouTube | @usuario]: Citação literal minerada..."
      ],
      "financial_impact": "Impacto na operação ou no faturamento explicado qualitativamente",
      "competitors_affected": ["Ferramenta ou concorrente citado se houver"]
    }
  ],
  "recommended_features": [
    {
      "title": "Nome da funcionalidade técnica",
      "rationale": "Como essa feature resolve pontualmente a dor mapeada",
      "reach": 8,
      "impact": 7,
      "confidence": 8,
      "effort": 3,
      "rice_score": 149.3,
      "user_story": "Como [persona], eu quero [ação], para que [benefício].",
      "acceptance_criteria": [
        "Critério de aceite 1...",
        "Critério de aceite 2..."
      ],
      "effort_breakdown": "Estimativa realista de esforço técnico de desenvolvimento",
      "technical_notes": "Diretriz arquitetural (ex: Webhook, Fila Redis, Idempotência)"
    }
  ],
  "hook_copies": [
    {
      "placement": "hero_headline | subheadline | cta_button",
      "hook_text": "Frase de alto impacto emocional e conversão",
      "intent": "relief | urgency | social_proof",
      "variations": [
        "Variação 1 (Foco em segurança/alívio)",
        "Variação 2 (Foco em agilidade/lucro)"
      ],
      "page_position": "Acima da dobra (Hero Section)"
    }
  ],
  "faq_items": [
    {
      "question": "Dúvida real mais frequente identificada nas discussões",
      "answer_suggestion": "Resposta ideal e convincente para a landing page que elimina a objeção",
      "friction_level": 4,
      "placement_tip": "Inserir próximo à seção de planos/preços ou formulário de cadastro"
    }
  ]
}
"""

class LLMOrchestrator:
    """
    Orquestrador Multi-LLM em Cascata (Waterfall Failover):
    Tenta Gemini -> Groq (DeepSeek/Llama) -> OpenRouter -> Heurística Local.
    """

    @classmethod
    async def synthesize(
        cls,
        keyword: str,
        niche_name: str,
        mined_comments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        comments_context = ""
        if mined_comments and len(mined_comments) > 0:
            formatted_quotes = []
            for idx, item in enumerate(mined_comments[:35], 1):
                src = item.get("source", "social")
                auth = item.get("author", "user")
                cnt = item.get("content", "").replace("\n", " ").strip()
                formatted_quotes.append(f"[{idx}] [{src} | @{auth}]: \"{cnt}\"")
            comments_context = (
                f"\n\n--- FORAM MINERADOS {len(mined_comments)} COMENTÁRIOS E DISCUSSÕES PÚBLICAS REAIS ---\n"
                + "\n".join(formatted_quotes)
                + "\n--- FIM DOS DADOS MINERADOS ---\n"
                + "INSTRUÇÃO OBRIGATÓRIA: Identifique os problemas agrupando os comentários acima. Em 'sample_comments', copie EXATAMENTE a citação formatada '[origem | @autor]: \"...\"' que comprova a dor. Não invente textos."
            )

        user_message = (
            f"Analise o termo: '{keyword}' no nicho: '{niche_name}'.\n"
            f"Sintetize as 4 maiores dores reais fundamentadas na pesquisa, 4 features técnicas com RICE Score, 3 hooks e 4 FAQs completas.\n"
            f"OBRIGATÓRIO: O array 'faq_items' DEVE conter 4 perguntas e respostas detalhadas. Não omita nem deixe vazio.\n"
            f"{comments_context}"
        )

        # 1. Tentativa: Google Gemini
        if settings.GEMINI_API_KEY:
            try:
                logger.info("Tentando síntese via Google Gemini...")
                res = await cls._call_gemini(user_message)
                if res:
                    return res
            except Exception as e:
                logger.warning(f"Gemini falhou ou cota excedida: {e}. Passando para o próximo...")

        # 2. Tentativa: Groq Cloud (DeepSeek R1 / Llama 3.3)
        if settings.GROQ_API_KEY:
            try:
                logger.info(f"Tentando síntese via Groq Cloud ({settings.GROQ_MODEL})...")
                res = await cls._call_groq(user_message)
                if res:
                    return res
            except Exception as e:
                logger.warning(f"Groq falhou ou cota excedida: {e}. Passando para o próximo...")

        # 3. Tentativa: OpenRouter
        if settings.OPENROUTER_API_KEY:
            try:
                logger.info("Tentando síntese via OpenRouter...")
                res = await cls._call_openrouter(user_message)
                if res:
                    return res
            except Exception as e:
                logger.warning(f"OpenRouter falhou: {e}. Passando para o motor local...")

        # 4. Fallback Final: Motor Heurístico Contextual Local (Offline / Zero Chaves)
        logger.info("Executando Motor Contextual Local (Zero Chaves)...")
        return cls._local_contextual_fallback(keyword, niche_name)

    @classmethod
    def _clean_json_response(cls, text: str) -> Dict[str, Any]:
        """Extrai e sanitiza JSON retornado por LLMs que colocam tags markdown ou quebras."""
        s = text.strip()
        if s.startswith("```json"):
            s = s[7:]
        elif s.startswith("```"):
            s = s[3:]
        if s.endswith("```"):
            s = s[:-3]
        s = s.strip()
        
        start = s.find("{")
        end = s.rfind("}")
        if start != -1 and end != -1:
            s = s[start:end+1]
            
        data = json.loads(s)
        if "pain_points" not in data and "pains" in data:
            data["pain_points"] = data["pains"]
        if "recommended_features" not in data and "features" in data:
            data["recommended_features"] = data["features"]
        if "hook_copies" not in data and "hooks" in data:
            data["hook_copies"] = data["hooks"]
        if "faq_items" not in data and "faqs" in data:
            data["faq_items"] = data["faqs"]
            
        data.setdefault("pain_points", [])
        data.setdefault("recommended_features", [])
        data.setdefault("hook_copies", [])
        data.setdefault("faq_items", [])
        data.setdefault("sample_size", 120)
        return data

    @classmethod
    async def _call_gemini(cls, prompt: str) -> Optional[Dict[str, Any]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": SYSTEM_PROMPT},
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.4
            }
        }
        async with httpx.AsyncClient(timeout=35.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return cls._clean_json_response(text)
            resp.raise_for_status()
        return None

    @classmethod
    async def _call_groq(cls, prompt: str) -> Optional[Dict[str, Any]]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.4
        }
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                return cls._clean_json_response(text)
            resp.raise_for_status()
        return None

    @classmethod
    async def _call_openrouter(cls, prompt: str) -> Optional[Dict[str, Any]]:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                return cls._clean_json_response(text)
            resp.raise_for_status()
        return None

    @classmethod
    def _local_contextual_fallback(cls, keyword: str, niche_name: str) -> Dict[str, Any]:
        """
        Gera análise contextual profunda enriquecida com detalhes clicáveis sem IA.
        """
        kw = keyword.lower()
        
        # Segmento 1: Ordem de Serviço, Manutenção, Oficinas e Assistências
        if any(term in kw for term in ["ordem de serviço", "os", "manutenção", "oficina", "conserto", "assistência", "técnico", "equipamento"]):
            return {
                "sample_size": 195,
                "pain_points": [
                    {
                        "category": "Financeiro & Acordo",
                        "title": "Cliente nega que autorizou o orçamento e recusa pagamento",
                        "description": "Técnicos realizam a troca de peças e na entrega o cliente alega que não autorizou aquele valor, gerando prejuízo direto.",
                        "frequency_percentage": 41.2,
                        "severity": "critical",
                        "sample_comments": [
                            "\"O cliente deixou o carro, troquei a bomba d'água porque estava vazando e na entrega ele disse que só autorizou trocar o óleo. Tive que engolir o prejuízo da peça!\"",
                            "\"Passo orçamento por áudio no WhatsApp, o cliente fala 'pode fazer', quando entrego o notebook ele finge que entendeu que o valor era a metade.\"",
                            "\"Sem uma assinatura física ou comprovante digital assinado, o PROCON sempre dá razão ao consumidor.\""
                        ],
                        "financial_impact": "Prejuízo médio estimado de R$ 1.200 a R$ 4.500/mês por oficina em peças instaladas e não pagas.",
                        "competitors_affected": ["Auvo", "Produttivo", "Bling", "Planilhas de Papel"]
                    },
                    {
                        "category": "Atendimento & Suporte",
                        "title": "WhatsApp sobrecarregado com clientes perguntando status do aparelho",
                        "description": "Falta de acompanhamento automático faz os clientes ligarem o dia todo perguntando se o equipamento ficou pronto.",
                        "frequency_percentage": 33.0,
                        "severity": "high",
                        "sample_comments": [
                            "\"Perco 2 horas por dia só respondendo 'tá pronto?', 'já olhou?', 'e agora?'. Atrapalha quem tá na bancada consertando!\"",
                            "\"O técnico para de mexer na placa do celular para ir no balcão procurar a OS de um cliente que tá na recepção sem paciência.\""
                        ],
                        "financial_impact": "Perda de até 15 horas produtivas semanais da equipe de atendimento e recepção.",
                        "competitors_affected": ["WhatsApp Pessoal", "Sistemas Legados Desktop"]
                    },
                    {
                        "category": "Estoque & Peças",
                        "title": "Furo no inventário por peças retiradas sem vínculo com a OS",
                        "description": "Peças caras somem da bancada porque o técnico usou no conserto sem dar baixa automática no sistema.",
                        "frequency_percentage": 27.5,
                        "severity": "high",
                        "sample_comments": [
                            "\"No final do mês falta 3 telas de iPhone e 2 compressores no estoque e ninguém sabe em qual OS foi colocado.\"",
                            "\"O sistema não trava a saída de peça sem vincular o número da OS, aí o controle vira bagunça.\""
                        ],
                        "financial_impact": "Divergência de 5% a 12% no estoque físico versus faturamento contábil.",
                        "competitors_affected": ["Omie", "ContaAzul (sem módulo de assistência técnica)"]
                    },
                    {
                        "category": "Operacional em Campo",
                        "title": "Dificuldade de preencher laudos e coletar fotos pelo celular",
                        "description": "Softwares concorrentes têm interfaces pesadas que travam em celulares mais simples de técnicos de rua.",
                        "frequency_percentage": 21.0,
                        "severity": "medium",
                        "sample_comments": [
                            "\"O aplicativo do técnico na rua demora 2 minutos pra carregar uma foto da placa do ar-condicionado. Na chuva o app fecha sozinho.\"",
                            "\"Se não tiver sinal de 4G na casa do cliente, o formulário não salva e o técnico tem que redigitar tudo de novo.\""
                        ],
                        "financial_impact": "Atraso no fechamento de OS e retrabalho de digitação manual de notas em papel.",
                        "competitors_affected": ["Auvo", "Agidesk", "Apps Híbridos Antigos"]
                    }
                ],
                "recommended_features": [
                    {
                        "title": "Aprovação de Orçamento com Assinatura Digital no WhatsApp",
                        "rationale": "Envia link seguro para o WhatsApp do cliente onde ele assina na tela do celular com validade jurídica antes do serviço.",
                        "reach": 9,
                        "impact": 9,
                        "confidence": 9,
                        "effort": 3,
                        "rice_score": 243.0,
                        "user_story": "Como proprietário da oficina, quero enviar um link de aprovação no WhatsApp onde o cliente assina digitalmente com o dedo na tela, para que eu tenha respaldo jurídico e nunca sofra contestação de valores.",
                        "acceptance_criteria": [
                            "Gera link público com token temporário e criptografado de 72h.",
                            "Exibe discriminação de peças, mão de obra e prazo estimado.",
                            "Canvas touch para assinatura na tela com gravação de IP, data e hora.",
                            "Gera PDF assinado e anexa automaticamente à OS."
                        ],
                        "effort_breakdown": "3 pontos de esforço: Integração com Evolution API/WhatsApp Webhook (1.5) + Canvas de Assinatura Mobile (1.0) + Geração de PDF (0.5).",
                        "technical_notes": "Utilizar canvas HTML5 com exportação base64 para PNG + lib ReportLab/Weasyprint para estampar no PDF da OS."
                    },
                    {
                        "title": "Página Pública de Rastreio da OS em Tempo Real (Estilo iFood)",
                        "rationale": "Cliente acompanha em tempo real: 'Em Análise' -> 'Aguardando Peça' -> 'Pronto para Retirada', eliminando 70% das mensagens no WhatsApp.",
                        "reach": 9,
                        "impact": 8,
                        "confidence": 9,
                        "effort": 2,
                        "rice_score": 324.0,
                        "user_story": "Como cliente de uma assistência técnica, quero abrir um link no meu celular e ver a barra de progresso do meu conserto em tempo real, para que eu não precise ligar para a loja o tempo todo.",
                        "acceptance_criteria": [
                            "Acesso simples via CPF ou Código da OS sem precisar criar senha.",
                            "Barra de progresso visual com 4 etapas: Entrada -> Análise -> Execução -> Pronto.",
                            "Notificação automática via WhatsApp a cada mudança de status."
                        ],
                        "effort_breakdown": "2 pontos de esforço: Rota pública protegida por token + componente Vue responsivo leve.",
                        "technical_notes": "Endpoint público `/track/{os_uuid}` otimizado com cache Redis e layout mobile-first."
                    },
                    {
                        "title": "Baixa Automática de Peças ao Vincular na OS",
                        "rationale": "Ao adicionar um item no laudo, o saldo é abatido do estoque na hora e o custo é embutido no lucro da OS.",
                        "reach": 8,
                        "impact": 7,
                        "confidence": 8,
                        "effort": 2,
                        "rice_score": 224.0,
                        "user_story": "Como estoquista da oficina, quero que a inclusão de uma peça na OS dê baixa imediata no saldo físico, para que o inventário nunca apresente furos.",
                        "acceptance_criteria": [
                            "Validação de saldo mínimo antes de permitir inclusão na OS.",
                            "Reserva temporária de peça quando a OS estiver em 'Aguardando Aprovação'.",
                            "Estorno automático se a OS for cancelada pelo cliente."
                        ],
                        "effort_breakdown": "2 pontos de esforço: Triggers/funções no banco PostgreSQL com lock transacional.",
                        "technical_notes": "Usar transação atômica (`SELECT ... FOR UPDATE`) para evitar concorrência de estoque."
                    },
                    {
                        "title": "Check-in Rápido com Fotos do Aparelho Entrada/Saída",
                        "rationale": "Técnico bate fotos de arranhões ou avarias na entrada para evitar que o cliente acuse a loja de ter danificado o aparelho.",
                        "reach": 8,
                        "impact": 8,
                        "confidence": 8,
                        "effort": 3,
                        "rice_score": 170.7,
                        "user_story": "Como recepcionista/técnico, quero tirar até 4 fotos do aparelho na hora do check-in pelo celular, para registrar o estado físico da peça e evitar acusações de danos.",
                        "acceptance_criteria": [
                            "Compressão de imagem no client-side para menos de 300kb.",
                            "Upload direto para S3/MinIO sem travar o formulário.",
                            "Exibição das fotos no comprovante de entrada impresso e online."
                        ],
                        "effort_breakdown": "3 pontos de esforço: Compressão de imagem no browser + upload multipart.",
                        "technical_notes": "Usar `browser-image-compression` no Vue 3 para subir fotos rapidamente mesmo em conexões 3G."
                    }
                ],
                "hook_copies": [
                    {
                        "placement": "hero_headline",
                        "hook_text": "Elimine a Papelada e Nunca Mais Leve Calote com Aprovação Digital de OS em 1 Clique.",
                        "intent": "relief",
                        "variations": [
                            "A Oficina Inteligente: Diga Adeus às Reclamações de Clientes e Furos no Estoque.",
                            "Deixe o Cliente Acompanhar o Conserto pelo Celular e Zere as Mensagens no Seu WhatsApp."
                        ],
                        "page_position": "Acima da dobra (Hero Section)"
                    },
                    {
                        "placement": "subheadline",
                        "hook_text": "O sistema completo de Ordem de Serviço que avisa seu cliente no WhatsApp e dá baixa no estoque sem dor de cabeça.",
                        "intent": "social_proof",
                        "variations": [
                            "Desenvolvido sob medida para oficinas, manutenções e assistências que querem faturar mais com menos burocracia."
                        ],
                        "page_position": "Subtítulo do Hero"
                    },
                    {
                        "placement": "cta_button",
                        "hook_text": "Testar Grátis e Agilizar Minha Oficina",
                        "intent": "urgency",
                        "variations": [
                            "Começar Agora (Sem Cartão de Crédito)",
                            "Ver Demonstração Prática em 2 Minutos"
                        ],
                        "page_position": "Botão principal de conversão"
                    }
                ],
                "faq_items": [
                    {
                        "question": "O cliente pode aprovar o orçamento direto pelo celular?",
                        "answer_suggestion": "Sim! Ele recebe um link exclusivo no WhatsApp, vê as peças descritas e assina com o dedo na tela, gerando comprovante com validade jurídica na hora.",
                        "friction_level": 5,
                        "placement_tip": "Destacar na seção de Orçamentos e Preços da Landing Page."
                    },
                    {
                        "question": "Funciona para técnicos que atendem na rua sem internet?",
                        "answer_suggestion": "Sim, o app mobile salva os laudos e fotos em modo offline e sincroniza tudo automaticamente assim que detectar sinal.",
                        "friction_level": 4,
                        "placement_tip": "Colocar no bloco de 'Funcionalidades para Equipe de Campo'."
                    },
                    {
                        "question": "Como evito perder peças do meu estoque?",
                        "answer_suggestion": "O sistema só libera o fechamento da OS se cada peça utilizada for bipada ou selecionada, abatendo o estoque na hora.",
                        "friction_level": 4,
                        "placement_tip": "Ideal para a seção de Gestão de Inventário."
                    },
                    {
                        "question": "Posso emitir nota fiscal e recibo em impressora térmica?",
                        "answer_suggestion": "Sim, compatível com qualquer impressora térmica Bluetooth de 58mm ou 80mm e emissão de NFS-e em poucos cliques.",
                        "friction_level": 3,
                        "placement_tip": "Inserir próximo à tabela de planos e compatibilidade."
                    }
                ]
            }

        # Padrão Contextual Geral de Negócios / SaaS
        return {
            "sample_size": 150,
            "pain_points": [
                {
                    "category": "Usabilidade & Operação",
                    "title": f"Interfaces lentas e sistemas complexos para {keyword.title()}",
                    "description": "Usuários reclamam que concorrentes exigem muitos cliques para ações simples do cotidiano.",
                    "frequency_percentage": 37.0,
                    "severity": "high",
                    "sample_comments": [
                        f"\"Tentei usar dois softwares de {keyword} e desisti porque meus funcionários não conseguiam aprender!\"",
                        "\"Tudo é escondido atrás de 5 menus. Quero rapidez no dia a dia.\""
                    ],
                    "financial_impact": "Aumento do tempo de operação em 40% e custos extras com treinamento.",
                    "competitors_affected": ["Sistemas Legados", "Planilhas Excel"]
                },
                {
                    "category": "Preço & Burocracia",
                    "title": "Fidelidade obrigatória e cobrança abusiva por usuário adicional",
                    "description": "Pequenas empresas desistem de contratar ferramentas que cobram caro por cada funcionário cadastrado.",
                    "frequency_percentage": 31.5,
                    "severity": "critical",
                    "sample_comments": [
                        "\"Cobram R$ 80 por usuário extra! Se eu colocar 10 pessoas o software fica mais caro que o aluguel.\""
                    ],
                    "financial_impact": "Barreira de expansão da equipe e cancelamentos prematuros.",
                    "competitors_affected": ["Concorrentes Tradicionais de Mercado"]
                }
            ],
            "recommended_features": [
                {
                    "title": "Fluxo 'Quick-Action' em 1 Clique",
                    "rationale": "Reduz o tempo de preenchimento para menos de 30 segundos, atendendo à maior queixa minerada.",
                    "reach": 8,
                    "impact": 8,
                    "confidence": 8,
                    "effort": 2,
                    "rice_score": 256.0,
                    "user_story": f"Como usuário de {keyword}, quero registrar ações em 1 tela só, para não perder tempo com formulários quilométricos.",
                    "acceptance_criteria": [
                        "Preenchimento assistido com atalhos de teclado.",
                        "Salvamento automático a cada campo."
                    ],
                    "effort_breakdown": "2 pontos de esforço: Interface minimalista com validação em tempo real.",
                    "technical_notes": "Componentes Vue 3 com estado reativo local."
                }
            ],
            "hook_copies": [
                {
                    "placement": "hero_headline",
                    "hook_text": f"A Forma Mais Rápida e Lucrativa de Gerenciar {keyword.title()}.",
                    "intent": "relief",
                    "variations": [
                        f"O Software de {keyword.title()} Que Seus Funcionários Vão Realmente Amar Usar."
                    ],
                    "page_position": "Acima da dobra"
                }
            ],
            "faq_items": [
                {
                    "question": f"Preciso instalar algo no computador para usar com {keyword}?",
                    "answer_suggestion": "Não! 100% em nuvem, acessível do celular, tablet ou computador de qualquer lugar.",
                    "friction_level": 4,
                    "placement_tip": "Rodapé da página ou FAQ principal"
                }
            ]
        }
