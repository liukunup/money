<template>
  <div class="ai-suggestion-card" v-if="suggestions.length > 0">
    <div class="card-header">
      <span class="card-title">AI Suggestions</span>
      <span v-if="isKeywordFallback" class="fallback-badge">Keyword Match</span>
    </div>
    
    <div class="suggestion-list">
      <div 
        v-for="(suggestion, index) in suggestions" 
        :key="suggestion.category_id"
        class="suggestion-item"
        :class="{ selected: selectedId === suggestion.category_id }"
        @click="selectSuggestion(suggestion.category_id)"
      >
        <div class="suggestion-icon">
          {{ suggestion.category_icon || '📁' }}
        </div>
        <div class="suggestion-info">
          <span class="category-name">{{ suggestion.category_name }}</span>
          <span class="reason">{{ suggestion.reason }}</span>
        </div>
        <div v-if="selectedId === suggestion.category_id" class="check-icon">
          ✓
        </div>
      </div>
    </div>
  </div>
  
  <div v-else-if="loading" class="ai-suggestion-card loading">
    <div class="loading-spinner"></div>
    <span>Getting AI suggestions...</span>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { aiService } from '@/services/ai.service';
import type { AISuggestion } from '@/types/models';

const props = defineProps<{
  note: string;
  enabled: boolean;
  limit?: number;
}>();

const emit = defineEmits<{
  (e: 'select', categoryId: number): void;
}>();

const suggestions = ref<AISuggestion[]>([]);
const selectedId = ref<number | null>(null);
const loading = ref(false);
const isKeywordFallback = ref(false);

const fetchSuggestions = async () => {
  if (!props.enabled || !props.note || props.note.length < 2) {
    suggestions.value = [];
    return;
  }
  
  try {
    loading.value = true;
    const response = await aiService.getSuggestions(props.note, props.limit || 3);
    suggestions.value = response.suggestions;
    
    if (suggestions.value.length > 0) {
      selectedId.value = suggestions.value[0].category_id;
      emit('select', selectedId.value);
    }
  } catch (error) {
    console.error('Failed to get suggestions:', error);
    suggestions.value = [];
  } finally {
    loading.value = false;
  }
};

const selectSuggestion = (categoryId: number) => {
  selectedId.value = categoryId;
  emit('select', categoryId);
};

watch(() => props.note, (newNote) => {
  if (newNote && props.enabled) {
    fetchSuggestions();
  } else {
    suggestions.value = [];
    selectedId.value = null;
  }
}, { immediate: true });

watch(() => props.enabled, (enabled) => {
  if (enabled && props.note) {
    fetchSuggestions();
  } else {
    suggestions.value = [];
    selectedId.value = null;
  }
});
</script>

<style scoped>
.ai-suggestion-card {
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  overflow: hidden;
}

.ai-suggestion-card.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px;
  color: #666;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e5e5;
  border-top-color: #007AFF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
}

.fallback-badge {
  font-size: 10px;
  padding: 2px 6px;
  background: #fff3e0;
  color: #ff9800;
  border-radius: 4px;
}

.suggestion-list {
  padding: 8px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.suggestion-item:hover {
  background: #f5f5f5;
}

.suggestion-item.selected {
  background: #e3f2fd;
}

.suggestion-icon {
  font-size: 24px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 8px;
}

.suggestion-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.category-name {
  font-size: 14px;
  font-weight: 500;
}

.reason {
  font-size: 12px;
  color: #666;
}

.check-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #007AFF;
  color: white;
  border-radius: 50%;
  font-size: 12px;
}
</style>
