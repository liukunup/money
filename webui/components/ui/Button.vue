<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  text?: string;
  variant?: 'primary' | 'secondary' | 'tertiary' | 'destructive' | 'success';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  type?: 'button' | 'submit' | 'reset';
  fullWidth?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  text: '',
  variant: 'primary',
  size: 'medium',
  disabled: false,
  loading: false,
  type: 'button',
  fullWidth: false,
});

const emit = defineEmits<{
  click: [event: MouseEvent];
}>();

const buttonClasses = computed(() => {
  const classes = ['btn'];

  // Variant classes
  classes.push(`btn--${props.variant}`);

  // Size classes
  classes.push(`btn--${props.size}`);

  // State classes
  if (props.disabled || props.loading) {
    classes.push('btn--disabled');
  }

  // Full width
  if (props.fullWidth) {
    classes.push('btn--full-width');
  }

  return classes.join(' ');
});

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event);
  }
};
</script>

<template>
  <button
    :type="type"
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="btn__spinner"></span>
    <span v-else class="btn__content">
      <slot>{{ text }}</slot>
    </span>
  </button>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-family);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-default);
  white-space: nowrap;
  position: relative;
  overflow: hidden;
}

/* Primary Variant */
.btn--primary {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn--primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn--primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: none;
}

/* Secondary Variant */
.btn--secondary {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.btn--secondary:hover:not(:disabled) {
  background: var(--color-separator-opaque);
}

/* Tertiary Variant */
.btn--tertiary {
  background: transparent;
  color: var(--color-primary);
}

.btn--tertiary:hover:not(:disabled) {
  background: rgba(0, 122, 255, 0.1);
}

/* Destructive Variant */
.btn--destructive {
  background: var(--color-error);
  color: var(--color-text-inverse);
}

.btn--destructive:hover:not(:disabled) {
  filter: brightness(0.9);
}

/* Success Variant */
.btn--success {
  background: var(--color-success);
  color: var(--color-text-inverse);
}

.btn--success:hover:not(:disabled) {
  filter: brightness(0.95);
}

/* Sizes */
.btn--small {
  height: 36px;
  padding: 0 var(--space-3);
  font-size: var(--font-size-sm);
}

.btn--medium {
  height: 44px;
  padding: 0 var(--space-4);
  font-size: var(--font-size-base);
}

.btn--large {
  height: 52px;
  padding: 0 var(--space-6);
  font-size: var(--font-size-lg);
}

/* Disabled State */
.btn--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Full Width */
.btn--full-width {
  width: 100%;
}

/* Spinner */
.btn__spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Content */
.btn__content {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
</style>
