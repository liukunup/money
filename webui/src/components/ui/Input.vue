<script setup lang="ts">
import { ref, computed, watch } from 'vue';

interface Props {
  modelValue?: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'select';
  label?: string;
  placeholder?: string;
  error?: string | null;
  helperText?: string;
  disabled?: boolean;
  required?: boolean;
  id?: string;
  name?: string;
  autocomplete?: string;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  type: 'text',
  label: '',
  placeholder: '',
  error: '',
  helperText: '',
  disabled: false,
  required: false,
  id: '',
  name: '',
  autocomplete: 'off',
});

const emit = defineEmits<{
  'update:modelValue': [value: string];
  blur: [event: FocusEvent];
  focus: [event: FocusEvent];
}>();

const inputRef = ref<HTMLInputElement | null>(null);
const showPassword = ref(false);
const isFocused = ref(false);

// Generate unique ID if not provided
const inputId = computed(() => props.id || `input-${Math.random().toString(36).slice(2, 9)}`);

// Determine if we should show the password toggle
const showPasswordToggle = computed(() => props.type === 'password');

// Compute the actual input type
const inputType = computed(() => {
  if (props.type === 'password' && showPassword.value) {
    return 'text';
  }
  if (props.type === 'select') {
    return 'select';
  }
  return props.type;
});

// Check if there's content in the input
const hasContent = computed(() => !!props.modelValue);

// Determine if label should be floating
const isLabelFloating = computed(() => isFocused.value || hasContent.value);

// Handle input changes
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  emit('update:modelValue', target.value);
};

// Handle focus
const handleFocus = (event: FocusEvent) => {
  isFocused.value = true;
  emit('focus', event);
};

// Handle blur
const handleBlur = (event: FocusEvent) => {
  isFocused.value = false;
  emit('blur', event);
};

// Toggle password visibility
const togglePassword = () => {
  showPassword.value = !showPassword.value;
};

// Focus the input
const focus = () => {
  inputRef.value?.focus();
};

// Expose focus method
defineExpose({
  focus,
});
</script>

<template>
  <div class="input-wrapper" :class="{ 'input-wrapper--error': error, 'input-wrapper--disabled': disabled }">
    <div class="input-container">
      <input
        v-if="type !== 'select'"
        :id="inputId"
        ref="inputRef"
        :type="inputType"
        :value="modelValue"
        :placeholder="isFocused ? placeholder : ''"
        :disabled="disabled"
        :required="required"
        :name="name"
        :autocomplete="autocomplete"
        class="input-field"
        :class="{
          'input-field--focused': isFocused,
          'input-field--has-content': hasContent,
          'input-field--error': error,
        }"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
      />
      <select
        v-else
        :id="inputId"
        ref="inputRef"
        :value="modelValue"
        :disabled="disabled"
        :required="required"
        :name="name"
        class="input-field input-field--select"
        :class="{
          'input-field--focused': isFocused,
          'input-field--has-content': hasContent,
          'input-field--error': error,
        }"
        @input="handleInput"
        @blur="handleBlur"
      >
        <slot></slot>
      </select>
      </div>

      <!-- Error message -->
      <p v-if="error" class="input-error">{{ error }}</p>
      <!-- Helper text -->
      <p v-else-if="helperText" class="input-helper">{{ helperText }}</p>
  </div>
</template>

<style scoped>
.input-wrapper {
  position: relative;
  width: 100%;
  margin-bottom: var(--space-4);
}

.input-container {
  position: relative;
  width: 100%;
}

.input-field {
  width: 100%;
  height: 52px;
  padding: 24px var(--space-4) var(--space-2);
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-separator-opaque);
  border-radius: var(--radius-md);
  outline: none;
  transition: all var(--duration-fast) var(--ease-default);
}

.input-field::placeholder {
  color: transparent;
}

.input-field:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.15);
}

.input-field--error {
  border-color: var(--color-error);
}

.input-field--error:focus {
  box-shadow: 0 0 0 3px rgba(255, 59, 48, 0.15);
}

.input-field:disabled {
  background: var(--color-bg-tertiary);
  cursor: not-allowed;
  opacity: 0.7;
}

/* Floating Label */
.input-label {
  position: absolute;
  left: var(--space-4);
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  pointer-events: none;
  transition: all var(--duration-fast) var(--ease-default);
}

.input-label--floating {
  top: 10px;
  transform: translateY(0);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.input-label--focused {
  color: var(--color-primary);
}

.input-label--error {
  color: var(--color-error);
}

.input-label__required {
  color: var(--color-error);
  margin-left: 2px;
}

/* Password Toggle */
.input-toggle {
  position: absolute;
  right: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  padding: var(--space-1);
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: color var(--duration-fast) var(--ease-default);
}

.input-toggle:hover {
  color: var(--color-text-primary);
}

/* Error & Helper Text */
.input-error {
  margin-top: var(--space-1);
  font-size: var(--font-size-xs);
  color: var(--color-error);
  animation: slideIn var(--duration-fast) var(--ease-default);
}

.input-helper {
  margin-top: var(--space-1);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
