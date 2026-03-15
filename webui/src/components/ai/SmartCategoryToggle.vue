<template>
  <div class="smart-category-toggle" :class="{ enabled: isEnabled }">
    <div class="toggle-content">
      <div class="toggle-icon">
        <svg v-if="isEnabled" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 6v6l4 2"/>
        </svg>
      </div>
      <div class="toggle-info">
        <span class="toggle-title">Smart Classification</span>
        <span class="toggle-description">
          {{ isEnabled ? 'AI will automatically suggest categories' : 'Enable to get AI-powered suggestions' }}
        </span>
      </div>
    </div>
    
    <button 
      class="toggle-switch"
      :class="{ active: isEnabled }"
      @click="toggle"
      :disabled="loading || !aiAvailable"
    >
      <span class="toggle-handle"></span>
    </button>
  </div>
  
  <div v-if="!aiAvailable && !loading" class="ai-unavailable">
    <span>AI not available. Please configure an AI provider.</span>
    <router-link to="/ai-providers">Setup</router-link>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { aiService } from '@/services/ai.service';
import type { AISettings } from '@/types/models';

const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
}>();

const loading = ref(true);
const aiAvailable = ref(false);
const isEnabled = ref(props.modelValue);

const loadSettings = async () => {
  try {
    const settings: AISettings = await aiService.getSettings();
    aiAvailable.value = settings.ai_enabled;
    isEnabled.value = aiAvailable.value && props.modelValue;
  } catch (error) {
    console.error('Failed to load AI settings:', error);
    aiAvailable.value = false;
  } finally {
    loading.value = false;
  }
};

const toggle = () => {
  if (!aiAvailable.value) return;
  isEnabled.value = !isEnabled.value;
  emit('update:modelValue', isEnabled.value);
};

onMounted(loadSettings);
</script>

<style scoped>
.smart-category-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 12px;
  transition: background 0.2s;
}

.smart-category-toggle.enabled {
  background: #e8f5e9;
}

.toggle-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.smart-category-toggle.enabled .toggle-icon {
  color: #34c759;
}

.toggle-icon svg {
  width: 24px;
  height: 24px;
}

.toggle-info {
  display: flex;
  flex-direction: column;
}

.toggle-title {
  font-size: 16px;
  font-weight: 500;
}

.toggle-description {
  font-size: 12px;
  color: #666;
}

.toggle-switch {
  width: 51px;
  height: 31px;
  background: #e5e5e5;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  position: relative;
  transition: background 0.2s;
}

.toggle-switch.active {
  background: #34c759;
}

.toggle-switch:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toggle-handle {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 27px;
  height: 27px;
  background: white;
  border-radius: 50%;
  transition: transform 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.toggle-switch.active .toggle-handle {
  transform: translateX(20px);
}

.ai-unavailable {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
  padding: 8px 12px;
  background: #fff3e0;
  border-radius: 8px;
  font-size: 12px;
}

.ai-unavailable a {
  color: #ff9800;
  font-weight: 500;
}
</style>
