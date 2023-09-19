import React from 'react'
import {css, useTheme} from '@emotion/react'

import Paper from '../../elements/Paper'


export default function GenericPanel({top, control, content, bottom, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      padding: 24px;
      height: 100%;
      background: ${theme.palette.surface.light};
      color: ${theme.palette.onSurface.dark};

      display: flex;
      flex-direction: column;

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
      padding-top: 8px;
      min-height: 48px;
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
