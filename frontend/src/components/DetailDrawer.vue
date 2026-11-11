<script setup lang="ts">
import {
  X,
  AlertTriangle,
  TrendingUp,
  MessageSquareQuote,
  DollarSign,
  Users,
  CheckCircle2,
  Code,
  Sparkles,
  Layers
} from 'lucide-vue-next'
import type { PainPoint, RecommendedFeature } from '@/types'

const props = defineProps<{
  isOpen: boolean
  type: 'pain' | 'feature' | null
  painData?: PainPoint | null
  featureData?: RecommendedFeature | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()
</script>

<template>
  <!-- Backdrop -->
  <div
    v-if="isOpen"
    @click="emit('close')"
    class="fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-50 transition-opacity"
  ></div>

  <!-- Slide-over Drawer -->
  <div
    class="fixed inset-y-0 right-0 max-w-xl w-full bg-slate-900 border-l border-slate-800 z-50 shadow-2xl flex flex-col transform transition-transform duration-300 ease-in-out"
    :class="isOpen ? 'translate-x-0' : 'translate-x-full'"
  >
    <!-- Header do Painel -->
    <div class="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/80 backdrop-blur-md">
      <div class="flex items-center gap-2.5">
        <div
          v-if="type === 'pain'"
          class="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400"
        >
          <AlertTriangle class="w-4 h-4" />
        </div>
        <div
          v-else
          class="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400"
        >
          <TrendingUp class="w-4 h-4" />
        </div>
        <div>
          <h2 class="text-sm font-bold text-white tracking-tight">
            {{ type === 'pain' ? 'Raio-X da Dor Minerada' : 'Especificação de Engenharia da Feature' }}
          </h2>
          <p class="text-xs text-slate-400">
            {{ type === 'pain' ? 'Evidências reais e impacto no negócio' : 'Critérios de aceite e arquitetura' }}
          </p>
        </div>
      </div>

      <button
        @click="emit('close')"
        class="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-all"
      >
        <X class="w-5 h-5" />
      </button>
    </div>

    <!-- Conteúdo Scrollável -->
    <div class="flex-1 overflow-y-auto p-6 space-y-6">
      <!-- CONTEÚDO: DETALHE DA DOR (PAIN POINT) -->
      <div v-if="type === 'pain' && painData" class="space-y-6">
        <!-- Título e Badges -->
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <span class="text-xs font-semibold text-indigo-400 bg-indigo-950/60 border border-indigo-800/40 px-2.5 py-0.5 rounded-md">
              {{ painData.category }}
            </span>
            <span
              class="text-xs font-bold px-2 py-0.5 rounded-md uppercase tracking-wider text-[10px]"
              :class="{
                'bg-red-500/10 text-red-400 border border-red-500/20': painData.severity === 'critical',
                'bg-amber-500/10 text-amber-400 border border-amber-500/20': painData.severity === 'high',
                'bg-blue-500/10 text-blue-400 border border-blue-500/20': painData.severity === 'medium'
              }"
            >
              Severidade: {{ painData.severity }} ({{ painData.frequency_percentage }}% das menções)
            </span>
          </div>
          <h3 class="text-base font-bold text-white">{{ painData.title }}</h3>
          <p class="text-xs text-slate-300 leading-relaxed">{{ painData.description }}</p>
        </div>

        <!-- Impacto Financeiro no Cliente -->
        <div class="p-4 bg-amber-950/20 border border-amber-800/30 rounded-xl space-y-1.5">
          <h4 class="text-xs font-bold text-amber-300 flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
            <DollarSign class="w-4 h-4 text-amber-400" />
            Impacto Financeiro na Operação
          </h4>
          <p class="text-xs text-slate-300 leading-relaxed">
            {{ painData.financial_impact || 'Gera atrito operacional contínuo e perda de margem de lucro nas transações.' }}
          </p>
        </div>

        <!-- A Voz do Cliente: Comentários Literais Minerados -->
        <div class="space-y-3">
          <h4 class="text-xs font-bold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
            <MessageSquareQuote class="w-4 h-4 text-indigo-400" />
            A Voz do Cliente (Comentários Reais Minerados)
          </h4>

          <div
            v-if="painData.sample_comments && painData.sample_comments.length > 0"
            class="space-y-2.5"
          >
            <div
              v-for="(c, idx) in painData.sample_comments"
              :key="idx"
              class="p-3 bg-slate-800/80 border border-slate-700/60 rounded-xl text-xs text-slate-300 italic border-l-4 border-l-indigo-500 leading-relaxed"
            >
              {{ c }}
            </div>
          </div>
          <div v-else class="text-xs text-slate-400 italic">
            Nenhum comentário específico extraído nesta amostra resumida.
          </div>
        </div>

        <!-- Concorrentes Afetados -->
        <div v-if="painData.competitors_affected && painData.competitors_affected.length > 0" class="space-y-2">
          <h4 class="text-xs font-bold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
            <Users class="w-4 h-4 text-emerald-400" />
            Concorrentes e Ferramentas Mais Criticadas
          </h4>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="(comp, idx) in painData.competitors_affected"
              :key="idx"
              class="px-2.5 py-1 bg-slate-800 text-slate-300 text-xs font-medium rounded-lg border border-slate-700"
            >
              {{ comp }}
            </span>
          </div>
        </div>
      </div>

      <!-- CONTEÚDO: DETALHE DA FEATURE (RECOMMENDED FEATURE) -->
      <div v-if="type === 'feature' && featureData" class="space-y-6">
        <!-- Título e Métricas RICE -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-3 py-1 rounded-lg flex items-center gap-1.5">
              <Sparkles class="w-3.5 h-3.5" />
              RICE Score: {{ featureData.rice_score }}
            </span>
          </div>
          <h3 class="text-base font-bold text-white">{{ featureData.title }}</h3>
          <p class="text-xs text-slate-300 leading-relaxed">{{ featureData.rationale }}</p>
        </div>

        <!-- Grade de Fatores RICE -->
        <div class="grid grid-cols-4 gap-2 p-3 bg-slate-800/60 border border-slate-700/60 rounded-xl text-center">
          <div>
            <div class="text-[10px] text-slate-400 uppercase font-semibold">Reach (R)</div>
            <div class="text-sm font-extrabold text-white mt-0.5">{{ featureData.reach }}/10</div>
          </div>
          <div>
            <div class="text-[10px] text-slate-400 uppercase font-semibold">Impact (I)</div>
            <div class="text-sm font-extrabold text-white mt-0.5">{{ featureData.impact }}/10</div>
          </div>
          <div>
            <div class="text-[10px] text-slate-400 uppercase font-semibold">Confidence (C)</div>
            <div class="text-sm font-extrabold text-white mt-0.5">{{ featureData.confidence }}/10</div>
          </div>
          <div>
            <div class="text-[10px] text-slate-400 uppercase font-semibold">Effort (E)</div>
            <div class="text-sm font-extrabold text-white mt-0.5">{{ featureData.effort }}/10</div>
          </div>
        </div>

        <!-- User Story (História de Usuário) -->
        <div class="space-y-2">
          <h4 class="text-xs font-bold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
            <Layers class="w-4 h-4 text-indigo-400" />
            User Story (Padrão Ágil)
          </h4>
          <div class="p-3.5 bg-slate-800/80 border border-slate-700/60 rounded-xl text-xs text-indigo-200 leading-relaxed font-medium">
            {{ featureData.user_story || 'Como usuário do sistema, quero ter essa funcionalidade integrada para resolver o gargalo identificado.' }}
          </div>
        </div>

        <!-- Critérios de Aceite (DoD) -->
        <div class="space-y-3">
          <h4 class="text-xs font-bold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
            <CheckCircle2 class="w-4 h-4 text-emerald-400" />
            Critérios de Aceite (Definition of Done)
          </h4>
          <div
            v-if="featureData.acceptance_criteria && featureData.acceptance_criteria.length > 0"
            class="space-y-2"
          >
            <div
              v-for="(crit, idx) in featureData.acceptance_criteria"
              :key="idx"
              class="flex items-start gap-2.5 p-2.5 bg-slate-800/60 border border-slate-700/50 rounded-xl text-xs text-slate-300"
            >
              <div class="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0 mt-0.5">
                ✓
              </div>
              <span>{{ crit }}</span>
            </div>
          </div>
        </div>

        <!-- Notas Técnicas e Justificativa de Esforço -->
        <div class="space-y-3">
          <h4 class="text-xs font-bold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
            <Code class="w-4 h-4 text-indigo-400" />
            Arquitetura & Estimativa de Esforço
          </h4>
          <div class="p-3.5 bg-slate-950 border border-slate-800 rounded-xl space-y-2 text-xs font-mono">
            <div class="text-slate-400">
              <span class="text-indigo-400 font-bold">Esforço:</span> {{ featureData.effort_breakdown || 'Estimado em 2 sprints de desenvolvimento.' }}
            </div>
            <div class="text-slate-400">
              <span class="text-emerald-400 font-bold">Stack Recomendada:</span> {{ featureData.technical_notes || 'Endpoints assíncronos no FastAPI + componente reativo no Vue 3.' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
