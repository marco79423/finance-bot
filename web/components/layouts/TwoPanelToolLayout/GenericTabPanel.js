import React from 'react'
import {css, useTheme} from '@emotion/react'

import Paper from '../../elements/Paper'


export default function GenericTabPanel({tabKey, tabLabel, top, control, content, bottom, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      max-width: 700px;
      width: inherit;
      padding: 24px;
      height: 100%;
      background: ${theme.palette.surface.light};
      color: ${theme.palette.onSurface.dark};

      display: flex;
      flex-direction: column;

      border-top-left-radius: 0;

      @media (max-width: ${theme.breakpoints.sm}px) {
        padding: 16px;
      }
    `,
    top: css`
      min-height: 40px;
    `,
    control: css`
      min-height: 48px;
    `,
    content: css`
      position: relative;
      flex: 1;
    `,
    bottom: css`
      min-height: 48px;
      display: flex;
      align-items: center;
    `,
  }

  return (
    <Paper css={styles.root} {...props}>
      {top && <div css={styles.top}>
        {top}
      </div>}
      {control && <div css={styles.control}>
        {control}
      </div>}
      {content && <div css={styles.content}>
        {content}
      </div>}
      {bottom && <div css={styles.bottom}>
        {bottom}
      </div>}
    </Paper>
  )
}
