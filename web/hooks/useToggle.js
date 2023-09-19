import React from 'react'

export default function useToggle(initialState = false) {
  const [state, setState] = React.useState(initialState)
  const toggle = React.useCallback(() => {
    setState(state => !state)
  }, [])
  return [state, toggle]
}
