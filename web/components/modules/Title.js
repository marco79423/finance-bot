import React from 'react'
import {css, useTheme} from '@emotion/react'
import Link from 'next/link'

import {useDeveloperMode} from '../../contexts/developerMode'


function Title({title, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      text-decoration: none;
      width: fit-content;

      display: flex;
      align-items: center;
    `,
    title: css`
      margin: 0;
      font-size: 2rem;
      font-weight: 800;
      color: ${theme.palette.onPrimary.main};

      @media (max-width: ${theme.breakpoints.sm}px) {
        font-size: 1.5rem;
      }
    `,

    mode: css`
      margin-left: 4px;
      color: ${theme.palette.secondary.dark};
      font-size: 1rem;
    `
  }

  const developMode = useDeveloperMode()

  return (
    <Link css={styles.root} href="/" {...props}>
      <div css={styles.title}>
        {title}
        {developMode ? (
          <span css={styles.mode}>[dev]</span>
        ) : null}
      </div>
    </Link>
  )
}

export default React.memo(Title)
