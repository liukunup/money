<template>
  <div class="line-chart">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'

interface Props {
  title: string
  xData: string[]
  series: Array<{ name: string; data: number[]; color: string }>
}

const props = defineProps<Props>()

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: any = null

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
      trigger: 'axis',
      backgroundColor: 'var(--color-surface-tertiary)',
      borderColor: 'var(--color-border)',
      textStyle: {
        color: 'var(--color-text-primary)',
      },
      formatter: (params: any) => {
        let result = `<div style="font-weight: 600; margin-bottom: 8px;">${params[0].axisValue}</div>`
        params.forEach((param: any) => {
          result += `
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
              <span style="width: 10px; height: 10px; border-radius: 50%; background: ${param.color};"></span>
              <span style="color: var(--color-text-secondary);">${param.seriesName}:</span>
              <span style="font-weight: 600;">${formatCurrency(param.value)}</span>
            </div>
          `
        })
        return result
      },
    },
    legend: {
      data: props.series.map((s) => s.name),
      bottom: 0,
      textStyle: {
        color: 'var(--color-text-secondary)',
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: props.xData,
      axisLine: {
        lineStyle: {
          color: 'var(--color-border)',
        },
      },
      axisLabel: {
        color: 'var(--color-text-tertiary)',
        fontSize: 12,
      },
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false,
      },
      axisLabel: {
        color: 'var(--color-text-tertiary)',
        fontSize: 12,
        formatter: (value: number) => formatCurrency(value, true),
      },
      splitLine: {
        lineStyle: {
          color: 'var(--color-border)',
          type: 'dashed',
        },
      },
    },
    series: props.series.map((s) => ({
      name: s.name,
      type: 'line',
      smooth: true,
      data: s.data,
      itemStyle: {
        color: s.color,
      },
      lineStyle: {
        width: 2,
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: `${s.color}20` },
            { offset: 1, color: `${s.color}05` },
          ],
        },
      },
    })),
  }

  chartInstance.setOption(option)
}

const formatCurrency = (amount: number, short: boolean = false): string => {
  if (short) {
    if (amount >= 1000) {
      return `¥${(amount / 1000).toFixed(1)}k`
    }
    return `¥${amount.toFixed(0)}`
  }
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
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
  () => [props.xData, props.series],
  () => {
    updateChart()
  },
  { deep: true }
)
</script>

<style scoped>
.line-chart {
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
</style>
