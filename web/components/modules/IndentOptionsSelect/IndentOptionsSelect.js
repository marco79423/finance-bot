import React from 'react'
import {useTranslation} from 'next-i18next'

import Select from '../../elements/Select'


export default function IndentOptionsSelect({
                                              currentIndentOptions,
                                              onIndentOptionsChange,

                                              supportTab=true,
                                            }) {
  const {t} = useTranslation('base')

  const selectionValue = React.useMemo(() => {
    return transformToSelectionValue(currentIndentOptions)
  }, [currentIndentOptions])

  const selections = React.useMemo(() => {
    const selections = [
      {key: '2-spaces', value: '2-spaces', label: t('Intent with 2 spaces')},
      {key: '3-spaces', value: '3-spaces', label: t('Intent with 3 spaces')},
      {key: '4-spaces', value: '4-spaces', label: t('Intent with 4 spaces')},
      {key: '8-spaces', value: '8-spaces', label: t('Intent with 8 spaces')},
    ]

    if (supportTab) {
      selections.push({key: 'tab', value: 'tab', label: t('Intent with a tab character')})
    }

    return selections
  }, [t, supportTab])

  const onCurrentSelectionChange = (value) => {
    switch (value) {
      case 'tab':
        onIndentOptionsChange({useTabs: true})
        return
      case '2-spaces':
        onIndentOptionsChange({useTabs: false, tabWidth: 2})
        return
      case '3-spaces':
        onIndentOptionsChange({useTabs: false, tabWidth: 3})
        return
      case '4-spaces':
        onIndentOptionsChange({useTabs: false, tabWidth: 4})
        return
      case '8-spaces':
        onIndentOptionsChange({useTabs: false, tabWidth: 8})
        return
    }
  }

  return (
    <Select
      currentValue={selectionValue}
      selections={selections}
      onSelectionChange={onCurrentSelectionChange}
    />
  )
}

function transformToSelectionValue({useTabs, tabWidth} = {useTabs: false, tabWidth: 2}) {
  if (useTabs) {
    return 'tab'
  } else {
    return `${tabWidth}-spaces`
  }
}
