import React from 'react'
import {css, useTheme} from '@emotion/react'
import {useTranslation} from 'next-i18next'
import {FullScreen, useFullScreenHandle} from 'react-full-screen'
import {Divider, IconButton, Tooltip} from '@mui/material'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import ContentCutIcon from '@mui/icons-material/ContentCut'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import ContentPasteIcon from '@mui/icons-material/ContentPaste'
import FullscreenIcon from '@mui/icons-material/Fullscreen'
import UploadFileIcon from '@mui/icons-material/UploadFile'

import {useAppCtx} from '../../../contexts/appCtx'
import {useNotifications} from '../../../hooks/notifications'
import readTextFromFile from '../../../utils/readTextFromFile'
import Paper from '../../elements/Paper'
import TextArea from '../../elements/TextArea'
import Button from '../../elements/Button'
import BasicDialog from '../../elements/BasicDialog'
import FileDropzone from '../FileDropzone'

const emptyFunc = () => {
}


export default function TextEditor({
                                     id,
                                     lang,
                                     value,
                                     onChange = emptyFunc,
                                     loading,
                                     readOnly,
                                     status,
                                     extraControl,
                                     ...props
                                   }) {
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

    extraControl: css`
      margin-top: 8px;
    `,
  }
  const {t} = useTranslation()

  const appCtx = useAppCtx()

  const notifications = useNotifications()

  const [fileUploadDialogOpen, setFileUploadDialogOpen] = React.useState(false)
  const onFileUploadDialogOpen = () => {
    setFileUploadDialogOpen(true)
  }

  const onFileUploadDialogClose = () => {
    setFileUploadDialogOpen(false)
  }

  const [fileInput, setFileInput] = React.useState(null)
  const onInputFileChange = React.useCallback(files => {
    if (files.length === 1) {
      setFileInput(files[0])
    } else {
      setFileInput(null)
    }
  }, [])

  const parseFileData = React.useCallback(() => {
    if (!fileInput) {
      return
    }

    readTextFromFile(fileInput)
      .then(text => onChange(text))
      .then(onFileUploadDialogClose)
  }, [fileInput, onChange])

  const copy = React.useCallback(() => {
    navigator.clipboard.writeText(value)
      .then(() => notifications.showSuccessMessage(t('text-editor.copy-success')))
  }, [value, notifications, t])

  const paste = React.useCallback(() => {
    navigator.clipboard.readText()
      .then(value => onChange(value))
  }, [onChange, notifications, t])

  const cut = React.useCallback(() => {
    navigator.clipboard.writeText(value)
      .then(() => notifications.showSuccessMessage(t('text-editor.cut-success')))
      .then(() => onChange(''))
  }, [value, onChange, notifications, t])

  const clear = React.useCallback(() => {
    onChange('')
  }, [onChange, notifications, t])

  const fullScreenHandle = useFullScreenHandle()

  return (
    <>
      <Paper css={styles.root}>
        <div css={styles.control}>
          {!readOnly && (
            <>
              <ControlButton
                icon={<UploadFileIcon/>}
                label={t('text-editor.upload')}
                onClick={onFileUploadDialogOpen}
              />
              <Divider orientation="vertical" flexItem/>
            </>
          )}

          <ControlButton
            icon={<ContentCopyIcon/>}
            label={t('text-editor.copy')}
            onClick={copy}
          />

          {!readOnly && (
            <ControlButton
              icon={<ContentCutIcon/>}
              label={t('text-editor.cut')}
              onClick={cut}
              disabled={!value}
            />
          )}

          {!readOnly && (
            <ControlButton
              icon={<ContentPasteIcon/>}
              label={t('text-editor.paste')}
              onClick={paste}
            />
          )}
          {!readOnly && (
            <ControlButton
              icon={<DeleteOutlineIcon/>}
              label={t('text-editor.clear')}
              onClick={clear}
              disabled={!value}
            />
          )}
          {!appCtx.isMobile && (
            <>
              <Divider orientation="vertical" flexItem/>

              <ControlButton
                icon={<FullscreenIcon/>}
                label={t('text-editor.fullscreen')}
                onClick={fullScreenHandle.enter}
              />
            </>
          )}
          <div css={css`flex: 1;`}/>
          {status}
        </div>
        <div css={styles.content}>
          <FullScreen css={styles.fullScreen} handle={fullScreenHandle}>
            <TextArea
              id={id}
              css={styles.textArea}
              value={value}
              onChange={onChange}
              placeholder={t('text-editor.placeholder')}
              readOnly={readOnly}
              loading={loading}
              mode={lang}
              options={{
                lineNumbers: true, foldGutter: true,
              }}

              ariaLabel={t('text-editor.aria-label')}

              {...props}
            />
          </FullScreen>
        </div>
        {extraControl && (
          <div css={styles.extraControl}>
            {extraControl}
          </div>
        )}
      </Paper>

      <BasicDialog
        title={t('text-editor.file-upload-dialog.title')}
        open={fileUploadDialogOpen}
        onClose={onFileUploadDialogClose}
        actions={<div css={css`
          display: inline-flex;
          gap: 8px;
        `}>
          <Button secondary onClick={onFileUploadDialogClose}>{t('text-editor.file-upload-dialog.cancel')}</Button>
          <Button disabled={!fileInput} onClick={parseFileData}>{t('text-editor.file-upload-dialog.confirm')}</Button>
        </div>}
      >
        <div>
          <div css={css`
            padding: 16px;
            font-size: 1.2rem;
          `}>
            <div>{t('text-editor.file-upload-dialog.description')}</div>
          </div>
          <FileDropzone
            acceptedFiles={['*']}
            filesLimit={1}
            onChange={onInputFileChange}
          />
        </div>
      </BasicDialog>
    </>
  )
}


function ControlButton({icon, label, onClick, ...props}) {
  return (
    <Tooltip title={label}>
      {/* 加 span 是為了不讓 Tooltip 因為 disabled button 而跳警告 */}
      <span>
        <IconButton
          disableRipple
          size="small"
          onClick={onClick}
          aria-label={label}
          {...props}
        >
          {icon}
        </IconButton>
      </span>
    </Tooltip>
  )
}