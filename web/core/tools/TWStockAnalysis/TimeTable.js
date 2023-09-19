import React from 'react'
import {css} from '@emotion/react'
import {Table, TableBody, TableCell, TableRow} from '@mui/material'

import Paper from '../../../components/elements/Paper'
import CopyButton from '../../../components/modules/DataExportControl/CopyButton'


function TimeTable({rows}) {
  const styles = {
    root: css`
      padding: 16px;
    `,

    cell: css`
      padding: 4px;
    `,

    highlight: css`
      font-size: 1.1rem;
      font-weight: 600;
    `,

    copy: css`
      margin-left: 4px;
    `
  }

  return (
    <Paper css={styles.root}>
      <Table size="small">
        <TableBody>
          {rows.map((row, idx) => (
            <TableRow key={row.label}>
              <TableCell css={[styles.cell, idx === 0 && styles.highlight]}>{row.label}</TableCell>
              <TableCell css={[styles.cell, idx === 0 && styles.highlight]}>{row.value}<CopyButton css={styles.copy} iconMode data={row.value}/></TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Paper>
  )
}

export default React.memo(TimeTable)
