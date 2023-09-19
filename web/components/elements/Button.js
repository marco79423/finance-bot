import React from 'react'
import PropTypes from 'prop-types'
import {Button as MuiButton} from '@mui/material'
import {css, useTheme} from '@emotion/react'
import {grey} from '@mui/material/colors'


function Button({children, className, disabled, secondary, onClick, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      background: ${secondary ? grey[700] : theme.palette.primary.dark};
      color: ${theme.palette.onPrimary.main};
      text-transform: initial;
    `
  }

  return (
    <MuiButton
      css={styles.root}
      className={className}
      variant="contained"
      disabled={disabled}
      onClick={onClick}
      {...props}
    >
      {children}
    </MuiButton>
  )
}

Button.propTypes = {
  children: PropTypes.node,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  onClick: PropTypes.func.isRequired,
}

export default React.memo(Button)
