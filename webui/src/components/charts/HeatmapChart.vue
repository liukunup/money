<template>
  <div class="heatmap-chart">
    <div class="heatmap-header">
      <div class="period-selector">
        <button 
          v-for="p in periods" 
          :key="p.value"
          :class="['period-btn', { active: selectedPeriod === p.value }]"
          @click="selectedPeriod = p.value"
        >
          {{ p.label }}
        </button>
      </div>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'

interface Props {
  data?: number[][]
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
})

const emit = defineEmits<{
  periodChange: [period: 'week' | 'month' | 'year']
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: any = null
const selectedPeriod = ref<'week' | 'month' | 'year'>('month')

const periods = [
  { value: 'week', label: 'Week' },
  { value: 'month', label: 'Month' },
  { value: 'year', label: 'Year' },
] as const

const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

const getAxisLabels = (period: string) => {
  if (period === 'week') {
    return { xAxis: weekDays, yAxis: ['Week 1'] }
  } else if (period === 'month') {
    return { xAxis: Array.from({ length: 31 }, (_, i) => String(i + 1)), yAxis: monthNames }
  } else {
    return { xAxis: monthNames, yAxis: ['Year -3', 'Year -2', 'Year -1', 'Current'] }
  }
}

const initChart = async () => {
  if (!chartRef.value) return

  try {
    const echarts = await import('echarts')
    chartInstance = echarts.init(chartRef.value)
    updateChart()
  } catch (error) {
    console.error('Failed to load ECharts:', error)
    chartRef.value.innerHTML = `
      <div class="chart-error">
        <p>Chart library not installed</p>
      </div>
    `
  }
}

const updateChart = () => {
  if (!chartInstance) return

  const { xAxis, yAxis } = getAxisLabels(selectedPeriod.value)
  
  const maxValue = Math.max(...props.data.map(d => d[2] || 0), 1)

  const option = {
    tooltip: {
      position: 'top',
      backgroundColor: 'var(--color-surface-tertiary)',
      borderColor: 'var(--color-border)',
      textStyle: {
        color: 'var(--color-text-primary)',
      },
      formatter: (params: any) => {
        const value = params.data?.[2] || 0
        return `
          <div style="display: flex; flex-direction: column; gap: 4px;">
            <div style="font-weight: 600;">Spending</div>
            <div style="color: var(--color-text-secondary);">
              ${formatCurrency(value)}
            </div>
          </div>
        `
      },
    },
    grid: {
      left: '15%',
      right: '10%',
      top: '10%',
      bottom: '15%',
    },
    xAxis: {
      type: 'category',
      data: xAxis,
      splitArea: {
        show: true,
      },
      axisLabel: {
        color: 'var(--color-text-secondary)',
        fontSize: 11,
      },
      axisLine: {
        lineStyle: {
          color: 'var(--color-border)',
        },
      },
    },
    yAxis: {
      type: 'category',
      data: yAxis,
      splitArea: {
        show: true,
      },
      axisLabel: {
        color: 'var(--color-text-secondary)',
        fontSize: 11,
      },
      axisLine: {
        lineStyle: {
          color: 'var(--color-border)',
        },
      },
    },
    visualMap: {
      min: 0,
      max: maxValue,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      inRange: {
        color: ['#f0f9ff', '#007AFF', '#FF3B30'],
      },
      textStyle: {
        color: 'var(--color-text-secondary)',
      },
    },
    series: [
      {
        name: 'Spending',
        type: 'heatmap',
        data: props.data,
        label: {
          show: false,
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  }

  chartInstance.setOption(option)
}

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

watch(selectedPeriod, (newPeriod) => {
  emit('periodChange', newPeriod)
})

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
  }
})

watch(
  () => props.data,
  () => {
    updateChart()
  },
  { deep: true }
)
</script>

<style scoped>
.heatmap-chart {
  width: 100%;
  height: 100%;
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.heatmap-header {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.period-selector {
  display: flex;
  gap: 8px;
  background: var(--color-surface-secondary);
  padding: 4px;
  border-radius: var(--radius-lg);
}

.period-btn {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all 0.2s;
}

.period-btn:hover {
  color: var(--color-text-primary);
}

.period-btn.active {
  background: var(--color-primary);
  color: #fff;
}

.chart-container {
  flex: 1;
  width: 100%;
  min-height: 350px;
}

.chart-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary);
  text-align: center;
  padding: 20px;
}
</style>