import markdown
from weasyprint import HTML, CSS
from io import BytesIO

# Template CSS estritamente alinhado às regras de impressão profissional (W3C Paged Media)
WEASYPRINT_CSS = """
@page {
    size: A4 portrait;
    margin: 20mm 15mm;
    @bottom-right {
        content: "Página " counter(page) " de " counter(pages);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 8pt;
        color: #64748b;
    }
    @bottom-left {
        content: "Métrica Social-Media — Documento Confidencial de Produto";
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 8pt;
        color: #94a3b8;
    }
}

body {
    font-family: "Liberation Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    color: #0f172a;
    font-size: 10pt;
    line-height: 1.6;
    margin: 0;
    padding: 0;
}

/* Regra de Ouro: Controle de Órfãs e Viúvas */
p, li {
    orphans: 3;
    widows: 3;
    margin-bottom: 8px;
    color: #334155;
}

/* Títulos: Proteção contra quebra no final da página */
h1 {
    font-size: 20pt;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 2.5px solid #e2e8f0;
    padding-bottom: 8px;
    margin-top: 0;
    margin-bottom: 14px;
    line-height: 1.25;
    break-after: avoid;
    page-break-after: avoid;
}

h2 {
    font-size: 14pt;
    font-weight: 700;
    color: #1e293b;
    border-bottom: 1.5px solid #f1f5f9;
    padding-bottom: 4px;
    margin-top: 24px;
    margin-bottom: 10px;
    break-after: avoid;
    page-break-after: avoid;
}

h3 {
    font-size: 11.5pt;
    font-weight: 700;
    color: #334155;
    margin-top: 16px;
    margin-bottom: 6px;
    break-after: avoid;
    page-break-after: avoid;
}

h4 {
    font-size: 10.5pt;
    font-weight: 600;
    color: #4338ca;
    margin-top: 12px;
    margin-bottom: 4px;
    break-after: avoid;
    page-break-after: avoid;
}

/* Proteção de Blocos e Tabelas */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 9pt;
    break-inside: avoid;
    page-break-inside: avoid;
}

tr, td, th {
    break-inside: avoid;
    page-break-inside: avoid;
}

th {
    background-color: #f8fafc;
    color: #0f172a;
    font-weight: 700;
    border: 1px solid #cbd5e1;
    padding: 7px 9px;
    text-align: left;
}

td {
    border: 1px solid #e2e8f0;
    color: #1e293b;
    padding: 7px 9px;
    vertical-align: top;
}

/* Blocos Importantes e Citações (A Voz do Cliente) */
blockquote, .bloco-importante {
    break-inside: avoid;
    page-break-inside: avoid;
    border-left: 3.5px solid #4f46e5;
    background-color: #f8fafc;
    color: #334155;
    padding: 8px 14px;
    margin: 10px 0;
    font-style: italic;
    border-radius: 0 4px 4px 0;
}

code {
    background-color: #f1f5f9;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    padding: 1.5px 4.5px;
    border-radius: 4px;
    font-size: 8.5pt;
    font-family: monospace;
}

hr {
    border: 0;
    border-top: 1px solid #e2e8f0;
    margin: 18px 0;
}
"""

class PdfService:
    @classmethod
    def generate_pdf_from_markdown(cls, markdown_text: str) -> bytes:
        """
        Converte o Markdown do dossiê em PDF A4 de altíssima fidelidade editorial
        usando WeasyPrint e regras de W3C Paged Media.
        """
        # Converte Markdown para HTML com suporte a tabelas e atributos
        html_body = markdown.markdown(
            markdown_text,
            extensions=["tables", "fenced_code", "nl2br", "sane_lists"]
        )

        full_html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="utf-8">
            <title>Dossiê Executivo de Inteligência de Mercado</title>
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """

        pdf_io = BytesIO()
        HTML(string=full_html).write_pdf(
            pdf_io,
            stylesheets=[CSS(string=WEASYPRINT_CSS)]
        )
        return pdf_io.getvalue()
