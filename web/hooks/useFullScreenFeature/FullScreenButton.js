import React from 'react'
import {useTranslation} from 'next-i18next'
import {IconButton, Tooltip} from '@mui/material'
import FullscreenIcon from '@mui/icons-material/Fullscreen'


function FullScreenButton({disabled, onClick, ...props}) {
  const {t} = useTranslation('base')

  return (
    <Tooltip title={t('Fullscreen')}>
      {/* 加 span 是為了不讓 Tooltip 因為 disabled button 而跳警告 */}
      <span>
        <IconButton
          disableRipple
          edge="end"
          disabled={disabled}
          aria-label={t('Fullscreen')}
          size="large"
          onClick={onClick}
          {...props}
        >
          <FullscreenIcon/>
        </IconButton>
      </span>
    </Tooltip>
  )
}

export default React.memo(FullScreenButton)
