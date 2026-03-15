<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUIStore } from '@/stores/ui';
import TransactionFormModal from '@/components/transaction/TransactionFormModal.vue';

const { t } = useI18n();
const uiStore = useUIStore();

const showModal = ref(false);

const isMobile = computed(() => uiStore.isMobileMode);

function openQuickRecord() {
  showModal.value = true;
}

function handleSave() {
  showModal.value = false;
}

function handleClose() {
  showModal.value = false;
}
</script>

<template>
  <Transition name="fab">
    <button
      v-if="isMobile"
      class="fab"
      @click="openQuickRecord"
      :aria-label="t('transactions.addTransaction')"
      :title="t('transactions.addTransaction')"
    >
      <span class="fab-icon">+</span>
    </button>
  </Transition>

  <TransactionFormModal
    v-if="showModal"
    mode="create"
    @close="handleClose"
    @save="handleSave"
  />
</template>

<style scoped>
.fab {
  position: fixed;
  bottom: calc(80px + env(safe-area-inset-bottom, 0px));
  right: var(--space-5);
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-size: 32px;
  font-weight: var(--font-weight-regular);
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.4);
  transition: all var(--duration-fast) var(--ease-default);
  z-index: var(--z-index-fab);
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.fab:hover {
  transform: scale(1.08);
  background: var(--color-primary-dark);
  box-shadow: 0 6px 20px rgba(0, 122, 255, 0.5);
}

.fab:active {
  transform: scale(0.95);
}

.fab-icon {
  line-height: 1;
  margin-top: -2px;
}

/* Transition */
.fab-enter-active,
.fab-leave-active {
  transition: transform var(--duration-fast) var(--ease-spring),
              opacity var(--duration-fast) var(--ease-default);
}

.fab-enter-from,
.fab-leave-to {
  transform: scale(0);
  opacity: 0;
}
</style>
