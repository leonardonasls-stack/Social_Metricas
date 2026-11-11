from typing import Dict, Any
from datetime import datetime


class DossierCompiler:
    """
    Compila os dados de mineração e síntese analítica em um Dossiê Técnico em Markdown,
    otimizado com tabelas executivas, badges de severidade e pronto para impressão A4.
    """

    @classmethod
    def compile_markdown(cls, niche_name: str, keyword: str, data: Dict[str, Any]) -> str:
        date_str = datetime.utcnow().strftime("%d/%m/%Y às %H:%M")
        sample_size = data.get("sample_size", 0)
        
        md = []
        md.append(f"# Dossiê de Inteligência de Mercado — {keyword.title()}")
        md.append(f"**Nicho:** {niche_name}  |  **Data de Emissão:** {date_str}  |  **Amostra Minerada:** {sample_size} interações públicas\n")
        md.append("---\n")
        
        # 1. Resumo Executivo
        md.append("## 1. Diagnóstico Executivo de Demanda")
        md.append(f"Este dossiê sintetiza a extração de inteligência pública (comentários, dúvidas e vídeos virais) para o segmento de **{keyword}**. O objetivo é orientar o desenvolvimento do produto e a arquitetura da landing page com base em dados empíricos de mercado, eliminando o desenvolvimento baseado em suposições.\n")
        
        # 2. Dores e Objeções Recorrentes
        md.append("## 2. Dores e Objeções Recorrentes (Comment Mining)")
        md.append("| Categoria | Principal Queixa / Medo | Frequência (%) | Severidade |")
        md.append("| :--- | :--- | :---: | :---: |")
        for p in data.get("pain_points", []):
            freq = f"{p['frequency_percentage']}%"
            sev = p['severity'].upper()
            md.append(f"| **{p['category']}** | {p['title']} | {freq} | `{sev}` |")
        md.append("\n")
        
        # 3. Features Recomendadas com RICE Score
        md.append("## 3. Matriz de Features com RICE Score (Priorização de Backlog)")
        md.append("| Ranking | Funcionalidade Proposta | Justificativa de Engenharia | R | I | C | E | RICE Score |")
        md.append("| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |")
        for idx, f in enumerate(data.get("recommended_features", []), 1):
            md.append(f"| #{idx} | **{f['title']}** | {f['rationale']} | {f['reach']} | {f['impact']} | {f['confidence']} | {f['effort']} | **{f['rice_score']}** |")
        md.append("\n> **Fórmula RICE:** $\\text{Score} = (\\text{Reach} \\times \\text{Impact} \\times \\text{Confidence}) / \\text{Effort}$\n")
        
        # 4. Copywriting e Ganchos Emocionais
        md.append("## 4. Ganchos de Copywriting Validados (Hero & CTAs)")
        for h in data.get("hook_copies", []):
            md.append(f"- **Posicionamento (`{h['placement']}`):** *\"{h['hook_text']}\"* (Intenção: `{h['intent']}`)")
        md.append("\n")
        
        # 5. FAQ Anti-Fricção
        md.append("## 5. FAQ Anti-Fricção (Quebra de Objeções no Checkout)")
        for f in data.get("faq_items", []):
            md.append(f"### P: {f['question']}")
            md.append(f"**Resposta Recomendada:** {f['answer_suggestion']}\n")
            
        md.append("---\n*Relatório gerado automaticamente pela plataforma Métrica Social-Media. Documento confidencial para planejamento de produto e proposta comercial.*")
        
        return "\n".join(md)
