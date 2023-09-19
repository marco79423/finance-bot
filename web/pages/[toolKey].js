import React from 'react'
import {getCookie} from 'cookies-next'
import {serverSideTranslations} from 'next-i18next/serverSideTranslations'

import {useToolInfo} from '../contexts/toolInfo'
import {DeveloperModeKey} from '../contexts/developerMode'
import detectMobileByReq from '../utils/detectMobileByReq'
import {AllToolInfos, AllToolConfigMap, AllToolInfoMap} from '../core/tools'
import ExtraMetaHead from '../components/modules/ExtraMetaHead'
import {useTranslation} from 'next-i18next'
import i18config from '../next-i18next.config'



export const getServerSideProps = async ({req, res, params, locale, query}) => {
  const toolKey = params.toolKey
  const toolInfo = AllToolInfoMap[toolKey]

  if (!toolInfo) {
    return {
      notFound: true
    }
  }

  const developMode = !!+getCookie(DeveloperModeKey, {req, res})
  if (!developMode && toolInfo?.isPrivate) {
    return {
      notFound: true
    }
  }

  const isMobile = detectMobileByReq(req)
  return {
    props: {
      ...await serverSideTranslations(locale, ['base'], ),
      ctx: {
        developMode,
        isMobile,
        query: query?.q ? query?.q : '',
        toolInfo,
        allToolInfos: AllToolInfos,
        locales: i18config.i18n.locales,

        defaultData: {
        }
      },
    },
  }
}


export default function ToolPage() {
  const {t} = useTranslation()
  const toolInfo = useToolInfo()
  const ToolComponent = AllToolConfigMap[toolInfo.key].Component

  return (
    <>
      <ExtraMetaHead
        title={t(toolInfo.key)}
        description={t(`${toolInfo.key}.description`)}
        keywords={t(`${toolInfo.key}.keywords`)}
      />

      <ToolComponent/>
    </>
  )
}
