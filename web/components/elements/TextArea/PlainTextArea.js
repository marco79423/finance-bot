import React from 'react'
import PropTypes from 'prop-types'
import lodash from 'lodash'
import {css, useTheme} from '@emotion/react'
import {FormControl, OutlinedInput} from '@mui/material'

import {hideScrollbar} from '../../../utils/css-helpers'


function Input(props) {
  // 消除警告，因為 textarea 不支援 inputRef
  props = lodash.omit(props, ['inputRef'])
  return (
    <textarea {...props} />
  )
}

export default function PlainTextArea({id, placeholder, autoFocus, value, onChange, ariaLabel, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      height: 100%;
      margin-top: 0;

      background: ${theme.palette.surface.light};
    
    `,

    input: css`
      height: 100%;
      align-items: start; // 將輸入框放至頂部
      color: ${theme.palette.onSurface.dark};

      & .MuiOutlinedInput-input {
        height: calc(100% - 48px); // 不要佔滿全部的輸入空間
        min-height: 150px;
        resize: none; // 不需要自動調整大小的 grabber
        overflow: auto; // 自動產生 scrollbar
        ${hideScrollbar}
      }
    `,
  }

  const onValueChange = (e) => {
    onChange(e.target.value)
  }

  return (
    <FormControl css={styles.root} variant="outlined" margin="normal" fullWidth {...props}>
      <OutlinedInput
        id={id}
        css={styles.input}
        placeholder={placeholder}
        autoFocus={autoFocus}
        value={value}
        onChange={onValueChange}
        inputComponent={Input}
        inputProps={{
          'aria-label': ariaLabel,
        }}
      />
    </FormControl>
  )
}

PlainTextArea.propTypes = {
  label: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func,
}
