import React from 'react'
import {css} from '@emotion/react'

import CopyButton from './CopyButton'
import DownloadControl from './DownloadControl'
import ShareButton from './ShareButton'


export default function DataExportControl({
                                            iconMode,
                                            disabled,
                                            data,

                                            copyEnabled=true,
                                            downloadEnabled=true,

                                            downloadButtonId,
                                            downloadFileExt = '.txt',

                                            shareEnabled=false,
                                          }) {
  const styles = {
    root: css`
      display: flex;
      align-items: center;
      gap: 8px;
    `,
  }

  return (
    <div css={styles.root}>
      {copyEnabled && <CopyButton
        iconMode={iconMode}
        disabled={disabled}
        data={data}
      />}
      {downloadEnabled && <DownloadControl
        iconMode={iconMode}
        buttonId={downloadButtonId}
        fileExt={downloadFileExt}
        disabled={disabled}
        data={data}
      />}
      {shareEnabled && <ShareButton
        iconMode={iconMode}
        disabled={disabled}
      />}
    </div>
  )
}
