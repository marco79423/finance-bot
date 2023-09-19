import React from 'react'
import {useRouter} from 'next/router'
import {i18n, useTranslation} from 'next-i18next'
import {setCookie} from 'cookies-next'

import Select from '../../elements/Select'
import useLocales from '../../../hooks/useLocales'


export default function LocaleSelect({...props}) {
  const [t] = useTranslation()
  const router = useRouter()

  const locales = useLocales()

  const localeSelections = React.useMemo(() => locales
    .map(locale => ({
      key: locale,
      label: t(`locales.${locale}`),
      value: locale,
    })), [locales, t])

  const onLocaleChange = React.useCallback((value) => {
    (async function () {
      // 若手動切換語言就記著使用者的選擇
      setCookie('NEXT_LOCALE', value)
      await router.replace(router.asPath, router.asPath, {locale: value})
    })()
  }, [router])

  React.useEffect(() => {
    if (locales.length > 0 && locales.indexOf(i18n.language) === -1) {
      onLocaleChange(locales[0])
    }
  }, [onLocaleChange, locales])

  return (
    <Select
      currentValue={i18n.language}
      selections={localeSelections}
      onSelectionChange={onLocaleChange}
      {...props}
    />
  )
}

