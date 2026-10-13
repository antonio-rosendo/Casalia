import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import enTranslations from './locales/en.json';
import esTranslations from './locales/es.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: enTranslations,
      es: esTranslations
    },
    supportedLngs: ['en', 'es'],
    nonExplicitSupportedLngs: true, // es-ES, es-MX... -> es
    load: 'languageOnly',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // not needed for react as it escapes by default
    }
  });

// Keep <html lang>, the title and the description in the current language.
function syncDocument() {
  document.documentElement.lang = i18n.language?.startsWith('es') ? 'es' : 'en';
  document.title = i18n.t('meta.title');
  document.querySelector('meta[name="description"]')?.setAttribute('content', i18n.t('meta.description'));
}
i18n.on('languageChanged', syncDocument);
syncDocument();

export default i18n;
