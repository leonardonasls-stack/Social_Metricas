<script setup lang="ts">
import { ref, computed } from 'vue'
import MarkdownIt from 'markdown-it'
import { Copy, Check, Download, FileText, Code2, Loader2 } from 'lucide-vue-next'
import { downloadDossierPdf } from '@/services/api'

const props = defineProps<{
  markdown: string
  keyword: string
  analysisId?: string
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

// Exportação Direta via WeasyPrint no Backend (Sem corte de texto nem páginas em branco)
const exportDirectPdf = async () => {
  if (exporting.value) return
  exporting.value = true

  try {
    if (!props.analysisId) {
      throw new Error('ID da análise não fornecido.')
    }
    await downloadDossierPdf(props.analysisId, props.keyword)
  } catch (err: any) {
    console.error('Erro ao baixar PDF via backend:', err)
    alert(`Erro ao gerar PDF: ${err.message || 'Falha no servidor'}`)
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <div class="dossier-card-container bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
    <!-- Header com Ações (Completamente ocultado na impressão via no-print) -->
    <div class="no-print flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
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
        id="dossier-rendered-view"
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

/* =======================================================
   ESTILOS ATIVADOS APENAS NO INSTANTE DA CAPTURA DO PDF
   (Garante que o html2canvas capture tudo legível com fundo branco)
   ======================================================= */
.pdf-render-mode {
  background-color: #ffffff !important;
  color: #0f172a !important;
  padding: 0 !important;
}

.pdf-render-mode > h1:first-child {
  margin-top: 0 !important;
  padding-top: 0 !important;
}

.pdf-render-mode h1 {
  color: #0f172a !important;
  border-bottom: 2px solid #e2e8f0 !important;
  font-size: 20pt !important;
  margin-top: 0 !important;
  margin-bottom: 12px !important;
}

.pdf-render-mode h2 {
  color: #1e293b !important;
  border-bottom: 1px solid #f1f5f9 !important;
  font-size: 14pt !important;
  margin-top: 20px !important;
  margin-bottom: 8px !important;
  page-break-after: avoid;
}

.pdf-render-mode h3 {
  color: #334155 !important;
  font-size: 11pt !important;
  margin-top: 14px !important;
  margin-bottom: 6px !important;
  page-break-after: avoid;
}

.pdf-render-mode p, 
.pdf-render-mode li {
  color: #334155 !important;
  font-size: 10pt !important;
  line-height: 1.5 !important;
}

.pdf-render-mode strong {
  color: #0f172a !important;
}

.pdf-render-mode table {
  width: 100% !important;
  border-collapse: collapse !important;
  font-size: 9pt !important;
  margin: 12px 0 !important;
  page-break-inside: avoid;
}

.pdf-render-mode th {
  background-color: #f8fafc !important;
  color: #0f172a !important;
  border: 1px solid #cbd5e1 !important;
  padding: 6px 8px !important;
}

.pdf-render-mode td {
  border: 1px solid #e2e8f0 !important;
  color: #1e293b !important;
  padding: 6px 8px !important;
}

.pdf-render-mode blockquote {
  border-left: 4px solid #4f46e5 !important;
  background-color: #f8fafc !important;
  color: #475569 !important;
  padding: 8px 12px !important;
  margin: 8px 0 !important;
  font-style: italic !important;
  page-break-inside: avoid;
}

.pdf-render-mode code {
  background-color: #f1f5f9 !important;
  color: #334155 !important;
  border: 1px solid #e2e8f0 !important;
  padding: 1px 4px !important;
  border-radius: 4px !important;
  font-size: 8.5pt !important;
}
</style>
