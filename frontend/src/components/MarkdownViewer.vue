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

// Exportação Direta para Arquivo PDF Limpo (Sem janela de impressão do navegador)
const exportDirectPdf = async () => {
  if (exporting.value) return
  exporting.value = true

  try {
    const element = document.getElementById('dossier-print-content')
    if (!element) {
      throw new Error('Elemento de conteúdo não encontrado.')
    }

    // Configuração do html2pdf para gerar um A4 editorial impecável
    const opt = {
      margin: [15, 15, 15, 15], // mm: topo, esquerda, baixo, direita
      filename: `Dossie_${props.keyword.toLowerCase().replace(/[^a-z0-9]/g, '_')}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: {
        scale: 2,
        useCORS: true,
        letterRendering: true,
        backgroundColor: '#ffffff'
      },
      jsPDF: {
        unit: 'mm',
        format: 'a4',
        orientation: 'portrait'
      },
      pagebreak: {
        mode: ['avoid-all', 'css', 'legacy']
      }
    }

    // @ts-ignore (html2pdf carregado via CDN bundle)
    if (window.html2pdf) {
      // @ts-ignore
      await window.html2pdf().set(opt).from(element).save()
    } else {
      console.warn('html2pdf não encontrado, utilizando fallback de impressão limpo.')
      window.print()
    }
  } catch (err) {
    console.error('Erro ao gerar PDF:', err)
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <div class="dossier-card-container bg-slate-800/80 border border-slate-700/80 rounded-2xl p-6 backdrop-blur-sm shadow-xl">
    <!-- Header com Ações (Nunca sai no PDF) -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-700/80 no-print">
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

        <!-- NOVO BOTÃO: EXPORTAR PDF DIRETO (1-Click Download) -->
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

    <!-- Conteúdo do Documento (Elemento capturado para o PDF) -->
    <div v-show="activeTab === 'preview'" class="mt-6 print:mt-0">
      <div
        id="dossier-print-content"
        class="prose prose-invert prose-indigo max-w-none text-slate-200 leading-relaxed space-y-4 print:prose-neutral print:text-slate-900 print:max-w-none print:w-full bg-transparent"
        v-html="renderedHtml"
      ></div>
    </div>

    <!-- Conteúdo Raw (Editor Monoespaçado) -->
    <div v-if="activeTab === 'raw'" class="mt-6 no-print">
      <textarea
        readonly
        :value="markdown"
        class="w-full h-[600px] p-4 bg-slate-900/90 text-indigo-200/90 font-mono text-xs rounded-xl border border-slate-700/80 focus:outline-none resize-y selection:bg-indigo-500 selection:text-white"
      ></textarea>
    </div>
  </div>
</template>

<style>
/* Estilos Dark Mode para visualização Web */
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

/* =======================================================
   ESTILOS ESPECÍFICOS PARA A CAPTURA E GERAÇÃO DO PDF
   (Cores corporativas, fundo branco e sem quebra de tabelas)
   ======================================================= */
#dossier-print-content {
  /* Quando capturado pelo html2canvas */
  background-color: #ffffff;
  color: #0f172a;
}

#dossier-print-content h1 {
  color: #0f172a !important;
  border-bottom: 2px solid #e2e8f0 !important;
  font-size: 20pt !important;
  padding-bottom: 6px !important;
  margin-bottom: 12px !important;
}

#dossier-print-content h2 {
  color: #1e293b !important;
  font-size: 14pt !important;
  margin-top: 20px !important;
  margin-bottom: 10px !important;
  page-break-after: avoid;
  break-after: avoid;
}

#dossier-print-content h3 {
  color: #334155 !important;
  font-size: 11pt !important;
  margin-top: 14px !important;
  margin-bottom: 6px !important;
  page-break-after: avoid;
  break-after: avoid;
}

#dossier-print-content p, 
#dossier-print-content li {
  color: #334155 !important;
  font-size: 10pt !important;
  line-height: 1.5 !important;
}

#dossier-print-content table {
  width: 100% !important;
  border-collapse: collapse !important;
  font-size: 9pt !important;
  margin: 12px 0 !important;
  page-break-inside: avoid;
  break-inside: avoid;
}

#dossier-print-content th {
  background-color: #f8fafc !important;
  color: #0f172a !important;
  border: 1px solid #cbd5e1 !important;
  padding: 6px 8px !important;
}

#dossier-print-content td {
  border: 1px solid #e2e8f0 !important;
  color: #1e293b !important;
  padding: 6px 8px !important;
}

#dossier-print-content blockquote {
  border-left: 4px solid #6366f1 !important;
  background-color: #f8fafc !important;
  color: #475569 !important;
  padding: 8px 12px !important;
  margin: 8px 0 !important;
  font-style: italic !important;
  page-break-inside: avoid;
  break-inside: avoid;
}

#dossier-print-content code {
  background-color: #f1f5f9 !important;
  color: #334155 !important;
  border: 1px solid #e2e8f0 !important;
  padding: 1px 4px !important;
  border-radius: 4px !important;
  font-size: 8.5pt !important;
}
</style>
