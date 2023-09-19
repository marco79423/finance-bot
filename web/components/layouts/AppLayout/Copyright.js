import React from 'react'
import {useTranslation} from 'next-i18next'
import {css, useTheme} from '@emotion/react'
import {Link} from '@mui/material'


function Copyright({...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      width: fit-content;
      color: ${theme.palette.primary.lightest};

      @media (max-width: ${theme.breakpoints.sm}px) {
        display: none;
      }
    `
  }

  const {t} = useTranslation('base')

  return (
    <div css={styles.root} {...props}>
      {`Copyright © ${new Date().getFullYear()} - `}
      <Link color="inherit" href="https://paji-toolset.net/">{t('site-name')}</Link>
    </div>
  )
}

export default React.memo(Copyright)
