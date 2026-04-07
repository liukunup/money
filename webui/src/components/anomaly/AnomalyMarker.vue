<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  level: 'warning' | 'anomaly' | 'alert';
  reason?: string;
}

const props = defineProps<Props>();

const levelConfig = {
  warning: {
    icon: '⚠️',
    color: '#FF9500',
    bgColor: 'rgba(255, 149, 0, 0.1)',
    label: 'Warning'
  },
  anomaly: {
    icon: '🔴',
    color: '#FF3B30',
    bgColor: 'rgba(255, 59, 48, 0.1)',
    label: 'Anomaly'
  },
  alert: {
    icon: '🚨',
    color: '#AF52DE',
    bgColor: 'rgba(175, 82, 222, 0.1)',
    label: 'Alert'
  }
};

const config = computed(() => levelConfig[props.level]);
</script>

<template>
  <div 
    class="anomaly-marker"
    :style="{ 
      color: config.color,
      backgroundColor: config.bgColor 
    }"
    :title="reason || config.label"
  >
    <span class="anomaly-marker__icon">{{ config.icon }}</span>
    <span class="anomaly-marker__label">{{ config.label }}</span>
  </div>
</template>

<style scoped>
.anomaly-marker {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.anomaly-marker__icon {
  font-size: 10px;
}

.anomaly-marker__label {
  text-transform: uppercase;
}
</style>
