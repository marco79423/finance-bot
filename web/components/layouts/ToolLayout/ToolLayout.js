import React from 'react'
import fp from 'lodash/fp'
import {useTranslation} from 'next-i18next'

import {useToolInfo} from '../../../contexts/toolInfo'
import useAllToolInfos from '../../../hooks/useAllToolInfos'
import AppLayout from '../AppLayout'
import Navbar from './Navbar'
import ToolSettings from './ToolSettings'


export default function ToolLayout({children, ...props}) {
  const toolInfo = useToolInfo()
  const {t} = useTranslation()
  const relatedTools = useRelatedTools()

  return (
    <AppLayout
      namePrefix={'tool'}
      title={t(`${toolInfo.key}`)}
      description={t(`${toolInfo.key}.description`)}
      relatedTools={relatedTools}
      navbar={<Navbar group={toolInfo.group}/>}
      settings={<ToolSettings/>}
      {...props}
    >
      {children}
    </AppLayout>
  )
}


function useRelatedTools() {
  const currentToolInfo = useToolInfo()
  const allToolInfos = useAllToolInfos()
  return React.useMemo(() =>
      fp.flow(
        fp.filter(toolInfo => toolInfo.group === currentToolInfo.group && toolInfo.key !== currentToolInfo.key)
      )(allToolInfos),
    [allToolInfos, currentToolInfo])
}
