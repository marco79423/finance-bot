import React from 'react'
import PropTypes from 'prop-types'
import {css, useTheme} from '@emotion/react'
import {Dialog, IconButton, useMediaQuery} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import {useTranslation} from 'next-i18next'


export default function BasicDialog({children, autoFullScreen, title, open, onClose, actions, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      .MuiDialog-paper {
        background: ${theme.palette.primary.lightest};
        border-radius: 8px;
        
        display: flex;
        flex-direction: column;
      }
    `,
    header: css`
      display: flex;
      justify-content: space-between;
      align-items: center;

      padding: 8px 8px 8px 16px;

      color: ${theme.palette.onPrimary.main};
      background: ${theme.palette.primary.dark};
      font-size: 1.2em;
      font-weight: 600;

      button {
        color: inherit;
      }
    `,
    content: css`
      flex: 1;
      padding: 16px;
      position: relative;
    `,
    actions: css`
      text-align: right;
      padding: 0 16px 16px;
    `,
  }
  const {t} = useTranslation('base')
  const fullScreen = useMediaQuery(theme.breakpoints.down('sm'))

  return (
    <Dialog
      css={styles.root}
      fullScreen={autoFullScreen && fullScreen}
      maxWidth="md"
      open={open}
      onClose={onClose}
      {...props}
    >
      {/*Header*/}
      <div css={styles.header}>
        {title}
        <IconButton aria-label={t('Close')} onClick={onClose}>
          <CloseIcon/>
        </IconButton>
      </div>

      {/*Content*/}
      <div css={styles.content}>
        {children}
      </div>

      {/*Actions*/}
      {actions && <div css={styles.actions}>
        {actions}
      </div>}
    </Dialog>
  )
}

BasicDialog.propTypes = {
  children: PropTypes.node.isRequired,
  autoFullScreen: PropTypes.bool,
  title: PropTypes.string.isRequired,
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  actions: PropTypes.node,
}
