import React from 'react'
import Joyride, {STATUS} from 'react-joyride'
import {useTheme} from '@emotion/react'
import {useTranslation} from 'next-i18next'


export default function Tour({steps, running, onChange}) {
  const {t} = useTranslation('base')
  const theme = useTheme()

  const handleTourCallback = ({status}) => {
    if (status === STATUS.FINISHED || status === STATUS.SKIPPED) {
      onChange(false)
    }
  }

  return (
    <Joyride
      styles={{
        options: {
          arrowColor: theme.palette.primary.lightest,
          backgroundColor: theme.palette.primary.lightest,
          primaryColor: theme.palette.primary.main,
          width: 400,
        }
      }}
      run={running}
      disableScrollParentFix={true} // 修正會亂加 overflow: initial 的問題
      showProgress={true}
      showSkipButton={true}
      continuous={true}
      hideCloseButton={true}
      callback={handleTourCallback}
      steps={steps}
      locale={{
        back: t('tour.back'),
        close: t('tour.close'),
        last: t('tour.last'),
        next: t('tour.next'),
        open: t('tour.open'),
        skip: t('tour.skip'),
      }}
    />
  )
}
