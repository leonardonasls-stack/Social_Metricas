<script setup lang="ts">
import { ref, computed } from 'vue'
import MarkdownIt from 'markdown-it'
import { Copy, Check, Printer, FileText, Code2 } from 'lucide-vue-next'

const props = defineProps<{
  markdown: string
  keyword: string
}>()

const activeTab = ref<'preview' | 'raw'>('preview')
const copied = ref(false)

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

const printDossier = () => {
  window.print()
}
</script>

<template>
  <div class="dossier-card-container bg-slate-800/80 border border-slate-700/80 rounded-2xl p-6 backdrop-blur-sm shadow-xl">
    <!-- Header com Ações (Ocultado na impressão via no-print) -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-700/80 no-print">
      <div>
        <h2 class="text-xl font-bold text-white flex items-center gap-2">
          <FileText class="w-5 h-5 text-indigo-400" />
          Dossiê Técnico & Diagnóstico de Mercado
        </h2>
        <p class="text-sm text-slate-400 mt-0.5">
          Relatório executivo estruturado para vendas de alto valor e arquitetura de produto.
        </p>
      </div>

      <div class="flex items-center gap-2 self-stretch sm:self-auto">
        <!-- Alternador Rendered vs Raw -->
        <div class="bg-slate-900/80 p-1 rounded-lg border border-slate-700/80 flex items-center">
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
          class="px-3 py-2 bg-slate-700/70 hover:bg-slate-600/80 text-slate-200 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 border border-slate-600/60"
        >
          <Check v-if="copied" class="w-4 h-4 text-emerald-400" />
          <Copy v-else class="w-4 h-4 text-slate-300" />
          <span>{{ copied ? 'Copiado!' : 'Copiar' }}</span>
        </button>

        <!-- Botão Imprimir A4 -->
        <button
          @click="printDossier"
          class="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 shadow-sm shadow-emerald-900/20"
        >
          <Printer class="w-4 h-4" />
          <span>Imprimir / PDF A4</span>
        </button>
      </div>
    </div>

    <!-- Conteúdo Renderizado (Preview Executivo & Impressão A4) -->
    <div v-if="activeTab === 'preview'" class="mt-6 print:mt-0">
      <div
        class="prose prose-invert prose-indigo max-w-none text-slate-200 leading-relaxed space-y-4 print:prose-neutral print:text-slate-900 print:max-w-none print:w-full"
        v-html="renderedHtml"
      ></div>
    </div>

    <!-- Conteúdo Raw (Editor Monoespaçado) -->
    <div v-else class="mt-6 no-print">
      <textarea
        readonly
        :value="markdown"
        class="w-full h-[600px] p-4 bg-slate-900/90 text-indigo-200/90 font-mono text-xs rounded-xl border border-slate-700/80 focus:outline-none resize-y selection:bg-indigo-500 selection:text-white"
      ></textarea>
    </div>
  </div>
</template>

<style>
/* Estilos para a tela normal (Dark Mode) */
.prose h1 {
  @apply text-2xl font-extrabold text-white pb-3 border-b border-slate-700/80 mb-4 tracking-tight;
}
.prose h2 {
  @apply text-lg font-bold text-indigo-300 mt-6 mb-3 tracking-tight flex items-center gap-2;
}
.prose h3 {
  @apply text-base font-semibold text-slate-200 mt-4 mb-2;
}
.prose p {
  @apply text-sm text-slate-300 mb-3 leading-relaxed;
}
.prose table {
  @apply w-full text-left border-collapse text-xs my-4 rounded-xl overflow-hidden border border-slate-700/80;
}
.prose th {
  @apply bg-slate-900/90 text-slate-300 font-semibold p-3 border-b border-slate-700/80;
}
.prose td {
  @apply p-3 border-b border-slate-800/80 text-slate-300;
}
.prose code {
  @apply font-mono text-xs bg-slate-900/80 text-indigo-300 px-1.5 py-0.5 rounded border border-slate-700/60;
}
.prose blockquote {
  @apply border-l-4 border-indigo-500 bg-indigo-950/20 px-4 py-2 rounded-r-lg my-4 text-xs text-indigo-200/90 italic;
}

/* Overrides Específicos para a Impressão A4 Limpa */
@media print {
  .prose h1 {
    font-size: 18pt !important;
    color: #0f172a !important;
    border-bottom: 2px solid #e2e8f0 !important;
    padding-bottom: 8px !important;
    margin-bottom: 12px !important;
  }
  .prose h2 {
    font-size: 14pt !important;
    color: #1e293b !important;
    margin-top: 18px !important;
    margin-bottom: 8px !important;
  }
  .prose h3 {
    font-size: 11pt !important;
    color: #334155 !important;
    margin-top: 12px !important;
    margin-bottom: 6px !important;
  }
  .prose p {
    font-size: 10pt !important;
    color: #334155 !important;
    line-height: 1.5 !important;
    margin-bottom: 8px !important;
  }
}
</style>
