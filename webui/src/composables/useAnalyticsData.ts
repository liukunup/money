import { ref, computed } from 'vue'
import budgetsService from '@/services/budgets.service'
import type { CashFlowData, HeatmapData } from '@/types/models'

export function useAnalyticsData() {
  const cashFlowData = ref<CashFlowData>({ nodes: [], links: [] })
  const heatmapData = ref<number[][]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchCashFlow = async (startDate?: string, endDate?: string) => {
    loading.value = true
    error.value = null
    try {
      cashFlowData.value = await budgetsService.getCashFlow({ start_date: startDate, end_date: endDate })
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch cash flow data'
      console.error('Cash flow fetch error:', e)
    } finally {
      loading.value = false
    }
  }

  const fetchHeatmap = async (period: 'week' | 'month' | 'year' = 'month') => {
    loading.value = true
    error.value = null
    try {
      const data = await budgetsService.getHeatmap(period)
      heatmapData.value = data.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch heatmap data'
      console.error('Heatmap fetch error:', e)
    } finally {
      loading.value = false
    }
  }

  const sankeyNodes = computed(() => cashFlowData.value.nodes)
  const sankeyLinks = computed(() => {
    return cashFlowData.value.links.map(link => ({
      source: typeof link.source === 'number' 
        ? cashFlowData.value.nodes[link.source]?.name 
        : link.source,
      target: typeof link.target === 'number' 
        ? cashFlowData.value.nodes[link.target]?.name 
        : link.target,
      value: link.value,
    }))
  })

  return {
    cashFlowData,
    heatmapData,
    loading,
    error,
    fetchCashFlow,
    fetchHeatmap,
    sankeyNodes,
    sankeyLinks,
  }
}