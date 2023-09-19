import React from 'react'
import {css, useTheme} from '@emotion/react'
import {useTranslation} from 'next-i18next'
import {FullScreen, useFullScreenHandle} from 'react-full-screen'
import {IconButton, Tooltip} from '@mui/material'
import FullscreenIcon from '@mui/icons-material/Fullscreen'

import {useAppCtx} from '../../../contexts/appCtx'
import Paper from '../../elements/Paper'
import ImageArea from '../ImageArea'


export default function ImageEditor({id, dataURL, loading, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      height: 100%;

      padding: 8px 16px 16px;
      background: ${theme.palette.surface.main};
      color: ${theme.palette.onSurface.dark};

      display: flex;
      flex-direction: column;
    `,

    control: css`
      margin-bottom: 8px;
      display: flex;
    `,

    fullScreen: css`
      height: 100%;
      background: ${theme.palette.surface.light};
    `,

    content: css`
      position: relative;
      flex: 1;
    `,
  }
  const {t} = useTranslation()

  const appCtx = useAppCtx()

  const fullScreenHandle = useFullScreenHandle()

  return (
    <Paper css={styles.root}>
      <div css={styles.control}>
        {!appCtx.isMobile && (
          <Tooltip title={t('text-editor.fullscreen')}>
            {/* 加 span 是為了不讓 Tooltip 因為 disabled button 而跳警告 */}
            <span>
              <IconButton
                disableRipple
                size="small"
                onClick={fullScreenHandle.enter}
                aria-label={t('text-editor.fullscreen')}
                {...props}
              >
                <FullscreenIcon/>
              </IconButton>
            </span>
          </Tooltip>
        )}
      </div>
      <Paper variant="outlined" css={styles.content}>
        <FullScreen css={styles.fullScreen} handle={fullScreenHandle}>
          <ImageArea
            id={id}
            loading={loading}
            source={dataURL}
          />
        </FullScreen>
      </Paper>
    </Paper>
  )
}
