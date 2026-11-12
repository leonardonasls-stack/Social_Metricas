<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  Search,
  Sparkles,
  TrendingUp,
  Layers,
  AlertTriangle,
  HelpCircle,
  Copy,
  Check,
  PlusCircle,
  Database,
  ArrowRight,
  ExternalLink,
  ChevronRight
} from 'lucide-vue-next'
import { fetchNiches, createNiche, runAnalysis, fetchDossier } from '@/services/api'
import type { Niche, Analysis, Dossier, PainPoint, RecommendedFeature } from '@/types'
import MarkdownViewer from '@/components/MarkdownViewer.vue'
import DetailDrawer from '@/components/DetailDrawer.vue'

const niches = ref<Niche[]>([])
const selectedNicheId = ref<string>('')
const keyword = ref<string>('sistema de ordem de serviço')
const forceRefresh = ref<boolean>(false)
const mode = ref<string>('live')
const selectedSources = ref<string[]>(['reddit', 'tiktok', 'instagram', 'youtube'])

const loading = ref<boolean>(false)
const activeTab = ref<'insights' | 'dossier'>('insights')
const currentAnalysis = ref<Analysis | null>(null)
const currentDossier = ref<Dossier | null>(null)
const newNicheName = ref<string>('')
const showNewNicheModal = ref<boolean>(false)
const copiedHook = ref<string | null>(null)

// Estados do Slide-over Drawer
const isDrawerOpen = ref<boolean>(false)
const drawerType = ref<'pain' | 'feature' | null>(null)
const selectedPain = ref<PainPoint | null>(null)
const selectedFeature = ref<RecommendedFeature | null>(null)

// Carrega Nichos na Inicialização
onMounted(async () => {
  try {
    const list = await fetchNiches()
    niches.value = list
    if (list.length > 0) {
      selectedNicheId.value = list[0].id
    } else {
      // Cria nicho padrão inicial
      const defaultNiche = await createNiche(
        'Tecnologia SaaS & Software',
        'Softwares de gestão, ordem de serviço, ERPs e ferramentas produtivas'
      )
      niches.value = [defaultNiche]
      selectedNicheId.value = defaultNiche.id
    }
  } catch (err) {
    console.error('Erro ao carregar nichos:', err)
  }
})

const handleCreateNiche = async () => {
  if (!newNicheName.value.trim()) return
  try {
    const created = await createNiche(newNicheName.value.trim())
    niches.value.push(created)
    selectedNicheId.value = created.id
    newNicheName.value = ''
    showNewNicheModal.value = false
  } catch (err) {
    console.error('Falha ao criar nicho:', err)
  }
}

const handleSearch = async () => {
  if (!selectedNicheId.value || !keyword.value.trim()) return

  loading.value = true
  try {
    const result = await runAnalysis({
      niche_id: selectedNicheId.value,
      keyword: keyword.value.trim(),
      sources: selectedSources.value,
      force_refresh: forceRefresh.value,
      mode: mode.value
    })
    currentAnalysis.value = result

    // Carrega o Dossiê Markdown
    const dossierData = await fetchDossier(result.id)
    currentDossier.value = dossierData
  } catch (err) {
    console.error('Erro na análise:', err)
  } finally {
    loading.value = false
  }
}

const openPainDetail = (pain: PainPoint) => {
  selectedPain.value = pain
  drawerType.value = 'pain'
  isDrawerOpen.value = true
}

const openFeatureDetail = (feature: RecommendedFeature) => {
  selectedFeature.value = feature
  drawerType.value = 'feature'
  isDrawerOpen.value = true
}

const closeDrawer = () => {
  isDrawerOpen.value = false
}

