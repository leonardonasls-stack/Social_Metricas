import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é um especialista em Product Management, Engenharia de Software e Copywriting de Alta Conversão.
Sua missão é analisar um nicho/termo pesquisado por um desenvolvedor e entregar um diagnóstico de produto CIRÚRGICO, baseado em dores reais de mercado (como se tivesse minerado centenas de discussões no Reddit, TikTok, Instagram e YouTube).

IMPORTANTE:
- NUNCA dê respostas genéricas com repetição de palavras.
- Analise a dor REAL operacional do segmento (ex: se for Ordem de Serviço, fale de aprovação de orçamento pelo WhatsApp, perda de peças no estoque, garantia contestada por cliente, técnicos em campo sem internet).
- Gere notas RICE realistas (1 a 10) e calcule: rice_score = (reach * impact * confidence) / effort.
- Retorne EXCLUSIVAMENTE um objeto JSON válido (sem tags markdown de código como ```json, apenas o JSON puro).

Formato do JSON exigido:
{
  "sample_size": 180,
  "pain_points": [
    {
      "category": "Operacional | Financeiro | Atendimento | Segurança",
      "title": "Título conciso da dor",
      "description": "Explicação detalhada da queixa comum",
      "frequency_percentage": 38.5,
      "severity": "critical | high | medium | low"
    }
  ],
  "recommended_features": [
    {
      "title": "Nome da funcionalidade técnica",
      "rationale": "Por que essa feature resolve a dor acima",
      "reach": 9,
      "impact": 8,
      "confidence": 9,
      "effort": 3,
      "rice_score": 216.0
    }
  ],
  "hook_copies": [
    {
      "placement": "hero_headline | subheadline | cta_button",
      "hook_text": "Frase de alto impacto emocional e conversão",
      "intent": "relief | urgency | social_proof"
    }
  ],
  "faq_items": [
    {
      "question": "Dúvida real mais frequente que trava a compra",
      "answer_suggestion": "Resposta ideal e convincente para a landing page",
      "friction_level": 5
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
    async def synthesize(cls, keyword: str, niche_name: str) -> Dict[str, Any]:
        user_message = f"Analise o termo: '{keyword}' no nicho: '{niche_name}'. Identifique as 4 maiores dores reais, 4 features com RICE Score, 3 hooks de copy e 4 FAQs anti-objeção."

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
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
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
                return json.loads(text)
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
                # Limpa markdown caso venha com ```json
                text_clean = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                return json.loads(text_clean)
            resp.raise_for_status()
        return None

    @classmethod
    def _local_contextual_fallback(cls, keyword: str, niche_name: str) -> Dict[str, Any]:
        """
        Gera análise contextual rica sem IA caso todas as chaves estejam esgotadas.
        Detecta segmentos por palavras-chave técnicas.
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
                        "severity": "critical"
                    },
                    {
                        "category": "Atendimento & Suporte",
                        "title": "WhatsApp sobrecarregado com clientes perguntando status do aparelho",
                        "description": "Falta de acompanhamento automático faz os clientes ligarem o dia todo perguntando se o equipamento ficou pronto.",
                        "frequency_percentage": 33.0,
                        "severity": "high"
                    },
                    {
                        "category": "Estoque & Peças",
                        "title": "Furo no inventário por peças retiradas sem vínculo com a OS",
                        "description": "Peças caras somem da bancada porque o técnico usou no conserto sem dar baixa automática no sistema.",
                        "frequency_percentage": 27.5,
                        "severity": "high"
                    },
                    {
                        "category": "Operacional em Campo",
                        "title": "Dificuldade de preencher laudos e coletar fotos pelo celular",
                        "description": "Softwares concorrentes têm interfaces pesadas que travam em celulares mais simples de técnicos de rua.",
                        "frequency_percentage": 21.0,
                        "severity": "medium"
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
                        "rice_score": 243.0
                    },
                    {
                        "title": "Página Pública de Rastreio da OS em Tempo Real (Estilo iFood)",
                        "rationale": "Cliente acompanha em tempo real: 'Em Análise' -> 'Aguardando Peça' -> 'Pronto para Retirada', eliminando 70% das mensagens no WhatsApp.",
                        "reach": 9,
                        "impact": 8,
                        "confidence": 9,
                        "effort": 2,
                        "rice_score": 324.0
                    },
                    {
                        "title": "Baixa Automática de Peças ao Vincular na OS",
                        "rationale": "Ao adicionar um item no laudo, o saldo é abatido do estoque na hora e o custo é embutido no lucro da OS.",
                        "reach": 8,
                        "impact": 7,
                        "confidence": 8,
                        "effort": 2,
                        "rice_score": 224.0
                    },
                    {
                        "title": "Check-in Rápido com Fotos do Aparelho Entrada/Saída",
                        "rationale": "Técnico bate fotos de arranhões ou avarias na entrada para evitar que o cliente acuse a loja de ter danificado o aparelho.",
                        "reach": 8,
                        "impact": 8,
                        "confidence": 8,
                        "effort": 3,
                        "rice_score": 170.7
                    }
                ],
                "hook_copies": [
                    {
                        "placement": "hero_headline",
                        "hook_text": "Elimine a Papelada e Nunca Mais Leve Calote com Aprovação Digital de OS em 1 Clique.",
                        "intent": "relief"
                    },
                    {
                        "placement": "subheadline",
                        "hook_text": "O sistema completo de Ordem de Serviço que avisa seu cliente no WhatsApp e dá baixa no estoque sem dor de cabeça.",
                        "intent": "social_proof"
                    },
                    {
                        "placement": "cta_button",
                        "hook_text": "Testar Grátis e Agilizar Minha Oficina",
                        "intent": "urgency"
                    }
                ],
                "faq_items": [
                    {
                        "question": "O cliente pode aprovar o orçamento direto pelo celular?",
                        "answer_suggestion": "Sim! Ele recebe um link exclusivo no WhatsApp, vê as peças descritas e assina com o dedo na tela, gerando comprovante na hora.",
                        "friction_level": 5
                    },
                    {
                        "question": "Funciona para técnicos que atendem na rua sem internet?",
                        "answer_suggestion": "Sim, o app mobile salva os laudos e fotos em modo offline e sincroniza tudo automaticamente assim que detectar sinal.",
                        "friction_level": 4
                    },
                    {
                        "question": "Como evito perder peças do meu estoque?",
                        "answer_suggestion": "O sistema só libera o fechamento da OS se cada peça utilizada for bipada ou selecionada, abatendo o estoque na hora.",
                        "friction_level": 4
                    },
                    {
                        "question": "Posso emitir nota fiscal e recibo em impressora térmica?",
                        "answer_suggestion": "Sim, compatível com qualquer impressora térmica Bluetooth de 58mm ou 80mm e emissão de NFS-e em poucos cliques.",
                        "friction_level": 3
                    }
                ]
            }

        # Segmento 2: Turismo & Lazer (Quadriciclo, Lanchas, etc)
        elif any(term in kw for term in ["quadriciclo", "passeio", "trilha", "turismo", "aventura", "buggy"]):
            from app.services.scrapecreators.mock_miner import MockMiner
            return MockMiner.generate_mock_analysis(keyword, ["reddit", "tiktok", "instagram"])

        # Padrão Contextual Geral de Negócios / SaaS
        return {
            "sample_size": 150,
            "pain_points": [
                {
                    "category": "Usabilidade & Operação",
                    "title": f"Interfaces lentas e sistemas complexos para {keyword.title()}",
                    "description": "Usuários reclamam que concorrentes exigem muitos cliques para ações simples do cotidiano.",
                    "frequency_percentage": 37.0,
                    "severity": "high"
                },
                {
                    "category": "Preço & Burocracia",
                    "title": "Fidelidade obrigatória e cobrança abusiva por usuário adicional",
                    "description": "Pequenas empresas desistem de contratar ferramentas que cobram caro por cada funcionário cadastrado.",
                    "frequency_percentage": 31.5,
                    "severity": "critical"
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
                    "rice_score": 256.0
                }
            ],
            "hook_copies": [
                {
                    "placement": "hero_headline",
                    "hook_text": f"A Forma Mais Rápida e Lucrativa de Gerenciar {keyword.title()}.",
                    "intent": "relief"
                }
            ],
            "faq_items": [
                {
                    "question": f"Preciso instalar algo no computador para usar com {keyword}?",
                    "answer_suggestion": "Não! 100% em nuvem, acessível do celular, tablet ou computador de qualquer lugar.",
                    "friction_level": 4
                }
            ]
        }
