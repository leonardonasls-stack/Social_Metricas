from typing import Dict, Any
from datetime import datetime


class DossierCompiler:
    """
    Compila os dados de mineração, raio-x das dores, especificações técnicas
    e síntese analítica em um Dossiê Técnico Executivo em Markdown de Alto Valor,
    otimizado para apresentação a clientes, propostas comerciais e impressão A4.
    """

    @classmethod
    def compile_markdown(cls, niche_name: str, keyword: str, data: Dict[str, Any]) -> str:
        date_str = datetime.utcnow().strftime("%d/%m/%Y às %H:%M")
        sample_size = data.get("sample_size", 0)
        
        md = []
        md.append(f"# Dossiê Executivo de Inteligência de Mercado — {keyword.title()}")
        md.append(f"**Nicho:** {niche_name}  |  **Data de Emissão:** {date_str}  |  **Amostra Minerada:** {sample_size} interações públicas\n")
        md.append("---\n")
        
        # 1. Diagnóstico Executivo de Demanda
        md.append("## 1. Diagnóstico Executivo & Análise de Demanda")
        md.append(f"Este dossiê técnico sintetiza a extração de inteligência pública (comentários, discussões, queixas de clientes e análise de concorrentes) para o segmento de **{keyword.title()}**.")
        md.append("O objetivo deste documento é embasar o desenvolvimento da aplicação e a redação da landing page sobre dados empíricos de mercado, eliminando suposições e blindando a operação contra falhas já cometidas por concorrentes.\n")
        
        # 2. Raio-X Detalhado das Dores & Voz do Cliente
        md.append("## 2. Raio-X das Dores Recorrentes & A Voz do Cliente")
        md.append("Diagnóstico aprofundado das principais fricções que geram perda de faturamento e desistência de contratação:\n")
        
        for idx, p in enumerate(data.get("pain_points", []), 1):
            sev = p.get("severity", "medium").upper()
            freq = p.get("frequency_percentage", 0)
            md.append(f"### 2.{idx} [{p.get('category', 'Geral')}] {p.get('title', '')}")
            md.append(f"- **Incidência Mapeada:** `{freq}% das discussões qualificadas`  |  **Severidade:** `{sev}`")
            md.append(f"- **Diagnóstico Operacional:** {p.get('description', '')}")
            
            if p.get("financial_impact"):
                md.append(f"- **⚠️ Impacto Operacional & Negócio:** *{p.get('financial_impact')}*")
                
            if p.get("competitors_affected"):
                comps = ", ".join(p.get("competitors_affected", []))
                md.append(f"- **Ferramentas / Concorrentes Mais Criticados:** `{comps}`")
                
            if p.get("sample_comments") and len(p.get("sample_comments", [])) > 0:
                md.append("\n**Depoimentos Reais Minerados (A Voz do Cliente):**")
                for comment in p.get("sample_comments", []):
                    md.append(f"> {comment}")
            md.append("\n")
            
        # 3. Matriz de Features com RICE Score e Especificação Técnica
        md.append("## 3. Matriz de Features com RICE Score* (Priorização de Backlog)")
        md.append("| Ranking | Funcionalidade Proposta | Justificativa de Engenharia | R | I | C | E | RICE Score* |")
        md.append("| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |")
        for idx, f in enumerate(data.get("recommended_features", []), 1):
            md.append(f"| #{idx} | **{f.get('title', '')}** | {f.get('rationale', '')} | {f.get('reach', 5)} | {f.get('impact', 5)} | {f.get('confidence', 5)} | {f.get('effort', 5)} | **{f.get('rice_score', 0)}** |")
        md.append("\n<small>\\* **RICE Score:** Framework de priorização de produto criado pela Intercom. A pontuação é calculada pela fórmula $\\text{Score} = (R \\times I \\times C) / E$, onde **R** (Reach/Alcance: usuários impactados no período), **I** (Impact/Impacto na experiência: 1 a 10), **C** (Confidence/Confiança técnica: 1 a 10) e **E** (Effort/Esforço de desenvolvimento: 1 a 10). Quanto maior o score, maior o retorno sobre investimento (ROI).</small>\n")

        # 3.1 Especificação Detalhada das Features de Maior Impacto
        md.append("### 3.1 Especificação de Engenharia das Features (User Stories & Critérios de Aceite)\n")
        for idx, f in enumerate(data.get("recommended_features", []), 1):
            md.append(f"#### Feature #{idx}: {f.get('title', '')}")
            if f.get("user_story"):
                md.append(f"**História de Usuário (User Story):**\n> {f.get('user_story')}\n")
                
            if f.get("acceptance_criteria") and len(f.get("acceptance_criteria", [])) > 0:
                md.append("**Critérios de Aceite (Definition of Done):**")
                for crit in f.get("acceptance_criteria", []):
                    md.append(f"- [x] {crit}")
                md.append("")
                
            if f.get("effort_breakdown") or f.get("technical_notes"):
                md.append("**Arquitetura & Estimativa de Esforço:**")
                if f.get("effort_breakdown"):
                    md.append(f"- **Justificativa do Esforço:** {f.get('effort_breakdown')}")
                if f.get("technical_notes"):
                    md.append(f"- **Stack / Diretriz Técnica:** `{f.get('technical_notes')}`")
            md.append("\n")

        # 4. Copywriting e Ganchos Emocionais Validados
        md.append("## 4. Ganchos de Copywriting & Estrutura de Conversão (Hero & CTAs)")
        md.append("Sugestões de redação testadas contra as maiores objeções do público-alvo:\n")
        for h in data.get("hook_copies", []):
            md.append(f"### Posicionamento: `{h.get('placement', '')}` (Intenção: `{h.get('intent', '')}`)")
            md.append(f"- **Headline Principal:** *\"{h.get('hook_text', '')}\"*")
            if h.get("page_position"):
                md.append(f"- **Posicionamento na Tela:** {h.get('page_position')}")
            if h.get("variations") and len(h.get("variations", [])) > 0:
                md.append("- **Variações de Teste A/B:**")
                for var in h.get("variations", []):
                    md.append(f"  - *\"{var}\"*")
            md.append("")
        md.append("\n")

        # 5. FAQ Anti-Fricção (Quebra de Objeções no Checkout)
        md.append("## 5. FAQ Anti-Fricção (Eliminação de Dúvidas Críticas)")
        md.append("Perguntas reais identificadas nos comentários que impedem o fechamento do negócio:\n")
        for idx, faq in enumerate(data.get("faq_items", []), 1):
            fric = faq.get("friction_level", 3)
            md.append(f"### P{idx}: {faq.get('question', '')}")
            md.append(f"**Resposta Recomendada:** {faq.get('answer_suggestion', '')}")
            md.append(f"- *Nível de Fricção:* `{fric}/5`  |  *Recomendação:* {faq.get('placement_tip', 'Inserir no bloco de FAQ principal da Landing Page')}\n")
            
        md.append("---\n*Relatório gerado automaticamente pela plataforma Métrica Social-Media. Documento técnico executivo para planejamento de produto, propostas comerciais e arquitetura de software.*")
        
        return "\n".join(md)

    @classmethod
    def compile_from_models(
        cls,
        niche_name: str,
        keyword: str,
        sample_size: int,
        pain_points: list,
        features: list,
        hooks: list,
        faqs: list
    ) -> str:
        """Recompila o Markdown diretamente a partir dos modelos persistidos no PostgreSQL."""
        data = {
            "sample_size": sample_size,
            "pain_points": [
                {
                    "category": getattr(p, "category", "Geral"),
                    "title": getattr(p, "title", ""),
                    "description": getattr(p, "description", ""),
                    "frequency_percentage": getattr(p, "frequency_percentage", 0),
                    "severity": getattr(p, "severity", "medium"),
                    "financial_impact": getattr(p, "financial_impact", None),
                    "competitors_affected": getattr(p, "competitors_affected", None),
                    "sample_comments": getattr(p, "sample_comments", None)
                }
                for p in pain_points
            ],
            "recommended_features": [
                {
                    "title": getattr(f, "title", ""),
                    "rationale": getattr(f, "rationale", ""),
                    "reach": getattr(f, "reach", 5),
                    "impact": getattr(f, "impact", 5),
                    "confidence": getattr(f, "confidence", 5),
                    "effort": getattr(f, "effort", 5),
                    "rice_score": getattr(f, "rice_score", 0),
                    "user_story": getattr(f, "user_story", None),
                    "acceptance_criteria": getattr(f, "acceptance_criteria", None),
                    "effort_breakdown": getattr(f, "effort_breakdown", None),
                    "technical_notes": getattr(f, "technical_notes", None)
                }
                for f in features
            ],
            "hook_copies": [
                {
                    "placement": getattr(h, "placement", ""),
                    "hook_text": getattr(h, "hook_text", ""),
                    "intent": getattr(h, "intent", ""),
                    "variations": getattr(h, "variations", None),
                    "page_position": getattr(h, "page_position", None)
                }
                for h in hooks
            ],
            "faq_items": [
                {
                    "question": getattr(faq, "question", ""),
                    "answer_suggestion": getattr(faq, "answer_suggestion", ""),
                    "friction_level": getattr(faq, "friction_level", 3),
                    "placement_tip": getattr(faq, "placement_tip", None)
                }
                for faq in faqs
            ]
        }
        return cls.compile_markdown(niche_name, keyword, data)

