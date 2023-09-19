import React from 'react'
import {useTranslation} from 'next-i18next'

import {useToolInfo} from '../../../contexts/toolInfo'
import TwoPanelToolLayout from '../TwoPanelToolLayout'


export default function InputResultPanelToolLayout({
                                                     inputLabel,
                                                     inputControl,
                                                     inputContent,
                                                     inputBottom,

                                                     resultLabel,
                                                     resultControl,
                                                     resultContent,
                                                     resultBottom,

                                                     children,
                                                   }) {
  const {t} = useTranslation()

  const toolInfo = useToolInfo()

  return (
    <TwoPanelToolLayout
      leftPanelName={inputLabel ?? t('input-result-panel-tool-layout.input-label')}
      leftPanelTop={t(`${toolInfo.key}.input-description`)}
      leftPanelControl={inputControl}
      leftPanelContent={inputContent}
      leftPanelBottom={inputBottom}

      rightPanelName={resultLabel ?? t('input-result-panel-tool-layout.result-label')}
      rightPanelTop={t('input-result-panel-tool-layout.result-description')}
      rightPanelControl={resultControl}
      rightPanelContent={resultContent}
      rightPanelBottom={resultBottom}
    >
      {children}
    </TwoPanelToolLayout>
  )
}
