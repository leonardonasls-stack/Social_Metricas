<script setup lang="ts">
import { ref, computed } from 'vue'
import MarkdownIt from 'markdown-it'
import { Copy, Check, Download, FileText, Code2, Loader2 } from 'lucide-vue-next'

const props = defineProps<{
  markdown: string
  keyword: string
}>()

const activeTab = ref<'preview' | 'raw'>('preview')
const copied = ref(false)
const exporting = ref(false)

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

const renderedHtml = computed(() => {
  return md.render(props.markdown)
})

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(props.markdown)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Falha ao copiar:', err)
  }
}

// Exportação Direta de PDF via html2pdf com folha de estilos editorial injetada
const exportDirectPdf = async () => {
  if (exporting.value) return
  exporting.value = true

  try {
    // 1. Cria um container temporário anexado ao body (invisível na tela)
    const printContainer = document.createElement('div')
    printContainer.id = 'temp-pdf-export-container'
    printContainer.style.position = 'fixed'
    printContainer.style.left = '-9999px'
    printContainer.style.top = '0'
    printContainer.style.width = '794px' // Largura exata A4 (96 DPI)
    printContainer.style.backgroundColor = '#ffffff'
    printContainer.style.color = '#0f172a'
    printContainer.style.fontFamily = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    printContainer.style.padding = '0'
    printContainer.style.margin = '0'

    // 2. Estilos específicos do documento impresso (tabelas com borda, títulos destacados, citações)
    const editorialCss = `
      <style>
        #temp-pdf-export-container h1 {
          font-size: 22px !important;
          font-weight: 800 !important;
          color: #0f172a !important;
          border-bottom: 2px solid #e2e8f0 !important;
          padding-bottom: 8px !important;
          margin-top: 0 !important;
          margin-bottom: 12px !important;
          line-height: 1.3 !important;
        }
        #temp-pdf-export-container h2 {
          font-size: 16px !important;
          font-weight: 700 !important;
          color: #1e293b !important;
          border-bottom: 1px solid #f1f5f9 !important;
          padding-bottom: 4px !important;
          margin-top: 22px !important;
          margin-bottom: 10px !important;
          page-break-after: avoid;
        }
        #temp-pdf-export-container h3 {
          font-size: 13px !important;
          font-weight: 600 !important;
          color: #334155 !important;
          margin-top: 14px !important;
          margin-bottom: 6px !important;
          page-break-after: avoid;
        }
        #temp-pdf-export-container h4 {
          font-size: 12px !important;
          font-weight: 600 !important;
          color: #475569 !important;
          margin-top: 10px !important;
          margin-bottom: 4px !important;
        }
        #temp-pdf-export-container p, 
        #temp-pdf-export-container li {
          font-size: 11px !important;
          color: #334155 !important;
          line-height: 1.6 !important;
          margin-bottom: 8px !important;
        }
        #temp-pdf-export-container table {
          width: 100% !important;
          border-collapse: collapse !important;
          font-size: 10px !important;
          margin: 14px 0 !important;
          page-break-inside: avoid;
        }
        #temp-pdf-export-container th {
          background-color: #f8fafc !important;
          color: #0f172a !important;
          font-weight: 700 !important;
          border: 1px solid #cbd5e1 !important;
          padding: 6px 8px !important;
          text-align: left !important;
        }
        #temp-pdf-export-container td {
          border: 1px solid #e2e8f0 !important;
          color: #1e293b !important;
          padding: 6px 8px !important;
        }
        #temp-pdf-export-container blockquote {
          border-left: 4px solid #4f46e5 !important;
          background-color: #f8fafc !important;
          color: #334155 !important;
          padding: 8px 12px !important;
          margin: 10px 0 !important;
          font-style: italic !important;
          page-break-inside: avoid;
        }
        #temp-pdf-export-container code {
          background-color: #f1f5f9 !important;
          color: #1e293b !important;
          border: 1px solid #e2e8f0 !important;
          padding: 1px 4px !important;
          border-radius: 4px !important;
          font-size: 9.5px !important;
          font-family: monospace !important;
        }
        #temp-pdf-export-container hr {
          border: 0 !important;
          border-top: 1px solid #e2e8f0 !important;
          margin: 16px 0 !important;
        }
      </style>
    `

    printContainer.innerHTML = editorialCss + renderedHtml.value
    document.body.appendChild(printContainer)

    const opt = {
      margin: [10, 12, 10, 12], // mm: topo, esquerda, baixo, direita
      filename: `Dossie_${props.keyword.toLowerCase().replace(/[^a-z0-9]/g, '_')}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: {
        scale: 2,
        useCORS: true,
        scrollY: 0,
        scrollX: 0,
        backgroundColor: '#ffffff'
      },
      jsPDF: {
        unit: 'mm',
        format: 'a4',
        orientation: 'portrait'
      },
      pagebreak: {
        mode: ['css', 'legacy']
      }
    }

    // @ts-ignore
    if (window.html2pdf) {
      // @ts-ignore
      await window.html2pdf().set(opt).from(printContainer).save()
    }

    // Remove elemento temporário do DOM
    document.body.removeChild(printContainer)
  } catch (err) {
    console.error('Erro ao gerar PDF:', err)
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <div class="dossier-card-container bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
    <!-- Header com Ações -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
      <div>
        <h2 class="text-xl font-bold text-white flex items-center gap-2">
          <FileText class="w-5 h-5 text-indigo-400" />
          Dossiê Técnico & Diagnóstico de Mercado
        </h2>
        <p class="text-sm text-slate-400 mt-0.5">
          Documento executivo estruturado para reuniões comerciais e arquitetura de produto.
        </p>
      </div>

      <div class="flex items-center gap-2.5 self-stretch sm:self-auto">
        <!-- Alternador Visualizar vs Raw -->
        <div class="bg-slate-950 p-1 rounded-lg border border-slate-800 flex items-center">
          <button
            @click="activeTab = 'preview'"
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5',
              activeTab === 'preview'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            ]"
          >
            <FileText class="w-3.5 h-3.5" />
            Visualizar
          </button>
          <button
            @click="activeTab = 'raw'"
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5',
              activeTab === 'raw'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            ]"
          >
            <Code2 class="w-3.5 h-3.5" />
            Markdown Raw
          </button>
        </div>

        <!-- Botão Copiar -->
        <button
          @click="copyToClipboard"
          class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 border border-slate-700"
        >
          <Check v-if="copied" class="w-4 h-4 text-emerald-400" />
          <Copy v-else class="w-4 h-4 text-slate-300" />
          <span>{{ copied ? 'Copiado!' : 'Copiar' }}</span>
        </button>

        <!-- Botão Exportar PDF -->
        <button
          @click="exportDirectPdf"
          :disabled="exporting"
          class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold rounded-lg transition-all flex items-center gap-2 shadow-md shadow-emerald-900/30"
        >
          <Loader2 v-if="exporting" class="w-4 h-4 animate-spin" />
          <Download v-else class="w-4 h-4" />
          <span>{{ exporting ? 'Gerando Arquivo PDF...' : 'Exportar PDF' }}</span>
        </button>
      </div>
    </div>

    <!-- Conteúdo do Documento no Frontend (Preview Dark Mode) -->
    <div v-show="activeTab === 'preview'" class="mt-6">
      <div
        class="prose prose-invert prose-indigo max-w-none text-slate-100 leading-relaxed space-y-4"
        v-html="renderedHtml"
      ></div>
    </div>

    <!-- Conteúdo Raw (Editor Monoespaçado) -->
    <div v-if="activeTab === 'raw'" class="mt-6">
      <textarea
        readonly
        :value="markdown"
        class="w-full h-[600px] p-4 bg-slate-950 text-indigo-300 font-mono text-xs rounded-xl border border-slate-800 focus:outline-none resize-y selection:bg-indigo-500 selection:text-white"
      ></textarea>
    </div>
  </div>
</template>

<style>
/* =======================================================
   ESTILOS DARK MODE PARA A TELA WEB (ALTO CONTRASTE E LEGIBILIDADE)
   ======================================================= */
.prose h1 {
  @apply text-2xl font-extrabold text-white pb-3 border-b border-slate-800 mb-4 tracking-tight;
}
.prose h2 {
  @apply text-lg font-bold text-indigo-400 mt-6 mb-3 tracking-tight border-b border-slate-800/60 pb-1.5 flex items-center gap-2;
}
.prose h3 {
  @apply text-base font-semibold text-slate-100 mt-4 mb-2;
}
.prose h4 {
  @apply text-sm font-semibold text-indigo-300 mt-3 mb-1;
}
.prose p, .prose li {
  @apply text-sm text-slate-200 mb-3 leading-relaxed;
}
.prose strong {
  @apply text-white font-semibold;
}
.prose table {
  @apply w-full text-left border-collapse text-xs my-4 rounded-xl overflow-hidden border border-slate-800;
}
.prose th {
  @apply bg-slate-950 text-slate-200 font-bold p-3 border-b border-slate-800;
}
.prose td {
  @apply p-3 border-b border-slate-800/80 text-slate-200;
}
.prose code {
  @apply font-mono text-xs bg-slate-950 text-indigo-300 px-2 py-0.5 rounded border border-slate-800;
}
.prose blockquote {
  @apply border-l-4 border-indigo-500 bg-slate-950/80 px-4 py-3 rounded-r-lg my-4 text-xs text-indigo-200 italic shadow-inner;
}
.prose hr {
  @apply border-slate-800 my-6;
}
</style>
