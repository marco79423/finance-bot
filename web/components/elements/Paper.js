import {Paper as MuiPaper} from '@mui/material'
import {css, useTheme} from '@emotion/react'

export default function Paper({children, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      background: ${theme.palette.surface.light};
    `
  }

  return (
    <MuiPaper css={styles.root} {...props}>
      {children}
    </MuiPaper>
  )
}
