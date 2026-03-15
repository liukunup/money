import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN.json'
import enUS from './locales/en-US.json'

export type LocaleType = 'zh-CN' | 'en-US'

// Get saved locale or default to zh-CN
function getSavedLocale(): LocaleType {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('locale') as LocaleType | null
    if (saved && (saved === 'zh-CN' || saved === 'en-US')) {
      return saved
    }
  }
  return 'zh-CN'
}

export const i18n = createI18n({
  legacy: false,
  locale: getSavedLocale(),
  fallbackLocale: 'en-US',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS,
  },
})

export default i18n

export function setLocale(locale: LocaleType) {
  i18n.global.locale.value = locale
  localStorage.setItem('locale', locale)
}

export function getLocale(): LocaleType {
  return i18n.global.locale.value as LocaleType
}
