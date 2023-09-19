import React from 'react'
import {json} from '@codemirror/lang-json'
import {StreamLanguage} from '@codemirror/language'
import {yaml} from '@codemirror/legacy-modes/mode/yaml'
import {toml} from '@codemirror/legacy-modes/mode/toml'
import {html} from '@codemirror/lang-html'
import {xml} from '@codemirror/lang-xml'
import {sql} from '@codemirror/lang-sql'
import {css} from '@codemirror/lang-css'
import {javascript} from '@codemirror/lang-javascript'
import {python} from '@codemirror/lang-python'


export default function useCodeMirrorExtensions(dataFormat) {
  return React.useMemo(() => {
    switch (dataFormat) {
      case 'json':
        return [
          json()
        ]
      case 'yaml':
        return [
          StreamLanguage.define(yaml)
        ]
      case 'toml':
        return [
          StreamLanguage.define(toml)
        ]
      case 'html':
        return [
          html()
        ]
      case 'xml':
        return [
          xml()
        ]
      case 'sql':
        return [
          sql()
        ]
      case 'css':
        return [
          css()
        ]
      case 'js':
        return [
          javascript({jsx: true})
        ]
      case 'python':
        return [
          python()
        ]
      default:
        return []
    }
  }, [dataFormat])
}