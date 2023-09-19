import React from 'react'
import {css, Global, useTheme} from '@emotion/react'
import {useTranslation} from 'next-i18next'
import Scrollbars from 'react-custom-scrollbars-2'

import Title from '../../modules/Title'


export default function BaseLayout({navbar, children, ...props}) {
  const theme = useTheme()
  const styles = {
    global: css`
      body {
        background: ${theme.palette.primary.lightest}; // 讓手機下拉時背景不是白色
      }
    `,

    root: css`
      position: absolute;
      height: 100%;
      width: 100%;

      display: flex;
      flex-direction: column;
    `,
    header: css`
      display: none;

      @media (max-width: ${theme.breakpoints.lg}px) {
        width: 100%;
        height: 64px;

        display: flex;
        justify-content: space-between;
        align-items: center;

        background: ${theme.palette.primary.dark};
        padding-left: 16px;
        padding-right: 16px;
      }
    `,
    main: css`
      flex: 1;
      position: relative;
      display: flex;
      overflow: hidden;
    `,
    nav: css`
      @media (max-width: ${theme.breakpoints.lg}px) {
        display: none;
      }
    `,

    content: css`
      flex: 1;
      position: relative;
    `,
  }

  const {t} = useTranslation('base')

  return (
    <>
      <Global
        styles={styles.global}
      />

      <div css={styles.root} {...props}>
        <header css={styles.header} data-nosnippet={true}>
          <Title title={t('site-name')}/>
        </header>
        <div css={styles.main}>
          <div css={styles.nav} data-nosnippet={true}>
            {navbar}
          </div>
          <Scrollbars css={styles.content} universal autoHide>
            {children}
          </Scrollbars>
        </div>
      </div>
    </>
  )
}
