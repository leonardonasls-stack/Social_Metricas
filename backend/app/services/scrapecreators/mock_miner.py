from typing import Dict, Any, List


class MockMiner:
    """
    Simulador realista de inteligência social para desenvolvimento, testes e sandbox.
    Gera dados analíticos pré-calculados específicos com base na palavra-chave.
    """

    @classmethod
    def generate_mock_analysis(cls, keyword: str, sources: List[str]) -> Dict[str, Any]:
        kw_lower = keyword.lower()
        
        # Exemplo focado no nicho de Turismo de Aventura / Quadriciclo
        if any(term in kw_lower for term in ["quadriciclo", "passeio", "trilha", "turismo", "aventura", "buggy"]):
            sample_size = 184
            pain_points = [
                {
                    "category": "Segurança & Medo",
                    "title": "Insegurança na pilotagem e medo de tombamento",
                    "description": "Usuários relatam receio de perder o controle em terrenos acidentados ou falta de capacetes de tamanho adequado.",
                    "frequency_percentage": 42.5,
                    "severity": "critical"
                },
                {
                    "category": "Clima & Cancelamento",
                    "title": "Incerteza sobre passeio em dias de chuva",
                    "description": "Comentários frequentes perguntando se o passeio é cancelado ou se o dinheiro é devolvido em caso de chuva súbita.",
                    "frequency_percentage": 28.0,
                    "severity": "high"
                },
                {
                    "category": "Regulação & CNH",
                    "title": "Dúvida persistente sobre exigência de CNH",
                    "description": "Clientes deixam de reservar por não saberem se passageiro sem CNH pode pilotar ou se adolescentes podem ir na garupa.",
                    "frequency_percentage": 22.5,
                    "severity": "medium"
                },
                {
                    "category": "Preço & Taxas Ocultas",
                    "title": "Cobrança surpresa de fotos e combustível",
                    "description": "Reclamações sobre fotógrafos que cobram valores abusivos após a trilha sem aviso prévio na reserva.",
                    "frequency_percentage": 18.2,
                    "severity": "medium"
                }
            ]
            
            features = [
                {
                    "title": "Briefing de Segurança Interativo no Checkout",
                    "rationale": "Demonstra em 3 passos simples como o quadriciclo é estável e guiado por instrutores credenciados, eliminando 42% do medo inicial.",
                    "reach": 9,
                    "impact": 9,
                    "confidence": 9,
                    "effort": 3,
                    "rice_score": round((9 * 9 * 9) / 3, 1) # 243.0
                },
                {
                    "title": "Política 'Chuva com Sol' (Reagendamento em 1 Clique)",
                    "rationale": "Garante reagendamento gratuito ou reembolso integral caso chova, quebrando a objeção climática antes do pagamento.",
                    "reach": 7,
                    "impact": 8,
                    "confidence": 8,
                    "effort": 2,
                    "rice_score": round((7 * 8 * 8) / 2, 1) # 224.0
                },
                {
                    "title": "Simulador de Idade e Garupa (Sem Necessidade de CNH)",
                    "rationale": "Calculadora rápida no início da landing page que diz na hora quem pode pilotar e quem pode ir na garupa com base na idade.",
                    "reach": 8,
                    "impact": 7,
                    "confidence": 9,
                    "effort": 2,
                    "rice_score": round((8 * 7 * 9) / 2, 1) # 252.0
                },
                {
                    "title": "Pacote 'Tudo Incluso' com Álbum Digital",
                    "rationale": "Inclui fotos de alta definição feitas por drone e equipamento higienizado no preço final com transparência total.",
                    "reach": 6,
                    "impact": 6,
                    "confidence": 8,
                    "effort": 4,
                    "rice_score": round((6 * 6 * 8) / 4, 1) # 72.0
                }
            ]
            
            hooks = [
                {
                    "placement": "hero_headline",
                    "hook_text": "Sinta a Adrenalina da Trilha com 100% de Segurança e Guias Credenciados.",
                    "intent": "relief"
                },
                {
                    "placement": "subheadline",
                    "hook_text": "Mesmo que você nunca tenha pilotado: quadriciclos automáticos, briefing passo a passo e garantia contra imprevistos.",
                    "intent": "social_proof"
                },
                {
                    "placement": "cta_button",
                    "hook_text": "Garantir Vaga com Reagendamento Grátis",
                    "intent": "urgency"
                }
            ]
            
            faqs = [
                {
                    "question": "Preciso ter CNH para pilotar o quadriciclo?",
                    "answer_suggestion": "Não é exigida CNH para trilhas em áreas privadas e ecológicas guiadas. Nossos quadriciclos são 100% automáticos e acompanhados por guias credenciados após aula prática.",
                    "friction_level": 5
                },
                {
                    "question": "E se chover no dia do meu passeio?",
                    "answer_suggestion": "Você tem garantia total de reagendamento sem taxas ou devolução do valor. Passeios com chuva leve são até mais emocionantes pela lama, mas você sempre decide!",
                    "friction_level": 5
                },
                {
                    "question": "Crianças ou adolescentes podem ir na garupa?",
                    "answer_suggestion": "Sim! A partir de 7 anos podem acompanhar os pais na garupa de quadriciclos duplos com colete e capacete especial ajustado.",
                    "friction_level": 4
                },
                {
                    "question": "O que está incluso no valor da reserva?",
                    "answer_suggestion": "Quadriciclo individual ou duplo, capacetes higienizados, guia credenciado, seguro individual e parada exclusiva para banho/fotos.",
                    "friction_level": 3
                }
            ]
        else:
            # Padrão genérico de mercado para qualquer outra palavra-chave
            sample_size = 140
            pain_points = [
                {
                    "category": "Experiência de Uso",
                    "title": f"Dificuldade de suporte e onboarding em {keyword}",
                    "description": "Usuários reclamam de lentidão para tirar dúvidas e termos técnicos complexos.",
                    "frequency_percentage": 36.0,
                    "severity": "high"
                },
                {
                    "category": "Preço & Contratos",
                    "title": "Falta de transparência nos planos e taxas adicionais",
                    "description": "Comentários negativos sobre taxas surpresas cobradas no primeiro faturamento.",
                    "frequency_percentage": 29.5,
                    "severity": "critical"
                }
            ]
            features = [
                {
                    "title": "Onboarding Guiado em 3 Minutos",
                    "rationale": "Reduz atrito inicial e resolve a principal reclamação minerada de suporte lento.",
                    "reach": 8,
                    "impact": 8,
                    "confidence": 8,
                    "effort": 3,
                    "rice_score": round((8 * 8 * 8) / 3, 1)
                }
            ]
            hooks = [
                {
                    "placement": "hero_headline",
                    "hook_text": f"A Solução Definitiva para {keyword.title()} Sem Burocracia.",
                    "intent": "relief"
                }
            ]
            faqs = [
                {
                    "question": f"Como funciona o serviço de {keyword}?",
                    "answer_suggestion": "Simples, ágil e com suporte em tempo real direto via WhatsApp.",
                    "friction_level": 4
                }
            ]
            
        return {
            "sample_size": sample_size,
            "pain_points": pain_points,
            "recommended_features": sorted(features, key=lambda x: x["rice_score"], reverse=True),
            "hook_copies": hooks,
            "faq_items": faqs
        }
