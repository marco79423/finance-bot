import React from 'react'
import {useTranslation} from 'next-i18next'

import {useNotifications} from '../../../../hooks/notifications'
import Button from '../../../elements/Button'
import {IconButton, Tooltip} from '@mui/material'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'


function CopyButton({iconMode, disabled, data, ...props}) {
  const {t} = useTranslation('base')

  const notifications = useNotifications()
  const copyToClipboard = React.useCallback(() => {
    navigator.clipboard.writeText(data)
      .then(() => notifications.showSuccessMessage(t('Copied Successfully')))
  }, [data, notifications, t])

  return (
    iconMode ? (
      <Tooltip title={t('Copy')}>
        {/* 加 span 是為了不讓 Tooltip 因為 disabled button 而跳警告 */}
        <span>
          <IconButton
            disabled={disabled}
            aria-label={t('Copy')}
            onClick={copyToClipboard}
            {...props}
          >
            <ContentCopyIcon/>
          </IconButton>
        </span>
      </Tooltip>
    ) : (
      <Button
        size="small"
        disabled={disabled}
        onClick={copyToClipboard}
        {...props}
      >{t('Copy')}</Button>
    )
  )
}

export default React.memo(CopyButton)
