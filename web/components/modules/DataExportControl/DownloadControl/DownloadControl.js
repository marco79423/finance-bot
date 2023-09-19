import React from 'react'
import {useTranslation} from 'next-i18next'
import {css} from '@emotion/react'
import {IconButton, Tooltip} from '@mui/material'
import DownloadIcon from '@mui/icons-material/Download'

import downloadFile from '../../../../utils/downloadFile'
import Button from '../../../elements/Button'
import TextField from '../../../elements/TextField'
import BasicDialog from '../../../elements/BasicDialog'


function DownloadControl({iconMode, disabled, data, fileExt = '.txt', buttonId, ...props}) {
  const styles = {
    content: css`
      min-width: 280px;
    `,
    description: css`
      margin-bottom: 8px;
    `,
    input: css`
      height: 48px;
    `,
    downloadButton: css`
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
    `,
  }

  const {t} = useTranslation('base')

  const [fileName, onFileNameChange] = React.useState(t('filename') + fileExt)
  const onDownloadButtonClick = React.useCallback(() => {
    if (typeof data === 'function') {
      downloadFile({fileName, data: data()})
    } else {
      downloadFile({fileName, data})
    }
  }, [fileName, data])

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
          <Tooltip title={t('Download')}>
            {/* 加 span 是為了不讓 Tooltip 因為 disabled button 而跳警告 */}
            <span>
              <IconButton
                disabled={disabled}
                aria-label={t('Download')}
                onClick={onOpenDialog}
                {...props}
              >
                <DownloadIcon/>
              </IconButton>
            </span>
          </Tooltip>
        ) : (
          <TextField
            value={fileName}
            onChange={onFileNameChange}
            ariaLabel={t('Filename')}
            action={
              <Button
                id={buttonId}
                size="small"
                css={styles.button}
                disabled={disabled}
                onClick={onDownloadButtonClick}
              >{t('Download')}</Button>
            }

            {...props}
          />
        )
      }

      <BasicDialog
        title={t('download-control.title')}
        open={dialogOpen}
        onClose={onCloseDialog}
        actions={
          <div css={styles.actions}>
            <Button
              id={buttonId}
              size="small"
              css={styles.downloadButton}
              disabled={disabled}
              onClick={onDownloadButtonClick}
            >{t('Download')}</Button>
          </div>
        }
      >
        <div css={styles.content}>
          <div css={styles.description}>{t('download-control.description')}</div>

          <TextField
            css={styles.input}
            value={fileName}
            onChange={onFileNameChange}
            ariaLabel={t('Filename')}
          />
        </div>
      </BasicDialog>
    </>
  )
}

export default React.memo(DownloadControl)
