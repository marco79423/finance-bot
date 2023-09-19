import React from 'react'
import PropTypes from 'prop-types'
import {useTranslation} from 'next-i18next'
import {css} from '@emotion/react'
import {useRouter} from 'next/router'

import {HostUrl} from '../../../config/vars.config'
import {useNotifications} from '../../../hooks/notifications'
import Checkbox from '../../elements/Checkbox'
import TextField from '../../elements/TextField'
import Button from '../../elements/Button'
import BasicDialog from '../../elements/BasicDialog'


export default function ShareDialog({open, onClose}) {
  const styles = {
    content: css`
      padding: 16px;
    `,

    input: css`
      height: 48px;
      min-width: 480px;
    `,
    control: css`
      margin-top: 8px;
    `,
    button: css`
      &:not(:first-of-type) {
        margin-left: 8px
      }
    `
  }
  const {t} = useTranslation('base')

  const router = useRouter()

  const [queryIncluded, setQueryIncluded] = React.useState(true)
  const shareLink = React.useMemo(() => {
    if (queryIncluded) {
      return HostUrl + router.asPath
    } else {
      return HostUrl + router.pathname
    }
  }, [router.pathname, router.asPath, queryIncluded])

  const notifications = useNotifications()
  const onCopyLinkButtonClick = async () => {
    await navigator.clipboard.writeText(shareLink)
    await notifications.showSuccessMessage(t('Copied Successfully'))
  }

  const onCloseButtonClick = () => {
    onClose()
  }

  return (
    <BasicDialog
      title={t('Share link')}
      open={open}
      onClose={onCloseButtonClick}
      actions={
        <div css={styles.actions}>
          <Button
            id="copy-button"
            css={styles.button}
            onClick={onCopyLinkButtonClick}>{t('Copy')}</Button>
        </div>
      }
    >
      <div css={styles.content}>
        <TextField
          css={styles.input}
          readOnly
          value={shareLink}
          ariaLabel={t('Share link')}
        />
        <div css={styles.control}>
          <Checkbox
            checked={queryIncluded}
            onChange={setQueryIncluded}
            label={t('Including your input.')}
          />
        </div>
      </div>
    </BasicDialog>
  )
}

ShareDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
}
