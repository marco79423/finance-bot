import React from 'react'

import Alert from '../../components/elements/Alert'

const context = React.createContext({})

export const Severity = Object.freeze({
  Error: 'error',
  Success: 'success',
})


export const NotificationsProvider = React.memo(({children}) => {
  const [state, setState] = React.useState({
    severity: Severity.Error,
    message: '',
    open: false,
  })

  const showErrorMessage = React.useCallback(message => {
    setState({
      severity: Severity.Error,
      message: message,
      open: true,
    })
  }, [])

  const showSuccessMessage = React.useCallback((message) => {
    setState({
      severity: Severity.Success,
      message: message,
      open: true,
    })
  }, [])

  const hideMessage = React.useCallback(() => {
    setState({
      ...state,
      open: false,
    })
  }, [])

  const notifications = React.useMemo(() => {
    return {
      showSuccessMessage,
      showErrorMessage,
      hideMessage,
    }
  }, [showSuccessMessage, showErrorMessage, hideMessage])

  return (
    <>
      <context.Provider value={notifications}>
        {children}
      </context.Provider>

      <Alert
        open={state.open}
        severity={state.severity}
        message={state.message}
        onClose={hideMessage}
      />
    </>
  )
})

export function useNotifications() {
  return React.useContext(context)
}
