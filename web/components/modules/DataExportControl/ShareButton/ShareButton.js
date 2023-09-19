import React from 'react'
import {useTranslation} from 'next-i18next'

import Button from '../../../elements/Button'
import ShareDialog from './ShareDialog'
import {IconButton, Tooltip} from '@mui/material'
import ShareIcon from '@mui/icons-material/Share'


function ShareButton({iconMode, disabled, ...props}) {
  const {t} = useTranslation('base')

  const [dialogOpen, setDialogOpen] = React.useState(false)
  const onOpenDialog = React.useCallback(() => {
    setDialogOpen(true)
  }, [])

  const onCloseDialog = React.useCallback(() => {
    setDialogOpen(false)
  }, [])

  return (
    <>
      {
        iconMode ? (
          <Tooltip title={t('Share')}>
            {/* 加 span 是為了不讓 Tooltip 因為 disabled button 而跳警告 */}
            <span>
              <IconButton
                disabled={disabled}
                aria-label={t('Share')}
                onClick={onOpenDialog}
                {...props}
              >
                <ShareIcon/>
              </IconButton>
            </span>
          </Tooltip>
        ) : (
          <Button
            size="small"
            disabled={disabled}
            onClick={onOpenDialog}
            {...props}
          >{t('Share')}</Button>
        )
      }

      <ShareDialog
        open={dialogOpen}
        onClose={onCloseDialog}
      />
    </>
  )
}

export default React.memo(ShareButton)
