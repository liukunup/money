<template>
  <div class="sankey-chart">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'

interface SankeyNode {
  name: string
}

interface SankeyLink {
  source: string | number
  target: string | number
  value: number
}

interface Props {
  title?: string
  nodes?: SankeyNode[]
  links?: SankeyLink[]
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Cash Flow',
  nodes: () => [],
  links: () => [],
})

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: any = null

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
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
      triggerOn: 'mousemove',
      backgroundColor: 'var(--color-surface-tertiary)',
      borderColor: 'var(--color-border)',
      textStyle: {
        color: 'var(--color-text-primary)',
      },
      formatter: (params: any) => {
        if (params.dataType === 'edge') {
          return `
            <div style="display: flex; flex-direction: column; gap: 4px;">
              <div style="font-weight: 600;">${params.data.source} → ${params.data.target}</div>
              <div style="color: var(--color-text-secondary);">
                ${formatCurrency(params.data.value)}
              </div>
            </div>
          `
        }
        return params.name
      },
    },
    series: [
      {
        type: 'sankey',
        layout: 'none',
        emphasis: {
          focus: 'adjacency',
        },
        data: props.nodes.map((node, index) => ({
          name: node.name,
          itemStyle: {
            color: index === 0 ? '#34C759' : // Income - green
                    index === props.nodes!.length - 1 ? '#FF3B30' : // Expense - red
                    '#007AFF', // Intermediate - blue
          },
        })),
        links: props.links,
        lineStyle: {
          color: 'gradient',
          curveness: 0.5,
        },
        label: {
          color: 'var(--color-text-primary)',
          fontSize: 12,
        },
        nodeWidth: 20,
        nodeGap: 8,
        layoutIterations: 32,
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
  () => [props.nodes, props.links],
  () => {
    updateChart()
  },
  { deep: true }
)
</script>

<style scoped>
.sankey-chart {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

.chart-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
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