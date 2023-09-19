import React from 'react'
import {useTranslation} from 'next-i18next'

import SettingsControl from '../../modules/SettingsControl'
import {useToolInfo} from '../../../contexts/toolInfo'


function ToolSettings({info, ...props}) {
  const {t} = useTranslation('base')
  const toolInfo = useToolInfo()

  const steps = React.useMemo(() => {
    return [
      {
        target: '#tool-title',
        disableBeacon: true,
        content: t('tour.tool-title'),
      },
      {
        target: '#tool-description',
        disableBeacon: true,
        content: t('tour.tool-description'),
      },
      {
        target: '#tool-content',
        disableBeacon: true,
        content: t('tour.tool-content'),
      },
      {
        target: '#nav',
        disableBeacon: true,
        placement: 'right-start',
        content: t('tour.nav'),
      },
    ]
  }, [t])

  return (
    <SettingsControl
      title={t('Tool Settings')}
      tourSteps={steps}
      {...props}
    />
  )
}

export default React.memo(ToolSettings)
