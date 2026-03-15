<script setup lang="ts">
interface Props {
  divided?: boolean;
  grouped?: boolean;
}

withDefaults(defineProps<Props>(), {
  divided: true,
  grouped: false,
});
</script>

<template>
  <div class="list" :class="{ 'list--divided': divided, 'list--grouped': grouped }">
    <slot></slot>
  </div>
</template>

<style scoped>
.list {
  width: 100%;
}

.list--divided .list-item:not(:last-child) {
  border-bottom: 1px solid var(--color-separator);
}

.list--grouped {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.list--grouped .list-item {
  padding: var(--space-3) var(--space-4);
}

.list--grouped .list-item:not(:last-child) {
  border-bottom: 1px solid var(--color-separator);
}
</style>
