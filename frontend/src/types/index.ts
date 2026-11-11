export interface Niche {
  id: string
  name: string
  slug: string
  description?: string
  total_analyses: number
  created_at: string
  updated_at: string
}

export interface PainPoint {
  category: string
  title: string
  description?: string
  frequency_percentage: number
  severity: 'low' | 'medium' | 'high' | 'critical'
}

export interface RecommendedFeature {
  title: string
  rationale: string
  reach: number
  impact: number
  confidence: number
  effort: number
  rice_score: number
}

export interface HookCopy {
  placement: string
  hook_text: string
  intent: string
}

export interface FaqItem {
  question: string
  answer_suggestion: string
  friction_level: number
}

export interface Analysis {
  id: string
  niche_id: string
  keyword: string
  mode: string
  sources_selected: string[]
  sample_size: number
  created_at: string
  is_cached?: boolean
  pain_points: PainPoint[]
  recommended_features: RecommendedFeature[]
  hook_copies: HookCopy[]
  faq_items: FaqItem[]
}

export interface Dossier {
  analysis_id: string
  keyword: string
  markdown_content: string
  created_at: string
}
