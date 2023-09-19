import React from 'react'
import Head from 'next/head'
import {appWithTranslation, useTranslation} from 'next-i18next'
import {CacheProvider} from '@emotion/react'
import {CssBaseline} from '@mui/material'

import {HostUrl} from '../config/vars.config'
import Manifest from '../public/manifest.json'
import createEmotionCache from '../utils/createEmotionCache'
import useCanonicalUrl from '../utils/useCanonicalUrl'
import AppProvider from '../contexts/AppProvider'

// Client-side cache, shared for the whole session of the user in the browser.
const clientSideEmotionCache = createEmotionCache()

function App({Component, emotionCache = clientSideEmotionCache, pageProps}) {
  const canonicalUrl = useCanonicalUrl(HostUrl)
  const {t} = useTranslation('base')

  return (
    <CacheProvider value={emotionCache}>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"/>

        <link rel="canonical" href={canonicalUrl}/>

        <meta name="application-name" content={t('site-name')}/>
        <meta name="apple-mobile-web-app-capable" content="yes"/>
        <meta name="apple-mobile-web-app-status-bar-style" content="default"/>
        <meta name="apple-mobile-web-app-title" content={Manifest.short_name}/>
        <meta name="theme-color" content={Manifest.theme_color}/>

        <meta name="twitter:card" content="summary"/>
        <meta name="twitter:url" content={canonicalUrl}/>
        <meta name="twitter:image" content={`${HostUrl}/logo.png`}/>
        <meta name="twitter:creator" content="@marco79423"/>

        <meta property="og:type" content="website"/>
        <meta property="og:site_name" content={t('site-name')}/>
        <meta property="og:url" content={canonicalUrl}/>
        <meta property="og:image" content={`${HostUrl}/logo.png`}/>
      </Head>

      {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
      <CssBaseline/>

      <AppProvider pageProps={pageProps}>
        <Component {...pageProps} />
      </AppProvider>

    </CacheProvider>
  )
}

export default appWithTranslation(App)
