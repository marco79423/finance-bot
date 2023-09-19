import React from 'react'
import {useTranslation} from 'next-i18next'

import ExtraMetaHead from '../components/modules/ExtraMetaHead'
import Home from '../core/tools/Home'
import {getCookie} from 'cookies-next'
import {DeveloperModeKey} from '../contexts/developerMode'
import detectMobileByReq from '../utils/detectMobileByReq'
import {serverSideTranslations} from 'next-i18next/serverSideTranslations'
import {AllToolInfos} from '../core/tools'
import i18config from '../next-i18next.config'


export const getServerSideProps = async ({req, res, locale, query}) => {
  const developMode = !!+getCookie(DeveloperModeKey, {req, res})
  const isMobile = detectMobileByReq(req)

  return {
    props: {
      ...await serverSideTranslations(locale, ['base']),
      ctx: {
        developMode,
        isMobile,
        locales: i18config.i18n.locales,
        allToolInfos: AllToolInfos,
        query: query?.q ? query?.q : '',
      },
    },
  }
}

export default function IndexPage({query}) {
  const {t} = useTranslation()

  return (
    <>
      <ExtraMetaHead
        description={t('home.title')}
        keywords={t('home.keywords')}
      />

      <Home query={query}/>
    </>
  )
}
