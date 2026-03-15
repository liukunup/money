<script setup lang="ts">
interface Props {
  clickable?: boolean;
}

withDefaults(defineProps<Props>(), {
  clickable: false,
});
</script>

<template>
  <div class="list-item" :class="{ 'list-item--clickable': clickable }">
    <slot></slot>
  </div>
</template>

<style scoped>
.list-item {
  display: flex;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  transition: background var(--duration-fast) var(--ease-default);
}

.list-item--clickable {
  cursor: pointer;
}

.list-item--clickable:hover {
  background: var(--color-bg-secondary);
}

.list-item--clickable:active {
  background: var(--color-bg-tertiary);
}
</style>
