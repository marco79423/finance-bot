import React from 'react'
import {css, useTheme} from '@emotion/react'

import BaseLayout from '../BaseLayout'
import RelatedTools from './RelatedTools'


export default function AppLayout({
                                    namePrefix = '',
                                    title,
                                    description,
                                    relatedTools,
                                    navbar,
                                    settings,
                                    children,
                                    ...props
                                  }) {
  const theme = useTheme()
  const styles = {
    root: css`
      display: flex;
      flex-direction: column;
      padding: 32px 32px 16px;
      background: ${theme.palette.primary.lightest};
      color: ${theme.palette.onSurface.dark};

      width: 100%;
      height: 100%;

      @media (max-width: ${theme.breakpoints.sm}px) {
        padding: 16px;
      }
    `,
    header: css`
      display: flex;
      justify-content: space-between;
      align-items: center;

      margin-bottom: 8px;
    `,
    title: css`
      color: ${theme.palette.onPrimary.dark};
      font-size: 2.0em;
      font-weight: 700;
    `,
    relatedTools: css`
      @media (max-width: ${theme.breakpoints.md}px) {
        display: none;
      }
    `,
    description: css`
      margin-bottom: 16px;
      font-size: 1.2rem;
    `,
    content: css`
      flex: 1;
      position: relative;
    `,
  }

  return (
    <BaseLayout
      navbar={navbar}
      {...props}
    >
      <main id={`${namePrefix}-container`} css={styles.root} {...props}>
        <header id="header">
          <div css={styles.header}>
            <div css={css`
              display: flex;
              align-items: flex-end;
              gap: 16px;
            `}>
              <div id="title" css={styles.title}>{title}</div>

              {/* 相關工具不需要爬蟲抓取 */}
              {relatedTools && <RelatedTools css={styles.relatedTools} tools={relatedTools} data-nosnippet={true}/>}
            </div>

            {/* 設定不需要爬蟲抓取 */}
            <div css={styles.settings} data-nosnippet={true}>{settings}</div>
          </div>
          <div id={`${namePrefix}-description`} css={styles.description}>{description}</div>
        </header>
        {/* 內容不需要爬蟲抓取 */}
        <div id={`${namePrefix}-content`} css={styles.content} data-nosnippet={true}>
          {children}
        </div>
      </main>
    </BaseLayout>
  )
}
