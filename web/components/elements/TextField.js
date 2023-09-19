import React from 'react'
import {Grid, InputBase, Paper} from '@mui/material'
import {css, useTheme} from '@emotion/react'

export default function TextField({id, placeholder, type, multiline, startAdornment, value, onChange, disabled, readOnly, action, ariaLabel, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      background: ${theme.palette.surface.light};
      padding-left: 8px;
    `,

    input: css`
      width: 100%;
      height: 100%;
      color: ${theme.palette.onSurface.dark};
      
      .MuiInputBase-input {
        padding: 0;
      }
    `
  }

  const onValueChange = (e) => {
    onChange(e.target.value)
  }

  return (
    <Grid css={styles.root} container alignItems="center" component={Paper} {...props}>
      <Grid item xs>
        <InputBase
          id={id}
          css={styles.input}
          fullWidth
          disabled={disabled}
          readOnly={readOnly}
          placeholder={placeholder}
          type={type}
          multiline={multiline}
          startAdornment={startAdornment}

          value={value}
          onChange={onValueChange}

          inputProps={{
            'aria-label': ariaLabel,
          }}
        />
      </Grid>
      {action ? (
        <Grid item>
          {action}
        </Grid>
      ) : null}
    </Grid>
  )
}
