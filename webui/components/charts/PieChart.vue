<template>
  <div class="pie-chart">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'

interface DataItem {
  name: string
  value: number
}

interface Props {
  title: string
  data: DataItem[]
  showIcon?: boolean
  getIcon?: (name: string) => string
}

const props = withDefaults(defineProps<Props>(), {
  showIcon: false,
})

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: any = null

// Format data with icons
const formattedData = computed(() => {
  if (!props.showIcon || !props.getIcon) {
    return props.data
  }

  return props.data.map((item) => ({
    ...item,
    name: `${props.getIcon?.(item.name) || '📊'} ${item.name}`,
  }))
})

// Calculate total
const total = computed(() => {
  return props.data.reduce((sum, item) => sum + item.value, 0)
})

// Load ECharts dynamically
const initChart = async () => {
  if (!chartRef.value) return

  try {
    // @ts-ignore - ECharts will be loaded dynamically
    const echarts = await import('echarts')
    chartInstance = echarts.init(chartRef.value)

    updateChart()
  } catch (error) {
    console.error('Failed to load ECharts:', error)
    chartRef.value.innerHTML = `
      <div class="chart-error">
        <p>Chart library not installed</p>
        <p class="error-hint">Run: npm install echarts</p>
      </div>
    `
  }
}

const updateChart = () => {
  if (!chartInstance) return

  const option = {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 17,
        fontWeight: 600,
        color: 'var(--color-text-primary)',
      },
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'var(--color-surface-tertiary)',
      borderColor: 'var(--color-border)',
      textStyle: {
        color: 'var(--color-text-primary)',
      },
      formatter: (params: any) => {
        const percent = ((params.value / total.value) * 100).toFixed(1)
        return `
          <div style="display: flex; flex-direction: column; gap: 4px;">
            <div style="font-weight: 600;">${params.name}</div>
            <div style="color: var(--color-text-secondary);">
              ${formatCurrency(params.value)} (${percent}%)
            </div>
          </div>
        `
      },
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: 0,
      top: 'middle',
      textStyle: {
        color: 'var(--color-text-secondary)',
        fontSize: 13,
      },
    },
    series: [
      {
        name: 'Expenses',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: 'var(--color-surface-primary)',
          borderWidth: 2,
        },
        label: {
          show: false,
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 600,
            color: 'var(--color-text-primary)',
            formatter: '{b}',
          },
        },
        labelLine: {
          show: false,
        },
        data: formattedData.value,
      },
    ],
  }

  chartInstance.setOption(option)
}

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

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
.pie-chart {
  width: 100%;
  height: 100%;
  min-height: 300px;
}

.chart-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
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

.error-hint {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin-top: 8px;
  background: var(--color-surface-secondary);
  padding: 8px 12px;
  border-radius: var(--radius-md);
  font-family: 'SF Mono', Monaco, 'Courier New', monospace;
}

/* Responsive Design */
@media (max-width: 768px) {
  .pie-chart {
    min-height: 350px;
  }
}
</style>
