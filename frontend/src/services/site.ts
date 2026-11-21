import api from '@/services/api'
import type { SiteContent } from '@/types/site'

export async function fetchSiteContent(): Promise<SiteContent> {
  const response = await api.get<SiteContent>('/api/v1/site/')
  return response.data
}
