<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  variant?: 'default' | 'elevated';
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
});

const cardClasses = computed(() => {
  const classes = ['card'];
  if (props.variant === 'elevated') {
    classes.push('card--elevated');
  }
  return classes.join(' ');
});
</script>

<template>
  <div :class="cardClasses">
    <slot></slot>
  </div>
</template>

<style scoped>
.card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  transition: transform var(--duration-fast) var(--ease-default),
              box-shadow var(--duration-fast) var(--ease-default);
}

.card--elevated {
  box-shadow: var(--shadow-md);
}

.card--elevated:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}
</style>
