import React from 'react'
import {useTranslation} from 'next-i18next'
import Scrollbars from 'react-custom-scrollbars-2'
import {css, useTheme} from '@emotion/react'

import Title from '../Title'
import Copyright from '../../layouts/AppLayout/Copyright'


function NavbarContainer({subHeader, children, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      height: 100%;
      display: flex;
      flex-direction: column;
      background: ${theme.palette.primary.light};
      width: 360px;
    `,

    header: css`
      background: ${theme.palette.primary.dark};
      padding: 8px 16px;
    `,

    title: css`
      margin: 0 auto;
    `,

    content: css`
      padding: 16px;
    `,

    copyright: css`
      margin: 0 auto 8px;
    `,
  }

  const {t} = useTranslation('base')

  return (
    <nav id="nav" css={styles.root} {...props}>
      <div css={styles.header}>
        <Title css={styles.title} title={t('site-name')}/>
        {subHeader}
      </div>
      <Scrollbars universal autoHide>
        <div css={styles.content}>
          {children}
        </div>
        <div css={styles.footer}>
          <Copyright css={styles.copyright}/>
        </div>
      </Scrollbars>
    </nav>
  )
}


export default React.memo(NavbarContainer)
