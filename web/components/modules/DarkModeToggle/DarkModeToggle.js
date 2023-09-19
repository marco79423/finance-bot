import React from 'react'
import {DarkModeSwitch} from 'react-toggle-dark-mode'

import {useDarkMode} from '../../../hooks/darkMode'


function DarkModeToggle(props) {
  const [darkMode, setDarkMode] = useDarkMode()

  return (
    <DarkModeSwitch
      checked={darkMode}
      onChange={setDarkMode}
      sunColor="yellow"
      size={30}
      {...props}
    />
  )
}

export default React.memo(DarkModeToggle)
