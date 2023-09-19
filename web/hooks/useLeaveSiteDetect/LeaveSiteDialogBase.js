import React from 'react'
import Image from 'next/image'
import {css, useTheme} from '@emotion/react'

import Button from '../../components/elements/Button'
import BasicDialog from '../../components/elements/BasicDialog'
import {useTranslation} from 'next-i18next'
import {useRouter} from 'next/router'


function LeaveSiteDialogBase({open, onClose, targetLink}) {
  const theme = useTheme()
  const styles = {
    content: css`
      min-width: 500px;
      padding: 16px;
      display: flex;
      gap: 24px;

      @media (max-width: ${theme.breakpoints.sm}px) {
        min-width: 280px;
        flex-direction: column;
        align-items: center;
      }
    `,

    description: css`
      font-size: 1.8rem;
      font-weight: 600;

      @media (max-width: ${theme.breakpoints.sm}px) {
        font-size: 1.5rem;
      }
    `,

    siteName: css`
      color: ${theme.palette.primary.main};
      font-size: 1.6rem;
      font-weight: 600;

      @media (max-width: ${theme.breakpoints.sm}px) {
        font-size: 1.5rem;
      }
    `,

    detail: css`
      margin-top: 16px;
    `,
    followLink: css`
      color: ${theme.palette.primary.main};
      font-size: 1.2rem;
      font-weight: 600;
    `,
  }

  const {t} = useTranslation('base')

  const router = useRouter()
  const followLink = async () => {
    await router.push(targetLink)
  }

  const showLink = React.useMemo(() => {
    if (targetLink) {
      const pathEnd = Math.min(
        targetLink.indexOf('?') > 0 ? targetLink.indexOf('?') : targetLinkh.length,
        targetLink.indexOf('#') > 0 ? targetLink.indexOf('#') : targetLink.length
      )
      return targetLink.substring(0, pathEnd)
    }
    return ''
  }, [targetLink])


  return (
    <BasicDialog
      title={t('leave-site-dialog.title')}
      open={open}
      onClose={onClose}
      actions={
        <div css={css`
          display: inline-flex;
          gap: 8px;
        `}>
          <Button secondary onClick={onClose}>{t('leave-site-dialog.cancel')}</Button>
          <Button onClick={followLink}>{t('leave-site-dialog.leave')}</Button>
        </div>
      }
    >
      <div css={styles.content}>
        <Image width={192} height={192} src="/logo-192x192.png"/>
        <div>
          <div css={styles.description}>{t('leave-site-dialog.description')}</div>
          <div css={styles.siteName}>{t('site-name')}</div>
          <div css={styles.detail}>{t('leave-site-dialog.detail')}</div>
          <div css={styles.followLink}>{showLink}</div>
        </div>
        <div css={css`flex: 1;`}/>
      </div>
    </BasicDialog>
  )
}

export default React.memo(LeaveSiteDialogBase)
