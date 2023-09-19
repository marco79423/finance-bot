import React from 'react'
import Link from 'next/link'
import {css, useTheme} from '@emotion/react'
import {List, ListItemButton} from '@mui/material'

import {useDeveloperMode} from '../../contexts/developerMode'
import useLeaveSiteDetect from '../../hooks/useLeaveSiteDetect'


function ToolList({tools}) {
  const theme = useTheme()
  const styles = {
    root: css`
      b {
        color: ${theme.palette.secondary.main};
      }
    `,

    item: css`
      padding: 16px;
    `,

    privateTag: css`
      margin-left: 4px;
      color: ${theme.palette.secondary.dark};
      font-size: 12px;
    `
  }
  const developMode = useDeveloperMode()

  const [handleLink, LeaveSiteDialog] = useLeaveSiteDetect()
  return (
    <>
      <List css={styles.root}>
        {tools.map(tool => (
          <li key={tool.label}>
            <Link href={tool.url} prefetch={false} passHref legacyBehavior>
              <ListItemButton css={styles.item} selected={tool.active} component="a" onClick={e => handleLink(e, tool.url)}>
                <span dangerouslySetInnerHTML={{__html: tool.label}}/>
                {developMode && tool.isPrivate ? (
                  <span css={styles.privateTag}>[P]</span>
                ) : null}
              </ListItemButton>
            </Link>
          </li>
        ))}
      </List>

      <LeaveSiteDialog/>
    </>
  )
}

export default React.memo(ToolList)
