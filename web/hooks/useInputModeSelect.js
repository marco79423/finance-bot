import {useTranslation} from 'next-i18next'
import React from 'react'

import Select from '../components/elements/Select'

export const InputMode = Object.freeze({
  TextInput: 'textInput',
  FromFile: 'fromFile',
})

export default function useInputModeSelect() {
  const {t} = useTranslation()

  const [inputMode, onInputModeChange] = React.useState(InputMode.TextInput)
  const inputModes = React.useMemo(() => [
    {
      key: InputMode.TextInput,
      label: t('Text input'),
      value: InputMode.TextInput
    },
    {
      key: InputMode.FromFile,
      label: t('From file'),
      value: InputMode.FromFile
    }
  ], [t])

  const InputModeSelect = React.useCallback((props) => (
    <Select
      selections={inputModes}
      currentValue={inputMode}
      onSelectionChange={onInputModeChange}
      {...props}
    />
  ), [inputMode, inputModes])

  return [InputModeSelect, inputMode]
}