const copyText = async (text: string) => {
  await navigator.clipboard.writeText(text)
  copiedHook.value = text
  setTimeout(() => {
    copiedHook.value = null
  }, 2000)
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
    <!-- Navbar Superior -->
    <header class="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-40 no-print">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Sparkles class="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 class="text-base font-bold text-white tracking-tight flex items-center gap-2">
              Métrica Social-Media
              <span class="text-[10px] font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full">
                v1.1 Multi-LLM
              </span>
            </h1>
            <p class="text-xs text-slate-400">Social Intelligence for App & Landing Page Builders</p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-3 py-1.5 rounded-lg">
            <Database class="w-3.5 h-3.5" />
            <span>PostgreSQL Cache Ativo</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <!-- Painel de Busca e Controles -->
      <section class="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm space-y-5 no-print">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Seletor de Nicho -->
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Layers class="w-3.5 h-3.5 text-indigo-400" />
                Nicho de Mercado
              </label>
              <button
                @click="showNewNicheModal = true"
                class="text-[11px] text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
              >
                <PlusCircle class="w-3 h-3" />
                Novo Nicho
              </button>
            </div>
            <select
              v-model="selectedNicheId"
              class="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option v-for="n in niches" :key="n.id" :value="n.id">
                {{ n.name }} ({{ n.total_analyses }} análises)
              </option>
            </select>
          </div>

          <!-- Input de Termo / Palavra-Chave -->
          <div class="md:col-span-2">
            <label class="block text-xs font-semibold text-slate-300 mb-1.5">
              Palavra-Chave, Concorrente ou Intenção de Compra
            </label>
            <div class="relative">
              <input
                v-model="keyword"
                @keyup.enter="handleSearch"
                placeholder="Ex: sistema de ordem de serviço, passeio de quadriciclo, clínica de estética"
                class="w-full bg-slate-800 border border-slate-700 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 placeholder-slate-500"
              />
              <Search class="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            </div>
          </div>
        </div>

        <!-- Opções Avançadas e Botão de Ação -->
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pt-3 border-t border-slate-800/80">
          <div class="flex flex-wrap items-center gap-4">
            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-400">Modo de Mineração:</span>
              <button
                type="button"
                @click="mode = mode === 'live' ? 'mock' : 'live'"
                class="px-2.5 py-1 rounded-lg text-xs font-medium border transition-colors flex items-center gap-1.5"
                :class="mode === 'live' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-slate-800 text-slate-300 border-slate-700'"
              >
                <span class="w-2 h-2 rounded-full" :class="mode === 'live' ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'"></span>
                {{ mode === 'live' ? '🔥 Pesquisa Real (ScrapeCreators Ao Vivo)' : '🧪 Sandbox (Mock)' }}
              </button>
            </div>

            <label class="flex items-center gap-1.5 text-xs text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                v-model="forceRefresh"
                class="rounded border-slate-700 text-indigo-600 focus:ring-indigo-500 bg-slate-800"
              />
              Forçar Nova Busca (Ignorar Cache)
            </label>
          </div>

          <button
            @click="handleSearch"
            :disabled="loading || !keyword.trim()"
            class="w-full sm:w-auto px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-sm rounded-xl transition-all shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2"
          >
            <Sparkles v-if="!loading" class="w-4 h-4" />
            <div v-else class="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
            <span>{{ loading ? 'Sintetizando Mercado...' : 'Analisar Mercado' }}</span>
          </button>
        </div>
      </section>

      <!-- Feedback de Cache e Amostra -->
      <div v-if="currentAnalysis" class="flex items-center justify-between text-xs text-slate-400 no-print px-1">
        <div class="flex items-center gap-2">
          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold"
            :class="currentAnalysis.is_cached ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'"
          >
            {{ currentAnalysis.is_cached ? '⚡ Recuperado do Cache (< 100ms)' : '✨ Mineração Nova Concluída' }}
          </span>
          <span>Amostra: <strong>{{ currentAnalysis.sample_size }}</strong> interações analisadas</span>
        </div>

        <!-- Abas: Dashboard vs Dossiê -->
        <div class="flex items-center gap-1 bg-slate-900 border border-slate-800 p-1 rounded-xl">
          <button
            @click="activeTab = 'insights'"
            :class="['px-3 py-1.5 rounded-lg text-xs font-semibold transition-all', activeTab === 'insights' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white']"
          >
            Dashboard de Métricas
          </button>
          <button
            @click="activeTab = 'dossier'"
            :class="['px-3 py-1.5 rounded-lg text-xs font-semibold transition-all', activeTab === 'dossier' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white']"
          >
            Dossiê em Markdown & Impressão
          </button>
        </div>
      </div>

      <!-- VISÃO 1: DASHBOARD DE INSIGHTS COM ELEMENTOS CLICÁVEIS -->
      <div v-if="currentAnalysis && activeTab === 'insights'" class="space-y-8 no-print">
        <!-- 1. Dores e Objeções Mineradas (Clicáveis) -->
        <div>
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-lg font-bold text-white flex items-center gap-2">
                <AlertTriangle class="w-5 h-5 text-amber-400" />
                Dores e Objeções Recorrentes (Comment Mining)
              </h2>
              <p class="text-xs text-slate-400 mt-0.5">Clique em qualquer card para ver comentários reais minerados e impacto financeiro.</p>
            </div>
            <span class="text-xs text-slate-400 hidden sm:inline">Classificado por frequência de queixas</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="(pain, idx) in currentAnalysis.pain_points"
              :key="idx"
              @click="openPainDetail(pain)"
              class="group bg-slate-900/90 border border-slate-800 hover:border-indigo-500/80 hover:bg-slate-800/50 rounded-2xl p-5 transition-all shadow-md cursor-pointer relative"
            >
              <div class="flex items-center justify-between gap-2 mb-2">
                <span class="text-xs font-semibold text-indigo-400 bg-indigo-950/60 border border-indigo-800/40 px-2 py-0.5 rounded-md">
                  {{ pain.category }}
                </span>
                <span
                  class="text-xs font-bold px-2 py-0.5 rounded-md uppercase tracking-wider text-[10px]"
                  :class="{
                    'bg-red-500/10 text-red-400 border border-red-500/20': pain.severity === 'critical',
                    'bg-amber-500/10 text-amber-400 border border-amber-500/20': pain.severity === 'high',
                    'bg-blue-500/10 text-blue-400 border border-blue-500/20': pain.severity === 'medium'
                  }"
                >
                  {{ pain.severity }} ({{ pain.frequency_percentage }}%)
                </span>
              </div>
              <h3 class="text-sm font-semibold text-white mb-1.5 group-hover:text-indigo-300 transition-colors flex items-center justify-between">
                <span>{{ pain.title }}</span>
                <ChevronRight class="w-4 h-4 text-slate-500 group-hover:text-indigo-400 transition-transform group-hover:translate-x-1 shrink-0" />
              </h3>
              <p class="text-xs text-slate-400 leading-relaxed line-clamp-2">{{ pain.description }}</p>
              
              <div class="mt-3 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-500 group-hover:text-slate-400">
                <span>🔍 Ver comentários de clientes e impacto</span>
                <span class="text-indigo-400 font-medium">Abrir Raio-X &rarr;</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. Matriz de Features com RICE Score (Linhas Clicáveis) -->
        <div>
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-lg font-bold text-white flex items-center gap-2">
                <TrendingUp class="w-5 h-5 text-emerald-400" />
                Matriz de Features com RICE Score (Priorização de Backlog)
              </h2>
              <p class="text-xs text-slate-400 mt-0.5">Clique em uma linha para ver a User Story, Critérios de Aceite e notas técnicas.</p>
            </div>
          </div>

          <div class="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-lg">
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-950/80 text-slate-400 border-b border-slate-800 uppercase font-semibold">
                  <tr>
                    <th class="p-3.5 text-center">Rank</th>
                    <th class="p-3.5">Feature Proposta</th>
                    <th class="p-3.5">Justificativa de Produto</th>
                    <th class="p-3.5 text-center">R</th>
                    <th class="p-3.5 text-center">I</th>
                    <th class="p-3.5 text-center">C</th>
                    <th class="p-3.5 text-center">E</th>
                    <th class="p-3.5 text-center text-emerald-400">RICE Score</th>
                    <th class="p-3.5 text-center">Ação</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-800/80 text-slate-300">
                  <tr
                    v-for="(feat, idx) in currentAnalysis.recommended_features"
                    :key="idx"
                    @click="openFeatureDetail(feat)"
                    class="hover:bg-slate-800/70 cursor-pointer transition-colors group"
                  >
                    <td class="p-3.5 text-center font-bold text-slate-400">#{{ idx + 1 }}</td>
                    <td class="p-3.5 font-semibold text-white whitespace-nowrap group-hover:text-emerald-300 transition-colors">
                      {{ feat.title }}
                    </td>
                    <td class="p-3.5 text-slate-400 max-w-md">{{ feat.rationale }}</td>
                    <td class="p-3.5 text-center font-mono">{{ feat.reach }}</td>
                    <td class="p-3.5 text-center font-mono">{{ feat.impact }}</td>
                    <td class="p-3.5 text-center font-mono">{{ feat.confidence }}</td>
                    <td class="p-3.5 text-center font-mono">{{ feat.effort }}</td>
                    <td class="p-3.5 text-center font-extrabold text-sm text-emerald-400">{{ feat.rice_score }}</td>
                    <td class="p-3.5 text-center">
                      <span class="text-[11px] text-indigo-400 bg-indigo-950/40 border border-indigo-800/40 px-2 py-1 rounded-md group-hover:bg-indigo-600 group-hover:text-white transition-all">
                        Especificar &rarr;
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 3. Copywriting & FAQ em 2 Colunas -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Ganchos de Copywriting -->
          <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-lg space-y-4">
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles class="w-4 h-4 text-indigo-400" />
              Ganchos e Headlines (Hero & CTAs)
            </h3>
            <div class="space-y-3">
              <div
                v-for="(hook, idx) in currentAnalysis.hook_copies"
                :key="idx"
                class="p-3.5 bg-slate-800/70 border border-slate-700/60 rounded-xl relative group hover:border-slate-600 transition-all"
              >
                <div class="flex items-center justify-between text-[10px] font-semibold text-slate-400 uppercase mb-1">
                  <span>{{ hook.placement }}</span>
                  <span class="text-indigo-400">{{ hook.intent }}</span>
                </div>
                <p class="text-xs font-medium text-slate-200 pr-8 italic">"{{ hook.hook_text }}"</p>
                <button
                  @click="copyText(hook.hook_text)"
                  class="absolute right-3 top-3.5 p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-700 transition-all"
                  title="Copiar texto"
                >
                  <Check v-if="copiedHook === hook.hook_text" class="w-3.5 h-3.5 text-emerald-400" />
                  <Copy v-else class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          <!-- FAQ Anti-Fricção -->
          <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-lg space-y-4">
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <HelpCircle class="w-4 h-4 text-emerald-400" />
              FAQ Anti-Fricção para Landing Page
            </h3>
            <div class="space-y-3">
              <div
                v-for="(faq, idx) in currentAnalysis.faq_items"
                :key="idx"
                class="p-3.5 bg-slate-800/70 border border-slate-700/60 rounded-xl space-y-1.5"
              >
                <h4 class="text-xs font-semibold text-white flex items-center justify-between">
                  <span>{{ faq.question }}</span>
                  <span class="text-[10px] font-normal text-amber-400 bg-amber-950/40 px-1.5 py-0.5 rounded border border-amber-800/40">
                    Fricção: {{ faq.friction_level }}/5
                  </span>
                </h4>
                <p class="text-xs text-slate-400 leading-relaxed">{{ faq.answer_suggestion }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- VISÃO 2: DOSSIÊ MARKDOWN & IMPRESSÃO -->
      <div v-if="currentDossier && activeTab === 'dossier'">
        <MarkdownViewer
          :markdown="currentDossier.markdown_content"
          :keyword="currentDossier.keyword"
          :analysis-id="currentDossier.analysis_id"
        />
      </div>

      <!-- Estado Inicial / Vazio -->
      <div
        v-if="!currentAnalysis && !loading"
        class="bg-slate-900/40 border border-dashed border-slate-800 rounded-3xl p-12 text-center max-w-xl mx-auto space-y-4"
      >
        <div class="w-12 h-12 rounded-2xl bg-indigo-950/60 border border-indigo-800/50 flex items-center justify-center mx-auto text-indigo-400">
          <Search class="w-6 h-6" />
        </div>
        <h3 class="text-base font-bold text-white">Nenhuma análise carregada</h3>
        <p class="text-xs text-slate-400 leading-relaxed">
          Selecione um nicho temático, digite a palavra-chave (ex: <em>"sistema de ordem de serviço"</em>) e clique em <strong>Analisar Mercado</strong>.
        </p>
      </div>
    </main>

    <!-- Slide-Over Drawer para Detalhamento Clicável -->
    <DetailDrawer
      :is-open="isDrawerOpen"
      :type="drawerType"
      :pain-data="selectedPain"
      :feature-data="selectedFeature"
      @close="closeDrawer"
    />

    <!-- Modal Novo Nicho -->
    <div
      v-if="showNewNicheModal"
      class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
    >
      <div class="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
        <h3 class="text-base font-bold text-white">Criar Novo Nicho Temático</h3>
        <p class="text-xs text-slate-400">
          Nichos agrupam pesquisas para economizar requisições e manter inteligência de mercado acumulada.
        </p>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Nome do Nicho</label>
          <input
            v-model="newNicheName"
            @keyup.enter="handleCreateNiche"
            placeholder="Ex: Clínicas de Estética, Turismo Ecológico"
            class="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div class="flex items-center justify-end gap-2 pt-2">
          <button
            @click="showNewNicheModal = false"
            class="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white rounded-lg transition-all"
          >
            Cancelar
          </button>
          <button
            @click="handleCreateNiche"
            :disabled="!newNicheName.trim()"
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg transition-all shadow-md"
          >
            Criar Nicho
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
