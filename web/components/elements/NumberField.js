import React from 'react'
import PropTypes from 'prop-types'
import {TextField} from '@mui/material'
import {css, useTheme} from '@emotion/react'


export default function NumberField({value, onChange, disabled, error, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      .MuiInputBase-input {
        background: ${theme.palette.surface.light};
      }
    `,
  }

  const onValueChange = (e) => {
    onChange(+e.target.value)
  }

  return (
    <TextField
      css={styles.root}
      inputProps={{min: 0, style: {textAlign: 'center'}}}
      type="number"
      size="small"
      disabled={disabled}
      error={error}
      onChange={onValueChange}
      value={value}
      {...props}
    />
  )
}

NumberField.propTypes = {
  className: PropTypes.string,
  value: PropTypes.number,
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
  error: PropTypes.bool,
}
