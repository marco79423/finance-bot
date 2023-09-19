import React from 'react'
import Head from 'next/head'
import {useTranslation} from 'next-i18next'

function ExtraMetaHead({title, description, keywords}) {
  const {t} = useTranslation('base')

  const wrappedTitle = React.useMemo(() => {
    if (title) {
      return `${title} - ${t('site-name')}`
    } else {
      return t('site-name')
    }
  }, [t, title])

  return (
    <Head>
      <title>{wrappedTitle}</title>
      <meta key="description" name="description" content={wrappedTitle}/>
      <meta key="keywords" name="keywords" content={keywords}/>

      <meta key="twitter:title" name="twitter:title" content={wrappedTitle}/>
      <meta key="twitter:description" name="twitter:description" content={description}/>

      <meta key="og:title" property="og:title" content={wrappedTitle}/>
      <meta key="og:description" property="og:description" content={description}/>
    </Head>
  )
}

export default React.memo(ExtraMetaHead)
