import React from 'react'
import {useTranslation} from 'next-i18next'

import {useAppCtx} from '../contexts/appCtx'
import {useDeveloperMode} from '../contexts/developerMode'


export default function useAllToolInfos() {
  const {t} = useTranslation()
  const appCtx = useAppCtx()
  const developMode = useDeveloperMode()
  return React.useMemo(() => appCtx.allToolInfos
    .filter(info => developMode || !info.isPrivate)
    .map(info => ({
      ...info,
      label: t(info.key)
    })), [t, developMode, appCtx.allToolInfos])
}
