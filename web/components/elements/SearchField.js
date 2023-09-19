import React from 'react'
import {css, useTheme} from '@emotion/react'
import {InputAdornment} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'

import TextField from './TextField'


function SearchField({query, onQueryChange, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      height: 40px;
      padding: 4px 8px;
    `,

    icon: css`
      color: ${theme.palette.onSurface.dark};
    `
  }

  return (
    <TextField
      css={styles.root}

      type="search"
      value={query}
      onChange={onQueryChange}

      startAdornment={(
        <InputAdornment position="start">
          <SearchIcon css={styles.icon}/>
        </InputAdornment>
      )}

      {...props}
    />
  )
}

export default React.memo(SearchField)
