import React from 'react'
import {css} from '@emotion/react'
import {Divider} from '@mui/material'

import Paper from '../../../components/elements/Paper'
import ToolList from '../../../components/modules/ToolList'


function ToolPanel({title, list}) {
  const styles = {
    root: css`
      min-width: 200px;
      padding: 16px;
    `,

    title: css`
      margin: 0.5rem;
      font-size: 1.2rem;
      font-weight: 600;
    `,
  }

  return (
    <Paper css={styles.root} component="section">
      {title ? (
        <>
          <header css={styles.title}>{title}</header>
          <Divider/>
        </>
      ) : null}
      <ToolList tools={list}/>
    </Paper>
  )
}

export default React.memo(ToolPanel)
