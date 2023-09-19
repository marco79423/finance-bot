import React from 'react'
import {useTranslation} from 'next-i18next'
import {css, useTheme} from '@emotion/react'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'

import {ProcessStatus} from '../../../constants'
import Processing from '../../elements/Processing'


export default function ProcessStatusInfo({id, processStatus, enableProgressing, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      height: 36px;
      width: 36px;
      line-height: 36px;

      display: flex;
      align-items: center;
      justify-content: center;
    `,
    success: css`
      color: ${theme.palette.success.main};
    `,

    failed: css`
      color: ${theme.palette.error.main};
    `,
  }

  const {t} = useTranslation('base')

  const Icon = () => {
    switch (processStatus) {
      case ProcessStatus.Success:
        return (
          <CheckCircleIcon id={id} css={styles.success} alt={t('Processing success')}/>
        )
      case ProcessStatus.Processing:
        return (
          enableProgressing ?
            <Processing id={id} css={styles.root} height={36} width={36} alt={t('Processing')}/> : null
        )
      case ProcessStatus.Failed:
        return (
          <ErrorIcon id={id} css={styles.failed} alt={t('Processing failed')}/>
        )
      default:
        return null
    }
  }

  return (
    <div css={styles.root} {...props}>
      <Icon/>
    </div>
  )
}

