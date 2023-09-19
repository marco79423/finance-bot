import React from 'react'
import PropTypes from 'prop-types'
import {css, useTheme} from '@emotion/react'
import {Checkbox as MuiCheckbox, Typography} from '@mui/material'


function Checkbox({checked, onChange, label}) {
  const theme = useTheme()
  const styles = {
    root: css`
      display: flex;
      align-items: center;
    `,

    checkbox: css`
      color: ${theme.palette.primary.dark}
      
      &.Mui-checked {
        color: ${theme.palette.primary.dark}
      }
    },  `
  }

  const wrappedOnChange = (e) => {
    onChange(e.target.checked)
  }

  return (
    <div css={styles.root}>
      <MuiCheckbox
        css={styles.checkbox}
        checked={checked}
        onChange={wrappedOnChange}

        inputProps={{
          'aria-label': label,
        }}
      />
      <Typography>{label}</Typography>
    </div>
  )
}

Checkbox.propTypes = {
  checked: PropTypes.bool.isRequired,
  onChange: PropTypes.func.isRequired,
  label: PropTypes.string.isRequired,
}

export default React.memo(Checkbox)
