import React from 'react'
import {css} from '@emotion/react'
import CodeMirror from '@uiw/react-codemirror'
import {githubDark, githubLight} from '@uiw/codemirror-theme-github'

import {useDarkMode} from '../../../hooks/darkMode'
import useCodeMirrorExtensions from './useCodeMirrorExtensions'

export default function CodeTextArea({
                                       id,
                                       dataFormat,
                                       placeholder,
                                       value,
                                       onChange,
                                       options,
                                       autoFocus,
                                       ariaLabel,
                                       ...props
                                     }) {
  const [darkMode] = useDarkMode()
  const styles = {
    root: css`
      position: absolute;  // 解決爆版問題 (TODO: 不確定原理)
      height: 100%;
      width: 100%;
      
      border-style: solid;
      border-width: 1px;
      border-color: rgba(0, 0, 0, 0.23);
      border-radius: 4px;

      &:hover {
        border-color: rgba(0, 0, 0, 0.87);
      }
    `
  }

  const extensions = useCodeMirrorExtensions(dataFormat)

  // 方便 e2e 測試抓取內容
  React.useEffect(() => {
    window.state = {
      ...window.state || {},
      [id]: value,
    }
  }, [id, value])

  return (
    <CodeMirror
      id={id}
      css={styles.root}
      placeholder={placeholder}
      value={value}
      theme={darkMode ? githubDark : githubLight}
      height="100%"
      autoFocus={autoFocus}
      basicSetup={{
        lineNumbers: false,
        foldGutter: false,
        ...options,
      }}
      extensions={extensions}
      onChange={onChange}

      aria-label={ariaLabel}

      {...props}
    />
  )
}
