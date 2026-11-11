import tempfile
import os
import typst
from typing import Dict, Any, List
from datetime import datetime


class TypstPdfService:
    """
    Geração Nativa e Ultrarrápida de PDF no Backend usando Typst.
    - Zero dependência de Chromium/navegador ou libs pesadas de SO.
    - Compilação nativa em Rust em menos de 20 milissegundos.
    - Controle perfeito de margens A4, paginação e blocos inquebráveis (#block(breakable: false)).
    """

    @classmethod
    def generate_pdf(
        cls,
        niche_name: str,
        keyword: str,
        sample_size: int,
        pain_points: List[Any],
        features: List[Any],
        hooks: List[Any],
        faqs: List[Any]
    ) -> bytes:
        date_str = datetime.utcnow().strftime("%d/%m/%Y às %H:%M")
        typ_code = cls._render_typst_template(
            niche_name=niche_name,
            keyword=keyword,
            sample_size=sample_size,
            date_str=date_str,
            pain_points=pain_points,
            features=features,
            hooks=hooks,
            faqs=faqs
        )
        
        # Cria arquivo temporário seguro para compilação garantida em qualquer versão do binding typst
        with tempfile.NamedTemporaryFile(suffix=".typ", mode="w", encoding="utf-8", delete=False) as tmp_in:
            tmp_in.write(typ_code)
            tmp_in_path = tmp_in.name

        try:
            pdf_bytes = typst.compile(tmp_in_path)
            return pdf_bytes
        finally:
            if os.path.exists(tmp_in_path):
                os.remove(tmp_in_path)

    @classmethod
    def _escape(cls, text: str) -> str:
        """Escapa caracteres reservados do Typst."""
        if not text:
            return ""
        return (
            str(text)
            .replace("\\", "\\\\")
            .replace("[", "\\[")
            .replace("]", "\\]")
            .replace("#", "\\#")
            .replace("$", "\\$")
            .replace("@", "\\@")
            .replace("*", "\\*")
            .replace("_", "\\_")
            .replace('"', '\\"')
        )

    @classmethod
    def _render_typst_template(
        cls,
        niche_name: str,
        keyword: str,
        sample_size: int,
        date_str: str,
        pain_points: List[Any],
        features: List[Any],
        hooks: List[Any],
        faqs: List[Any]
    ) -> str:
        kw_title = cls._escape(keyword.title())
        niche_esc = cls._escape(niche_name)

        doc = []
        doc.append(f"""
#set page(
  paper: "a4",
  margin: (top: 20mm, bottom: 20mm, left: 15mm, right: 15mm),
  footer: [
    #grid(
      columns: (1fr, 1fr),
      align(left, text(fill: rgb("#94a3b8"), size: 8pt)[
        Métrica Social-Media — Documento Técnico Confidencial
      ]),
      align(right, text(fill: rgb("#64748b"), size: 8pt)[
        #counter(page).display()
      ])
    )
  ]
)

#set text(
  font: ("Liberation Sans", "Roboto", "Helvetica Neue", "Arial"),
  size: 10pt,
  fill: rgb("#0f172a"),
  lang: "pt"
)

#set par(
  justify: true,
  leading: 0.65em,
  first-line-indent: 0pt
)

// Título Principal
#v(-5mm)
#text(size: 20pt, weight: "bold", fill: rgb("#0f172a"))[Dossiê Executivo de Inteligência de Mercado]
#v(1mm)
#text(size: 15pt, weight: "bold", fill: rgb("#4338ca"))[{kw_title}]

#v(2mm)
#line(length: 100%, stroke: 1.5pt + rgb("#e2e8f0"))
#v(1mm)

#text(size: 8.5pt, fill: rgb("#475569"))[
  *Nicho:* {niche_esc} | *Data de Emissão:* {date_str} | *Amostra Minerada:* {sample_size} interações públicas
]

#v(4mm)

// 1. Diagnóstico Executivo
== 1. Diagnóstico Executivo & Análise de Demanda

Este dossiê técnico sintetiza a extração de inteligência pública (comentários, discussões, queixas de clientes e análise de concorrentes) para o segmento de *{kw_title}*. O objetivo é embasar o desenvolvimento da aplicação e a redação da landing page sobre dados empíricos de mercado, eliminando suposições e blindando a operação contra falhas recorrentes de concorrentes.

#v(3mm)

// 2. Raio-X das Dores Recorrentes
== 2. Raio-X das Dores Recorrentes & A Voz do Cliente
Diagnóstico aprofundado das principais fricções que geram perda de faturamento e desistência de contratação:
""")

        # Itera sobre Dores com Blocos Inquebráveis
        for idx, p in enumerate(pain_points, 1):
            title = cls._escape(getattr(p, "title", str(p.get("title", ""))))
            category = cls._escape(getattr(p, "category", str(p.get("category", "Geral"))))
            desc = cls._escape(getattr(p, "description", str(p.get("description", ""))))
            severity = str(getattr(p, "severity", p.get("severity", "medium"))).upper()
            freq = getattr(p, "frequency_percentage", p.get("frequency_percentage", 0))
            fin_impact = cls._escape(str(getattr(p, "financial_impact", p.get("financial_impact", ""))))

            doc.append(f"""
#block(breakable: false)[
  #v(2mm)
  === 2.{idx} [{category}] {title}
  #v(1mm)
  - *Incidência Estimada:* `{freq}% das menções` | *Severidade:* `{severity}`
  - *Diagnóstico Operacional:* {desc}
""")
            if fin_impact and fin_impact != "None":
                doc.append(f"  - *⚠️ Impacto Financeiro na Operação:* _{fin_impact}_\n")

            comments = getattr(p, "sample_comments", p.get("sample_comments", [])) or []
            if comments:
                doc.append("  #v(1mm)\n  *Depoimentos Reais Minerados (A Voz do Cliente):*\n")
                for c in comments:
                    c_esc = cls._escape(c)
                    doc.append(f"""
  #rect(fill: rgb("#f8fafc"), stroke: (left: 3pt + rgb("#4f46e5")), inset: 8pt, radius: (right: 4pt))[
    #text(style: "italic", fill: rgb("#334155"), size: 9pt)[{c_esc}]
  ]
""")
            doc.append("]\n")

        # 3. Matriz RICE
        doc.append(f"""
#v(3mm)
== 3. Matriz de Features com RICE Score (Priorização de Backlog)

#table(
  columns: (28pt, 1fr, 1.3fr, 22pt, 22pt, 22pt, 22pt, 40pt),
  stroke: 0.5pt + rgb("#cbd5e1"),
  fill: (col, row) => if row == 0 {{ rgb("#f1f5f9") }} else {{ none }},
  align: (col, row) => if col in (0, 3, 4, 5, 6, 7) {{ center }} else {{ left }},
  [#text(weight: "bold")[Rank]],
  [#text(weight: "bold")[Feature Proposta]],
  [#text(weight: "bold")[Justificativa]],
  [#text(weight: "bold")[R]],
  [#text(weight: "bold")[I]],
  [#text(weight: "bold")[C]],
  [#text(weight: "bold")[E]],
  [#text(weight: "bold", fill: rgb("#059669"))[RICE]],
""")
        for idx, f in enumerate(features, 1):
            f_title = cls._escape(getattr(f, "title", str(f.get("title", ""))))
            f_rat = cls._escape(getattr(f, "rationale", str(f.get("rationale", ""))))
            r = getattr(f, "reach", f.get("reach", 5))
            i = getattr(f, "impact", f.get("impact", 5))
            c = getattr(f, "confidence", f.get("confidence", 5))
            e = getattr(f, "effort", f.get("effort", 5))
            score = getattr(f, "rice_score", f.get("rice_score", 0))
            doc.append(f"  [#{idx}], [{f_title}], [{f_rat}], [{r}], [{i}], [{c}], [{e}], [*#{score}*],\n")
        doc.append(")\n\n#v(1mm)\n_Fórmula RICE:_ $(R times I times C) / E$\n")

        # 3.1 Especificação de Engenharia das Features
        doc.append("""
#v(3mm)
== 3.1 Especificação de Engenharia das Features
""")
        for idx, f in enumerate(features, 1):
            f_title = cls._escape(getattr(f, "title", str(f.get("title", ""))))
            u_story = cls._escape(str(getattr(f, "user_story", f.get("user_story", ""))))
            e_break = cls._escape(str(getattr(f, "effort_breakdown", f.get("effort_breakdown", ""))))
            t_notes = cls._escape(str(getattr(f, "technical_notes", f.get("technical_notes", ""))))
            crits = getattr(f, "acceptance_criteria", f.get("acceptance_criteria", [])) or []

            doc.append(f"""
#block(breakable: false)[
  === Feature #{idx}: {f_title}
""")
            if u_story and u_story != "None":
                doc.append(f"  *História de Usuário (User Story):*\n  _{u_story}_\n\n")

            if crits:
                doc.append("  *Critérios de Aceite (Definition of Done):*\n")
                for cr in crits:
                    cr_esc = cls._escape(cr)
                    doc.append(f"  - [x] {cr_esc}\n")

            if (e_break and e_break != "None") or (t_notes and t_notes != "None"):
                doc.append(f"  #v(1mm)\n  *Arquitetura & Estimativa de Esforço:*\n")
                if e_break and e_break != "None":
                    doc.append(f"  - *Justificativa:* {e_break}\n")
                if t_notes and t_notes != "None":
                    doc.append(f"  - *Diretriz Técnica:* `{t_notes}`\n")
            doc.append("]\n")

        # 4. Ganchos de Copywriting
        doc.append("""
#v(3mm)
== 4. Ganchos de Copywriting & Estrutura de Conversão
Sugestões de redação testadas contra as maiores objeções do público-alvo:
""")
        for h in hooks:
            place = cls._escape(str(getattr(h, "placement", h.get("placement", ""))))
            intent = cls._escape(str(getattr(h, "intent", h.get("intent", ""))))
            text_h = cls._escape(str(getattr(h, "hook_text", h.get("hook_text", ""))))
            doc.append(f"""
#block(breakable: false)[
  - *Posicionamento (`{place}` | Intenção: `{intent}`):*
    \"{text_h}\"
]
""")

        # 5. FAQ Anti-Fricção
        doc.append("""
#v(3mm)
== 5. FAQ Anti-Fricção (Eliminação de Dúvidas Críticas)
""")
        for idx, faq in enumerate(faqs, 1):
            q = cls._escape(str(getattr(faq, "question", faq.get("question", ""))))
            a = cls._escape(str(getattr(faq, "answer_suggestion", faq.get("answer_suggestion", ""))))
            fric = getattr(faq, "friction_level", faq.get("friction_level", 3))
            doc.append(f"""
#block(breakable: false)[
  *P{idx}: {q}* (Fricção: `{fric}/5`)\n
  *Resposta:* {a}\n
]
""")

        doc.append("""
#v(5mm)
#line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
#align(center, text(size: 8pt, fill: rgb("#64748b"))[
  Relatório compilado nativamente via Typst Engine. Métrica Social-Media.
])
""")
        return "".join(doc)
