import React from 'react'
import Link from 'next/link'
import {css} from '@emotion/react'
import {Chip} from '@mui/material'

function RelatedTools({tools = [], ...props}) {
  const styles = {
    root: css`
      display: flex;
      align-items: flex-end;
      gap: 8px;
    `,
  }

  return (
    <div css={styles.root} {...props}>
      {
        tools.slice(0, 3).map(tool => (
          <Link key={tool.key} href={tool.url} legacyBehavior>
            <Chip label={tool.label} variant="outlined" component="a" clickable/>
          </Link>
        ))
      }
    </div>
  )
}

export default React.memo(RelatedTools)
