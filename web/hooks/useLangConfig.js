import React from 'react'
import langsConfig from '../config/langs.config'

export default function useLangConfig(lang) {
  return React.useMemo(() => langsConfig[lang] ?? null, [lang])
}