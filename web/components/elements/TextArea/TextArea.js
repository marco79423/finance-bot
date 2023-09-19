import React from 'react'
import {css} from '@emotion/react'
import {CircularProgress} from '@mui/material'

import PlainTextArea from './PlainTextArea'
import CodeTextArea from './CodeTextArea'

export default function TextArea({mode, loading, ...props}) {
  const styles = {
    root: css`
      position: relative;
      width: 100%;
      height: 100%;
    `,

    loadingCover: css`
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    `
  }

  return (
    <div css={styles.root}>
      {mode !== 'text' ? (
        <CodeTextArea
          disabled={loading}
          editable={!loading}
          dataFormat={mode}
          {...props}
        />
      ) : (
        <PlainTextArea
          disabled={loading}
          editable={!loading}
          {...props}
        />
      )}

      {loading && (
        <div css={styles.loadingCover}>
          <CircularProgress/>
        </div>
      )}
    </div>
  )
}

