import React from 'react'
import useToggle from './useToggle'

export default function useKeyPressToggle(defaultState, key) {
  const keys = Array.isArray(key) ? key : [key]

  const [value, toggle] = useToggle(defaultState)
  React.useEffect(() => {
    const handleKeyPress = event => {
      if(keys.includes(event.key)) {
        toggle()
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => {
      window.removeEventListener('keydown', handleKeyPress)
    }
  }, [value])

  return value
}
