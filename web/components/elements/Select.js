import React from 'react'
import PropTypes from 'prop-types'
import {css, useTheme} from '@emotion/react'
import {FormControl, MenuItem, Select as MuiSelect} from '@mui/material'


function Select({currentValue, selections, onSelectionChange, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      background: ${theme.palette.surface.light};
      color: ${theme.palette.onSurface.dark};
    `
  }

  const onChange = (event) => {
    onSelectionChange(event.target.value)
  }

  return (
    <FormControl size="small">
      <MuiSelect
        css={styles.root}
        value={currentValue}
        onChange={onChange}
        {...props}
      >
        {selections.map(selection => (
          <MenuItem
            key={selection.key}
            disabled={selection.disabled}
            value={selection.value}>{selection.label}</MenuItem>
        ))}
      </MuiSelect>
    </FormControl>
  )
}

Select.propTypes = {
  currentValue: PropTypes.any.isRequired,
  selections: PropTypes.arrayOf(PropTypes.shape({
    key: PropTypes.any.isRequired,
    label: PropTypes.string.isRequired,
    value: PropTypes.any.isRequired,
    disabled: PropTypes.bool,
  })).isRequired,
  onSelectionChange: PropTypes.func.isRequired,
}

export default React.memo(Select)
