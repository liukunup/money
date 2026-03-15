<script setup lang="ts">
import { ref, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';

interface SpeechRecognitionEvent extends Event {
  readonly resultIndex: number;
  readonly results: SpeechRecognitionResultList;
}

interface SpeechRecognitionErrorEvent extends Event {
  readonly error: string;
  readonly message: string;
}

interface SpeechRecognitionResultList {
  readonly length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  readonly isFinal: boolean;
  readonly length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionAlternative {
  readonly transcript: string;
  readonly confidence: number;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onstart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any) | null;
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => any) | null;
  onend: ((this: SpeechRecognition, ev: Event) => any) | null;
  start(): void;
  stop(): void;
}

const { t } = useI18n();

const emit = defineEmits<{
  result: [text: string];
  error: [message: string];
  start: [];
  stop: [];
}>();

const isListening = ref(false);
const isSupported = ref(false);
const transcript = ref('');

let recognition: SpeechRecognition | null = null;

onUnmounted(() => {
  if (recognition) {
    recognition.stop();
  }
});

function initSpeechRecognition() {
  const SpeechRecognitionAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  
  if (!SpeechRecognitionAPI) {
    isSupported.value = false;
    emit('error', 'Speech recognition not supported in this browser');
    return false;
  }

  isSupported.value = true;
  recognition = new SpeechRecognitionAPI();
  recognition!.continuous = false;
  recognition!.interimResults = true;
  recognition!.lang = 'zh-CN';

  recognition!.onstart = () => {
    isListening.value = true;
    emit('start');
  };

  recognition!.onresult = (event: SpeechRecognitionEvent) => {
    let finalTranscript = '';
    let interimTranscript = '';

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const result = event.results[i];
      if (result.isFinal) {
        finalTranscript += result[0].transcript;
      } else {
        interimTranscript += result[0].transcript;
      }
    }

    transcript.value = finalTranscript || interimTranscript;
    if (finalTranscript) {
      emit('result', finalTranscript);
    }
  };

  recognition!.onerror = (event: SpeechRecognitionErrorEvent) => {
    isListening.value = false;
    let errorMessage = t('voiceRecognition.error');
    
    switch (event.error) {
      case 'no-speech':
        errorMessage = t('voiceRecognition.noSpeech');
        break;
      case 'audio-capture':
        errorMessage = t('voiceRecognition.noMicrophone');
        break;
      case 'not-allowed':
        errorMessage = t('voiceRecognition.notAllowed');
        break;
    }
    
    emit('error', errorMessage);
  };

  recognition!.onend = () => {
    isListening.value = false;
    emit('stop');
  };

  return true;
}

function toggleListening() {
  if (!isSupported.value) {
    if (!initSpeechRecognition()) {
      return;
    }
  }

  if (isListening.value) {
    recognition?.stop();
  } else {
    transcript.value = '';
    recognition?.start();
  }
}
</script>

<template>
  <button
    type="button"
    class="voice-input-btn"
    :class="{ listening: isListening, unsupported: !isSupported }"
    :title="isSupported ? (isListening ? t('voiceRecognition.stop') : t('voiceRecognition.start')) : t('voiceRecognition.notSupported')"
    @click="toggleListening"
  >
    <svg v-if="!isListening" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
      <line x1="12" y1="19" x2="12" y2="23"/>
      <line x1="8" y1="23" x2="16" y2="23"/>
    </svg>
    <span v-else class="voice-wave">
      <span class="wave-bar"></span>
      <span class="wave-bar"></span>
      <span class="wave-bar"></span>
    </span>
  </button>
</template>

<style scoped>
.voice-input-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 50%;
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
}

.voice-input-btn:hover:not(.unsupported) {
  background: var(--color-primary);
  color: white;
}

.voice-input-btn.listening {
  background: #FF3B30;
  color: white;
  animation: pulse 1.5s infinite;
}

.voice-input-btn.unsupported {
  opacity: 0.5;
  cursor: not-allowed;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(255, 59, 48, 0.4);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 10px rgba(255, 59, 48, 0);
  }
}

.voice-wave {
  display: flex;
  align-items: center;
  gap: 2px;
  height: 20px;
}

.wave-bar {
  width: 3px;
  height: 100%;
  background: white;
  border-radius: 2px;
  animation: wave 0.5s ease-in-out infinite;
}

.wave-bar:nth-child(1) {
  animation-delay: 0s;
}

.wave-bar:nth-child(2) {
  animation-delay: 0.15s;
}

.wave-bar:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes wave {
  0%, 100% {
    transform: scaleY(0.5);
  }
  50% {
    transform: scaleY(1);
  }
}
</style>
