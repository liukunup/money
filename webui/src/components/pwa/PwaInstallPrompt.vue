<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const deferredPrompt = ref<any>(null);
const showInstallPrompt = ref(false);
const isInstalled = ref(false);

onMounted(() => {
  if (window.matchMedia('(display-mode: standalone)').matches) {
    isInstalled.value = true;
    return;
  }

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt.value = e;
    setTimeout(() => {
      showInstallPrompt.value = true;
    }, 3000);
  });

  window.addEventListener('appinstalled', () => {
    isInstalled.value = true;
    showInstallPrompt.value = false;
    deferredPrompt.value = null;
  });
});

async function handleInstall() {
  if (!deferredPrompt.value) return;

  await deferredPrompt.value.prompt();
  
  const { outcome } = await deferredPrompt.value.userChoice;
  if (outcome === 'accepted') {
    isInstalled.value = true;
  }
  
  showInstallPrompt.value = false;
  deferredPrompt.value = null;
}

function handleDismiss() {
  showInstallPrompt.value = false;
}
</script>

<template>
  <Teleport to="body">
    <Transition name="slide-up">
      <div v-if="showInstallPrompt && !isInstalled" class="pwa-install-prompt">
        <div class="pwa-prompt-content">
          <div class="pwa-prompt-icon">
            <span class="pwa-icon">💰</span>
          </div>
          <div class="pwa-prompt-text">
            <h3 class="pwa-prompt-title">{{ t('pwa.install.title') }}</h3>
            <p class="pwa-prompt-description">{{ t('pwa.install.description') }}</p>
          </div>
        </div>
        <div class="pwa-prompt-actions">
          <button class="pwa-dismiss-btn" @click="handleDismiss">
            {{ t('pwa.install.later') }}
          </button>
          <button class="pwa-install-btn" @click="handleInstall">
            {{ t('pwa.install.install') }}
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.pwa-install-prompt {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--color-bg-primary);
  border-top-left-radius: var(--radius-xl);
  border-top-right-radius: var(--radius-xl);
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.15);
  padding: var(--space-5);
  z-index: 9999;
  padding-bottom: calc(var(--space-5) + env(safe-area-inset-bottom, 0px));
}

.pwa-prompt-content {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.pwa-prompt-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  background: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.pwa-icon {
  font-size: 28px;
}

.pwa-prompt-text {
  flex: 1;
}

.pwa-prompt-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1) 0;
}

.pwa-prompt-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.pwa-prompt-actions {
  display: flex;
  gap: var(--space-3);
}

.pwa-dismiss-btn {
  flex: 1;
  padding: var(--space-3) var(--space-4);
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
}

.pwa-dismiss-btn:hover {
  background: var(--color-bg-secondary);
}

.pwa-install-btn {
  flex: 1;
  padding: var(--space-3) var(--space-4);
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
}

.pwa-install-btn:hover {
  background: var(--color-primary-dark);
}

/* Transition */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform var(--duration-normal) var(--ease-spring),
              opacity var(--duration-normal) var(--ease-default);
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
