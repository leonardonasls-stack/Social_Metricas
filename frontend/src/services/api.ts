import axios from 'axios'
import type { Niche, Analysis, Dossier } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const fetchNiches = async (): Promise<Niche[]> => {
  const response = await api.get('/niches')
  return response.data
}

export const createNiche = async (name: string, description?: string): Promise<Niche> => {
  const response = await api.post('/niches', { name, description })
  return response.data
}

export const runAnalysis = async (params: {
  niche_id: string
  keyword: string
  sources?: string[]
  force_refresh?: boolean
  mode?: string
}): Promise<Analysis> => {
  const response = await api.post('/analyses', {
    niche_id: params.niche_id,
    keyword: params.keyword,
    sources: params.sources || ['reddit', 'tiktok', 'instagram', 'youtube'],
    force_refresh: params.force_refresh || false,
    mode: params.mode || 'mock'
  })
  return response.data
}

export const fetchDossier = async (analysisId: string): Promise<Dossier> => {
  const response = await api.get(`/analyses/${analysisId}/dossier`)
  return response.data
}

export const downloadDossierPdf = async (analysisId: string, keyword: string): Promise<void> => {
  try {
    const response = await api.get(`/analyses/${analysisId}/pdf`, {
      responseType: 'blob'
    })
    
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `Dossie_${keyword.toLowerCase().replace(/[^a-z0-9]/g, '_')}.pdf`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error: any) {
    if (error.response && error.response.data instanceof Blob) {
      const text = await error.response.data.text()
      try {
        const json = JSON.parse(text)
        throw new Error(json.detail || text)
      } catch {
        throw new Error(text)
      }
    }
    throw error
  }
}

